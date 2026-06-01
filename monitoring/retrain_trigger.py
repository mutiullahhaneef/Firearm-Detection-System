import shutil
from pathlib import Path

class RetrainTrigger:
    def __init__(self, queue_dir="monitoring/review_queue", min_conf=0.30, max_conf=0.55):
        self.queue_dir = Path(queue_dir)
        self.queue_dir.mkdir(exist_ok=True, parents=True)
        self.min_conf = min_conf
        self.max_conf = max_conf
        
    def check_and_queue(self, source_path, detections):
        if not detections: return
        
        max_conf = max([d["confidence"] for d in detections])
        if self.min_conf <= max_conf <= self.max_conf:
            source_path = Path(source_path)
            dest = self.queue_dir / source_path.name
            if source_path.exists() and not dest.exists():
                shutil.copy2(source_path, dest)
                print(f"[Monitoring] Flagged {source_path.name} for human review (conf: {max_conf:.2f})")
