import os
import yaml

ROOT = os.path.dirname(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(ROOT, "..", "config.yaml")


def get_config():
    # Load config.yaml from repo root; fall back to packaged config if needed
    path = os.getenv("CONFIG_PATH", os.path.join(os.getcwd(), "config.yaml"))
    try:
        with open(path, "r") as f:
            cfg = yaml.safe_load(f)
    except FileNotFoundError:
        # minimal default
        cfg = {}

    # Environment overrides (example)
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        cfg.setdefault("database", {})["url"] = db_url

    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        cfg.setdefault("cache", {})["redis_url"] = redis_url

    return cfg
