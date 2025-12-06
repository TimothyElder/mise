import platform
import logging
from pathlib import Path

# ---------- logging config ----------
def setup_logging(log_dir: Path = None, level=logging.INFO):
    """Configure application-wide logging"""
    if log_dir is None:
        # Platform-specific default locations
        if platform.system() == "Darwin":  # macOS
            log_dir = Path.home() / "Library" / "Logs" / "Mise"
        elif platform.system() == "Windows":
            log_dir = Path.home() / "AppData" / "Local" / "Mise" / "Logs"
        else:  # Linux and others
            log_dir = Path.home() / ".mise" / "logs"
    
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "mise.logger"
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logging.info(f"Logging initialized at {log_file}")