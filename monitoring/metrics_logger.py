import csv
import time
from pathlib import Path

class MetricsLogger:
    def __init__(self, log_dir="monitoring/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True, parents=True)
        self.csv_file = self.log_dir / "metrics.csv"
        
        if not self.csv_file.exists():
            with open(self.csv_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "source", "inference_time_ms", "num_detections", "max_confidence"])
                
    def log(self, source, inference_time_ms, detections):
        max_conf = max([d["confidence"] for d in detections]) if detections else 0.0
        with open(self.csv_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([time.time(), source, inference_time_ms, len(detections), max_conf])
