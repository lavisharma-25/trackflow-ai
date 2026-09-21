"""Small local smoke test. The real automated tests live in tests/."""

from src.db.database import init_db


def run_smoke_test() -> None:
    init_db()
    print("TrackFlow database initialized successfully.")


if __name__ == "__main__":
    run_smoke_test()
