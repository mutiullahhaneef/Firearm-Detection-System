import json
import time
import threading
from pathlib import Path

class IncidentLogger:
    def __init__(self, config):
        self.enabled = config.get("enabled", True)
        self.log_dir = Path(config.get("log_dir", "incidents"))
        self._lock = threading.Lock()
        if self.enabled:
            self.log_dir.mkdir(exist_ok=True, parents=True)
            (self.log_dir / "screenshots").mkdir(exist_ok=True)
            self.log_file = self.log_dir / "incident_log.json"
            if not self.log_file.exists():
                with open(self.log_file, "w") as f:
                    json.dump([], f)

    def log_incident(self, source, max_conf):
        if not self.enabled:
            return

        incident = {
            "timestamp": time.time(),
            "time_str": time.ctime(),
            "source": source,
            "max_confidence": round(max_conf, 4)
        }

        with self._lock:
            try:
                with open(self.log_file, "r") as f:
                    logs = json.load(f)
                if not isinstance(logs, list):
                    logs = []
            except (json.JSONDecodeError, IOError):
                logs = []

            logs.append(incident)
            with open(self.log_file, "w") as f:
                json.dump(logs, f, indent=2)
