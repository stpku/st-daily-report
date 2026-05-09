import os


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(ROOT_DIR, "config")
RUNTIME_DIR = os.path.join(ROOT_DIR, "runtime")
RUNTIME_STATE_DIR = os.path.join(RUNTIME_DIR, "state")
RUNTIME_LOG_DIR = os.path.join(RUNTIME_DIR, "logs")
RUNTIME_EXPORT_DIR = os.path.join(RUNTIME_DIR, "exports")


def ensure_runtime_dirs():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(RUNTIME_STATE_DIR, exist_ok=True)
    os.makedirs(RUNTIME_LOG_DIR, exist_ok=True)
    os.makedirs(RUNTIME_EXPORT_DIR, exist_ok=True)


def config_path(filename: str) -> str:
    ensure_runtime_dirs()
    return os.path.join(CONFIG_DIR, filename)


def runtime_state_path(filename: str) -> str:
    ensure_runtime_dirs()
    return os.path.join(RUNTIME_STATE_DIR, filename)


def resolve_path(preferred: str, legacy: str | None = None) -> str:
    ensure_runtime_dirs()
    candidates = [preferred]
    if legacy:
        candidates.append(legacy)

    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return preferred
