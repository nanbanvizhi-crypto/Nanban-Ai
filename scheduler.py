"""
🔔 Automation jobs — Nanban runs things by itself on a schedule.

Schedules:
  • Daily        — every day at HH:MM
  • Every N hours — repeat on an interval (e.g. every 4 hours)
  • Weekly       — chosen weekdays at HH:MM
  • Once         — a single run at a date + time

Job kinds:
  • Prompt  — run one LLM prompt
  • Chain   — run several prompts in order (each step sees the previous output)
  • Action  — a safe built-in: self-check (doctor), backup, or a daily India Lab exercise

Each run's output is saved to data/scheduled/ and (if set up) pushed to Telegram / WhatsApp.
A background thread checks once a minute. Jobs live in data/schedules.json.
"""

import json
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path

import config

SCHED_FILE = config.DATA_DIR / "schedules.json"
OUT_DIR = config.DATA_DIR / "scheduled"
_thread = None
_stop = False
_lock = threading.Lock()

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
ACTIONS = {
    "self_check": "🩺 Self-check (doctor)",
    "backup": "💾 Backup now",
    "lab_exercise": "🎯 India Lab daily exercise",
}


# ---------------------------------------------------------------- storage
def load() -> list[dict]:
    try:
        items = json.loads(SCHED_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []
    return [_migrate(t) for t in items]


def save(items: list[dict]) -> None:
    with _lock:
        SCHED_FILE.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")


def _migrate(t: dict) -> dict:
    """Old tasks had flat time/prompt — wrap them into the new shape."""
    if "sched" not in t:
        t = {
            "id": t.get("id", int(time.time())),
            "name": t.get("prompt", "Task")[:40],
            "enabled": True,
            "sched": {"type": "daily", "time": t.get("time", "08:00"),
                      "every_min": 240, "days": [], "date": ""},
            "kind": "prompt",
            "mode": t.get("mode", "assistant"),
            "prompt": t.get("prompt", ""),
            "steps": [],
            "action": "",
            "notify": {"telegram": True, "whatsapp": False},
            "last_run": t.get("last_run", ""),
            "last_status": "",
        }
    t.setdefault("enabled", True)
    t.setdefault("notify", {"telegram": True, "whatsapp": False})
    t.setdefault("last_status", "")
    return t


# ---------------------------------------------------------------- create / edit
def add(name: str, sched_type: str, time_hhmm: str = "", every_hours: float = 4,
        days: list | None = None, date: str = "", kind: str = "prompt",
        prompt: str = "", action: str = "", mode: str = "assistant",
        notify_tg: bool = True, notify_wa: bool = False) -> str:
    sched_type = (sched_type or "daily").lower()
    name = (name or "").strip() or (prompt.strip()[:40] if prompt else action or "Job")

    # validate schedule
    sched = {"type": sched_type, "time": "", "every_min": 240, "days": [], "date": ""}
    if sched_type in ("daily", "weekly", "once"):
        time_hhmm = (time_hhmm or "").strip()
        try:
            datetime.strptime(time_hhmm, "%H:%M")
        except ValueError:
            return "⚠️ Time should be HH:MM (24-hour), e.g. 08:30."
        sched["time"] = time_hhmm
    if sched_type == "interval":
        try:
            m = int(float(every_hours) * 60)
            if m < 5:
                return "⚠️ Interval must be at least 5 minutes."
            sched["every_min"] = m
        except Exception:
            return "⚠️ Enter the interval in hours, e.g. 4."
    if sched_type == "weekly":
        idxs = [WEEKDAYS.index(d) for d in (days or []) if d in WEEKDAYS]
        if not idxs:
            return "⚠️ Pick at least one weekday."
        sched["days"] = idxs
    if sched_type == "once":
        date = (date or "").strip()
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return "⚠️ Date should be YYYY-MM-DD, e.g. 2026-11-10."
        sched["date"] = date

    # validate job
    kind = (kind or "prompt").lower()
    steps = []
    if kind == "prompt":
        if not prompt.strip():
            return "⚠️ Type the prompt Nanban should run."
    elif kind == "chain":
        steps = [s.strip() for s in (prompt or "").splitlines() if s.strip()]
        if len(steps) < 2:
            return "⚠️ Chain needs 2+ steps — put one prompt per line."
    elif kind == "action":
        if action not in ACTIONS:
            return "⚠️ Pick a valid action."

    items = load()
    new_id = max((t.get("id", 0) for t in items), default=99) + 1
    items.append({
        "id": new_id, "name": name, "enabled": True,
        "sched": sched, "kind": kind, "mode": mode, "prompt": prompt.strip(),
        "steps": steps, "action": action,
        "notify": {"telegram": bool(notify_tg), "whatsapp": bool(notify_wa)},
        "last_run": "", "last_status": "",
    })
    save(items)
    return f"✅ Added automation **{name}** ({_sched_label(sched)})."


def remove(task_id: int) -> str:
    save([t for t in load() if t.get("id") != task_id])
    return "🗑️ Removed."


def toggle(task_id: int) -> str:
    items = load()
    for t in items:
        if t.get("id") == task_id:
            t["enabled"] = not t.get("enabled", True)
            save(items)
            return f"{'▶️ Enabled' if t['enabled'] else '⏸️ Paused'} **{t['name']}**."
    return "Not found."


def run_now(task_id: int) -> str:
    for t in load():
        if t.get("id") == task_id:
            threading.Thread(target=_run_task, args=(t, True), daemon=True).start()
            return f"🚀 Running **{t['name']}** now… output saves to data/scheduled/ (+ notify if set)."
    return "Not found."


# ---------------------------------------------------------------- display
def _sched_label(s: dict) -> str:
    t = s.get("type")
    if t == "daily":
        return f"daily {s.get('time')}"
    if t == "interval":
        m = s.get("every_min", 240)
        return f"every {m//60}h{m%60:02d}m" if m % 60 else f"every {m//60}h"
    if t == "weekly":
        ds = ", ".join(WEEKDAYS[i] for i in s.get("days", []))
        return f"{ds} {s.get('time')}"
    if t == "once":
        return f"once {s.get('date')} {s.get('time')}"
    return t or "?"


def list_text() -> str:
    items = load()
    if not items:
        return "_No automation jobs yet. Add one below._"
    lines = []
    for t in items:
        on = "🟢" if t.get("enabled", True) else "⏸️"
        kind = t.get("kind", "prompt")
        what = (ACTIONS.get(t.get("action", ""), t.get("action", "")) if kind == "action"
                else (f"{len(t.get('steps', []))}-step chain" if kind == "chain"
                      else t.get("prompt", "")[:60]))
        last = f" · last: {t.get('last_status') or t.get('last_run') or '—'}"
        lines.append(f"- {on} **{t['name']}** · {_sched_label(t['sched'])} · {kind}: {what}{last} `id:{t['id']}`")
    return "\n".join(lines)


# ---------------------------------------------------------------- execution
def _agent_run(prompt: str, mode: str, context: str = "") -> str:
    from agent_core import Agent
    agent = Agent(mode or "assistant")
    full = (f"[Previous step output]\n{context}\n\n{prompt}" if context else prompt)
    text = ""
    for ev in agent.stream(full):
        if getattr(ev, "kind", "") == "text":
            text += ev.data
    return text.strip()


def _do_action(action: str) -> str:
    if action == "self_check":
        import doctor
        try:
            doctor.run_all()
        except Exception:
            pass
        return "🩺 Self-check:\n" + doctor.quick_summary()
    if action == "backup":
        import backup
        try:
            p = backup.make_backup() if hasattr(backup, "make_backup") else backup.create()
            return f"💾 Backup created: {p}"
        except Exception as e:
            return f"💾 Backup failed: {e}"
    if action == "lab_exercise":
        import random
        import india_lab as il
        d = random.choice(il.DOMAINS)
        prompt = (f"India Lab daily exercise on '{d['name']}'. Oru chinna hands-on lab task "
                  f"(un sontha lab / legal target mattum) + oru defense tip kudu. Tanglish la, short-ah. "
                  f"Context: {d['what_ta']}")
        return f"🎯 Today's India Lab exercise — {d['name']}\n\n" + _agent_run(prompt, "assistant")
    return "Unknown action."


def _run_task(task: dict, manual: bool = False) -> None:
    try:
        kind = task.get("kind", "prompt")
        if kind == "action":
            text = _do_action(task.get("action", ""))
            title = ACTIONS.get(task.get("action", ""), task.get("action", ""))
        elif kind == "chain":
            ctx, parts = "", []
            for i, step in enumerate(task.get("steps", []), 1):
                out = _agent_run(step, task.get("mode", "assistant"), ctx)
                parts.append(f"### Step {i}: {step}\n{out}")
                ctx = out
            text = "\n\n".join(parts)
            title = task.get("name", "Chain")
        else:
            text = _agent_run(task.get("prompt", ""), task.get("mode", "assistant"))
            title = task.get("prompt", task.get("name", ""))

        OUT_DIR.mkdir(exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        safe = "".join(c if c.isalnum() else "_" for c in task.get("name", "job"))[:30]
        (OUT_DIR / f"{stamp}_{safe}.md").write_text(
            f"# {title}\n_{datetime.now():%Y-%m-%d %H:%M}_\n\n{text}", encoding="utf-8")

        msg = f"⏰ {task.get('name','Automation')}\n\n{text}"
        notify = task.get("notify", {})
        if notify.get("telegram"):
            try:
                import telegram_bot
                telegram_bot.push(msg)
            except Exception:
                pass
        if notify.get("whatsapp"):
            try:
                import whatsapp
                if whatsapp.configured() and getattr(config, "WHATSAPP_TO", ""):
                    whatsapp.send(config.WHATSAPP_TO, msg[:3500])
            except Exception:
                pass
        _mark(task["id"], "✅ " + datetime.now().strftime("%m-%d %H:%M"))
    except Exception as e:
        _mark(task.get("id"), f"⚠️ {e}")


def _mark(task_id, status: str) -> None:
    items = load()
    for t in items:
        if t.get("id") == task_id:
            t["last_run"] = datetime.now().isoformat(timespec="minutes")
            t["last_status"] = status
    save(items)


def _due(task: dict, now: datetime) -> bool:
    if not task.get("enabled", True):
        return False
    s = task.get("sched", {})
    typ = s.get("type")
    hhmm = now.strftime("%H:%M")
    today = now.strftime("%Y-%m-%d")
    last = task.get("last_run", "")
    if typ == "daily":
        return s.get("time") == hhmm and not last.startswith(today)
    if typ == "weekly":
        return (now.weekday() in s.get("days", []) and s.get("time") == hhmm
                and not last.startswith(today))
    if typ == "once":
        if last:
            return False
        try:
            target = datetime.strptime(f"{s.get('date')} {s.get('time')}", "%Y-%m-%d %H:%M")
            return now >= target
        except Exception:
            return False
    if typ == "interval":
        if not last:
            return True
        try:
            prev = datetime.fromisoformat(last)
            return now - prev >= timedelta(minutes=s.get("every_min", 240))
        except Exception:
            return True
    return False


def _loop() -> None:
    while not _stop:
        now = datetime.now()
        for task in load():
            if _due(task, now):
                _mark(task["id"], "running…")
                threading.Thread(target=_run_task, args=(task,), daemon=True).start()
        time.sleep(30)


def start() -> None:
    global _thread
    if _thread and _thread.is_alive():
        return
    _thread = threading.Thread(target=_loop, daemon=True)
    _thread.start()
