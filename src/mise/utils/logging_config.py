import logging
from pathlib import Path

def setup_logging(log_dir: Path | None = None, level: int = logging.INFO) -> None:
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    handlers = []

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    handlers.append(console_handler)

    if log_dir is not None:
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "mise.log", encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(file_handler)

    logging.basicConfig(level=level, handlers=handlers)