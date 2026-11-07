"""
Remote servers for Nanban: a registry of machines you can reach over SSH
(VPS, Raspberry Pi, office PCs, cloud VMs), plus the SSH/SFTP engine used by the
terminal, the AI tools, the web app and the API.

Registry file: data/servers.json
  { "office": {"host": "192.168.1.20", "port": 22, "user": "dev", "key": "C:/Users/me/.ssh/id_ed25519",
               "password": "", "tags": ["linux"], "notes": "Ubuntu box in the office"} }

Passwords are only saved if you choose `--save-password`; otherwise Nanban asks once per session.
"""

import json
import posixpath
import socket
import stat
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

import config

REGISTRY_FILE = config.DATA_DIR / "servers.json"
DEFAULT_TIMEOUT = 120
_lock = threading.Lock()
_connections: dict[str, "RemoteHost"] = {}
_session_passwords: dict[str, str] = {}


# ---------------------------------------------------------------- registry

def load() -> dict:
    try:
        return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save(registry: dict) -> None:
    REGISTRY_FILE.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")


def names() -> list[str]:
    return sorted(load())


def get(name: str) -> dict | None:
    entry = load().get(name)
    return dict(entry, name=name) if entry else None


def parse_target(target: str) -> tuple[str, str, int]:
    """'user@host:port' -> (user, host, port). user defaults to 'root', port to 22."""
    user, _, rest = target.rpartition("@")
    host, _, port = rest.partition(":")
    return user or "root", host, int(port) if port.isdigit() else 22


def add(name: str, target: str, key: str = "", password: str = "", save_password: bool = False,
        notes: str = "") -> str:
    if not name.replace("-", "").replace("_", "").isalnum():
        return "Server name: letters, numbers, - and _ only."
    user, host, port = parse_target(target)
    if not host:
        return "Give the address as user@host or user@host:port"
    registry = load()
    registry[name] = {
        "host": host, "port": port, "user": user, "key": key,
        "password": password if save_password else "", "notes": notes,
        "added": time.strftime("%Y-%m-%d"),
    }
    save(registry)
    if password and not save_password:
        _session_passwords[name] = password
    disconnect(name)
    return f"Added server '{name}' = {user}@{host}:{port}" + (" (key auth)" if key else "")


def remove(name: str) -> str:
    registry = load()
    if name not in registry:
        return f"No server called '{name}'."
    del registry[name]
    save(registry)
    disconnect(name)
    return f"Removed '{name}'."


# ---------------------------------------------------------------- SSH engine

@dataclass
class RunResult:
    code: int
    output: str
    seconds: float = 0.0


@dataclass
class RemoteHost:
    """One SSH connection, reused for many commands. Created through connect()."""
    name: str
    host: str
    port: int
    user: str
    key: str = ""
    password: str = ""
    cwd: str = "~"
    client: object = None
    _sftp: object = None
    home: str = ""
    os_name: str = ""
    lock: threading.Lock = field(default_factory=threading.Lock)

    # ---- connection

    def open(self) -> None:
        import paramiko
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        kwargs = dict(hostname=self.host, port=self.port, username=self.user, timeout=15,
                      banner_timeout=20, auth_timeout=20, allow_agent=True, look_for_keys=not self.password)
        if self.key:
            kwargs["key_filename"] = str(Path(self.key).expanduser())
        if self.password:
            kwargs["password"] = self.password
        client.connect(**kwargs)
        transport = client.get_transport()
        if transport:
            transport.set_keepalive(30)
        self.client = client
        self.home = self._exec("echo $HOME").output.strip() or "~"
        if self.cwd == "~":
            self.cwd = self.home
        probe = self._exec(". /etc/os-release 2>/dev/null && echo $PRETTY_NAME || uname -s").output.strip()
        self.os_name = probe.splitlines()[0] if probe else "Linux"

    def close(self) -> None:
        for obj in (self._sftp, self.client):
            try:
                if obj:
                    obj.close()
            except Exception:
                pass
        self._sftp = self.client = None

    def alive(self) -> bool:
        try:
            transport = self.client.get_transport() if self.client else None
            return bool(transport and transport.is_active())
        except Exception:
            return False

    # ---- commands

    def _exec(self, command: str, timeout: int = DEFAULT_TIMEOUT, on_line=None) -> RunResult:
        started = time.monotonic()
        with self.lock:
            stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout, get_pty=False)
            stdin.close()
            channel = stdout.channel
            channel.set_combine_stderr(True)
            lines, buffer = [], b""
            deadline = started + timeout
            while True:
                if channel.recv_ready():
                    buffer += channel.recv(65536)
                    *done, buffer = buffer.split(b"\n")
                    for raw in done:
                        line = raw.decode("utf-8", errors="replace").rstrip("\r")
                        lines.append(line)
                        if on_line:
                            on_line(line)
                elif channel.exit_status_ready():
                    while channel.recv_ready():
                        buffer += channel.recv(65536)
                    break
                elif time.monotonic() > deadline:
                    channel.close()
                    lines.append(f"[stopped: took longer than {timeout}s]")
                    return RunResult(124, "\n".join(lines), time.monotonic() - started)
                else:
                    time.sleep(0.03)
            if buffer:
                for raw in buffer.split(b"\n"):
                    line = raw.decode("utf-8", errors="replace").rstrip("\r")
                    if line:
                        lines.append(line)
                        if on_line:
                            on_line(line)
            code = channel.recv_exit_status()
        return RunResult(code, "\n".join(lines), time.monotonic() - started)

    def run(self, command: str, timeout: int = DEFAULT_TIMEOUT, on_line=None) -> RunResult:
        """Run a command in the remote working directory (non-interactive, login shell)."""
        quoted_cwd = self.cwd.replace("'", "'\\''")
        wrapped = f"cd '{quoted_cwd}' 2>/dev/null; {command}"
        return self._exec(f"bash -lc {_shell_quote(wrapped)}", timeout, on_line)

    def change_dir(self, target: str) -> str:
        target = target.strip() or "~"
        if target == "~" or target.startswith("~/"):
            target = self.home + target[1:]
        result = self.run(f"cd -- {_shell_quote(target)} && pwd")
        if result.code != 0:
            return result.output.strip() or f"cd: {target}: No such directory"
        self.cwd = result.output.strip().splitlines()[-1]
        return ""

    def display_cwd(self) -> str:
        if self.home and (self.cwd == self.home or self.cwd.startswith(self.home + "/")):
            return "~" + self.cwd[len(self.home):]
        return self.cwd

    def resolve(self, path: str) -> str:
        path = (path or ".").strip()
        if path.startswith("~"):
            path = self.home + path[1:]
        return path if path.startswith("/") else posixpath.normpath(posixpath.join(self.cwd, path))

    # ---- files (SFTP)

    @property
    def sftp(self):
        if self._sftp is None:
            self._sftp = self.client.open_sftp()
        return self._sftp

    def read_text(self, path: str) -> str:
        with self.sftp.open(self.resolve(path), "rb") as handle:
            return handle.read().decode("utf-8", errors="replace")

    def write_text(self, path: str, content: str) -> None:
        full = self.resolve(path)
        self.run(f"mkdir -p {_shell_quote(posixpath.dirname(full))}")
        with self.sftp.open(full, "wb") as handle:
            handle.write(content.encode("utf-8"))

    def exists(self, path: str) -> bool:
        try:
            self.sftp.stat(self.resolve(path))
            return True
        except IOError:
            return False

    def upload(self, local: Path, remote: str) -> str:
        full = self.resolve(remote)
        try:
            if stat.S_ISDIR(self.sftp.stat(full).st_mode):
                full = posixpath.join(full, local.name)
        except IOError:
            pass
        self.sftp.put(str(local), full)
        return full

    def download(self, remote: str, local: Path) -> Path:
        full = self.resolve(remote)
        if local.is_dir():
            local = local / posixpath.basename(full)
        self.sftp.get(full, str(local))
        return local

    # ---- health

    def status(self) -> dict:
        script = (
            "echo HOST=$(hostname); echo UP=$(uptime -p 2>/dev/null || uptime); "
            "echo LOAD=$(cut -d' ' -f1-3 /proc/loadavg 2>/dev/null); "
            "echo MEM=$(free -m 2>/dev/null | awk '/Mem:/{printf \"%d/%dMB\", $3, $2}'); "
            "echo DISK=$(df -h / 2>/dev/null | awk 'NR==2{print $3\"/\"$2\" (\"$5\")\"}'); "
            "echo CPU=$(nproc 2>/dev/null); "
            "echo TOP=$(ps -eo comm,%cpu --sort=-%cpu 2>/dev/null | awk 'NR>1 && NR<5{printf \"%s %s%% \", $1, $2}')"
        )
        result = self._exec(script, timeout=20)
        info = {"name": self.name, "ok": result.code == 0, "os": self.os_name}
        for line in result.output.splitlines():
            key, _, value = line.partition("=")
            info[key.lower()] = value.strip()
        return info


def _shell_quote(text: str) -> str:
    return "'" + text.replace("'", "'\\''") + "'"


# ---------------------------------------------------------------- connection pool

def connect(name: str, ask_password=None) -> RemoteHost:
    """Get a live connection to a registered server (reconnecting if needed).
    `ask_password(name)` is called when no key/password is known."""
    entry = get(name)
    if not entry:
        raise ValueError(f"No server called '{name}'. Add one with: /server add {name} user@host")
    with _lock:
        host = _connections.get(name)
        if host and host.alive():
            return host
        password = entry.get("password") or _session_passwords.get(name, "")
        if not password and not entry.get("key") and ask_password:
            password = ask_password(name) or ""
            if password:
                _session_passwords[name] = password
        host = RemoteHost(name=name, host=entry["host"], port=entry["port"], user=entry["user"],
                          key=entry.get("key", ""), password=password)
        try:
            host.open()
        except socket.timeout:
            raise ConnectionError(f"'{name}' ({entry['host']}:{entry['port']}) did not answer. Is it on, and is SSH running?")
        except Exception as e:
            kind = type(e).__name__
            if "Authentication" in kind or "auth" in str(e).lower():
                raise ConnectionError(f"'{name}': login failed for user {entry['user']}. Check the key or password.")
            raise ConnectionError(f"'{name}': {e}")
        _connections[name] = host
        return host


def disconnect(name: str) -> None:
    with _lock:
        host = _connections.pop(name, None)
    if host:
        host.close()


def disconnect_all() -> None:
    for name in list(_connections):
        disconnect(name)


def status_all(ask_password=None) -> list[dict]:
    """Health of every registered server, collected in parallel."""
    results: dict[str, dict] = {}

    def probe(name):
        try:
            results[name] = connect(name, ask_password).status()
        except Exception as e:
            results[name] = {"name": name, "ok": False, "error": str(e)}

    threads = [threading.Thread(target=probe, args=(n,), daemon=True) for n in names()]
    for t in threads:
        t.start()
    for t in threads:
        t.join(45)
    return [results.get(n, {"name": n, "ok": False, "error": "timed out"}) for n in names()]
