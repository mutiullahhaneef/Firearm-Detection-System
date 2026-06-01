import time
from pathlib import Path
from inference.run_image import load_config, run_inference, YOLO
from alerts.alert_manager import AlertManager
import json

class DetectionService:
    def __init__(self):
        self.start_time = time.time()
        self.inf_config = load_config("configs/inference_config.yaml")
        self.alert_manager = AlertManager("configs/alert_config.yaml")
        # Load model ONCE at startup instead of every request
        self.model = YOLO(self.inf_config["model_path"])

    def process_image(self, file_path: Path, override_conf: float = None):
        # Pass pre-loaded model to avoid reloading on every request
        run_inference(file_path, self.inf_config, override_conf=override_conf, model=self.model)

        json_path = Path(self.inf_config["output_dir"]) / f"{file_path.stem}_result.json"

        result = {"filename": file_path.name, "detections": [], "inference_time_ms": 0}
        if json_path.exists():
            try:
                with open(json_path, "r") as f:
                    result = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        # Trigger alerts
        self.alert_manager.process_detections(file_path.name, result.get("detections", []))

        # Return path to annotated image
        annotated_path = Path(self.inf_config["output_dir"]) / f"{file_path.stem}_annotated{file_path.suffix}"
        if annotated_path.exists():
            result["annotated_image"] = f"/outputs/{annotated_path.name}"

        return result
