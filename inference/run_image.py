import cv2
import json
import time
import yaml
from pathlib import Path
from ultralytics import YOLO

# Per-class bounding box colors (BGR)
CLASS_COLORS = {
    "pistol":       (0,   230,  118),
    "rifle":        (0,   140,  255),
    "shotgun":      (0,   23,   255),
    "sniper_rifle": (255, 145,   0),
    "machine_gun":  (180,  0,   180),
    "revolver":     (0,   229,  255),
}
DEFAULT_COLOR = (200, 200, 200)


def load_config(config_path="configs/inference_config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def draw_annotated_boxes(image, detections, class_names):
    """Draw clean bounding boxes with labels on the image."""
    annotated = image.copy()
    h, w, _ = annotated.shape

    # Top status bar
    bar_overlay = annotated.copy()
    cv2.rectangle(bar_overlay, (0, 0), (w, 50), (30, 30, 30), -1)
    cv2.addWeighted(bar_overlay, 0.7, annotated, 0.3, 0, annotated)

    if detections:
        status_text = "FIREARM DETECTED"
        status_color = (60, 60, 255)
    else:
        status_text = "NO THREATS FOUND"
        status_color = (100, 220, 100)

    cv2.putText(annotated, "Firearm Detection System", (15, 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1, cv2.LINE_AA)
    cv2.putText(annotated, status_text, (15, 42),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, status_color, 1, cv2.LINE_AA)

    # Draw each detection
    for d in detections:
        x1, y1, x2, y2 = map(int, d["bbox"])
        conf = d["confidence"]
        cls_name = d["class"]
        color = CLASS_COLORS.get(cls_name.lower(), DEFAULT_COLOR)

        # Semi-transparent fill
        box_overlay = annotated.copy()
        cv2.rectangle(box_overlay, (x1, y1), (x2, y2), color, -1)
        cv2.addWeighted(box_overlay, 0.08, annotated, 0.92, 0, annotated)

        # Border
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2, cv2.LINE_AA)

        # Corner brackets
        corner_len = min(18, int((x2 - x1) * 0.2), int((y2 - y1) * 0.2))
        ct = 3
        cv2.line(annotated, (x1, y1), (x1 + corner_len, y1), color, ct, cv2.LINE_AA)
        cv2.line(annotated, (x1, y1), (x1, y1 + corner_len), color, ct, cv2.LINE_AA)
        cv2.line(annotated, (x2, y1), (x2 - corner_len, y1), color, ct, cv2.LINE_AA)
        cv2.line(annotated, (x2, y1), (x2, y1 + corner_len), color, ct, cv2.LINE_AA)
        cv2.line(annotated, (x1, y2), (x1 + corner_len, y2), color, ct, cv2.LINE_AA)
        cv2.line(annotated, (x1, y2), (x1, y2 - corner_len), color, ct, cv2.LINE_AA)
        cv2.line(annotated, (x2, y2), (x2 - corner_len, y2), color, ct, cv2.LINE_AA)
        cv2.line(annotated, (x2, y2), (x2, y2 - corner_len), color, ct, cv2.LINE_AA)

        # Label
        label = f"{cls_name.upper()} {conf:.0%}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.45
        (tw, th), _ = cv2.getTextSize(label, font, font_scale, 1)

        label_y = y1 - th - 10 if y1 - th - 10 > 55 else y1 + 5
        label_bottom = y1 if y1 - th - 10 > 55 else y1 + th + 15
        text_y = y1 - 6 if y1 - th - 10 > 55 else y1 + th + 10

        cv2.rectangle(annotated, (x1, label_y), (x1 + tw + 10, label_bottom), color, -1)
        cv2.putText(annotated, label, (x1 + 5, text_y), font, font_scale, (0, 0, 0), 1, cv2.LINE_AA)

    return annotated


def run_inference(source_path, config=None, override_conf=None, model=None):
    if config is None:
        config = load_config()

    # Use provided model or load a new one
    if model is None:
        model = YOLO(config["model_path"])

    source_path = Path(source_path)
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(exist_ok=True, parents=True)

    valid_exts = set(config["supported_formats"])

    images = []
    if source_path.is_file() and source_path.suffix.lower() in valid_exts:
        images.append(source_path)
    elif source_path.is_dir():
        images = [f for f in source_path.iterdir() if f.is_file() and f.suffix.lower() in valid_exts]

    if not images:
        print(f"No valid images found in {source_path}")
        return

    for img_path in images:
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"Failed to load {img_path}")
            continue

        start = time.perf_counter()
        conf_val = override_conf if override_conf is not None else config["confidence_threshold"]

        results = model.predict(
            source=img,
            conf=conf_val,
            iou=config["nms_iou_threshold"],
            verbose=False
        )
        elapsed_ms = (time.perf_counter() - start) * 1000

        detections = []
        for box in results[0].boxes:
            x1, y1, x2, y2 = map(float, box.xyxy[0])
            conf = float(box.conf[0])
            cls_name = model.names[int(box.cls[0])]

            detections.append({
                "bbox": [x1, y1, x2, y2],
                "confidence": conf,
                "class": cls_name
            })

        # Draw annotated image
        annotated = draw_annotated_boxes(img, detections, model.names)

        result_json = {
            "filename": img_path.name,
            "inference_time_ms": elapsed_ms,
            "detections": detections
        }

        base_name = img_path.stem
        if config["save_json"]:
            with open(output_dir / f"{base_name}_result.json", "w") as f:
                json.dump(result_json, f, indent=2)

        if config["save_annotated"]:
            cv2.imwrite(str(output_dir / f"{base_name}_annotated{img_path.suffix}"), annotated)

        print(f"Processed {img_path.name} in {elapsed_ms:.1f}ms - Found {len(detections)} objects")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=str, required=True, help="Image or directory")
    args = parser.parse_args()

    run_inference(args.source)
