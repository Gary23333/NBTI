#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "$0")"
if ((BASH_VERSINFO[0] < 4 || (BASH_VERSINFO[0] == 4 && BASH_VERSINFO[1] < 3))); then
  echo "start.sh requires Bash 4.3 or newer (for wait -n)." >&2
  exit 1
fi

# Production traffic may pass through a local reverse proxy. Never rely on
# localhost-only admin access in this mode.
if [[ -z "${NBTI_ADMIN_TOKEN:-}" ]]; then
  echo "Set NBTI_ADMIN_TOKEN before starting the production servers." >&2
  exit 1
fi

pids=()
cleanup() {
  trap - EXIT INT TERM
  if ((${#pids[@]})); then
    kill -TERM "${pids[@]}" 2>/dev/null || true
    wait "${pids[@]}" 2>/dev/null || true
  fi
}
trap cleanup EXIT
trap 'exit 143' TERM
trap 'exit 130' INT

gunicorn -c gunicorn.conf.py server:app &
pids+=("$!")
gunicorn --bind 0.0.0.0:8080 --workers 1 --worker-class gthread \
  --threads 8 --timeout 120 --access-logfile - --error-logfile - frontend_server:app &
pids+=("$!")

# Preserve the failed child's exit code and terminate/reap the other server.
status=0
wait -n "${pids[@]}" || status=$?
exit "$status"

