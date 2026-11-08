#!/bin/bash
# Nanban — install the full Kali arsenal (official metapackages) inside the Kali WSL distro.
# Runs detached as root; progress in /var/log/nanban-arsenal.log. Safe to re-run (apt is idempotent).
export DEBIAN_FRONTEND=noninteractive
LOG=/var/log/nanban-arsenal.log
OPTS="-y -q -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold"
PKGS="kali-linux-large seclists nuclei bloodhound netexec"
USER_NAME="${1:-nanbanlinux}"

echo "=== START $(date)"
# wait for any other apt/dpkg to finish, then repair half-done installs
for _ in $(seq 1 120); do fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1 || break; sleep 5; done
dpkg --configure -a
apt-get update -q
apt-get install $OPTS $PKGS
rc=$?
echo "=== APT EXIT: $rc $(date)"
if [ $rc -ne 0 ]; then
  echo "=== retrying once (fix-missing)"
  apt-get install $OPTS --fix-missing $PKGS
  echo "=== APT RETRY EXIT: $? $(date)"
fi
su - "$USER_NAME" -c "nuclei -update-templates" 2>&1 | tail -2
apt-get clean
echo "=== DONE $(date)"
