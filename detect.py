"""
detect.py — Run firearm detection on a single image or folder of images
Usage:
    python detect.py --source image.jpg
    python detect.py --source data/images/val/
    python detect.py --source image.jpg --conf 0.6 --model models/best.pt
"""

import argparse
import cv2
import time
from pathlib import Path
from ultralytics import YOLO


# ── Per-class bounding box colors (BGR) ──────────────────────────────────────
CLASS_COLORS = {
    "pistol":      (0,   200,   0),   # Green
    "rifle":       (0,   100, 255),   # Orange
    "shotgun":     (0,     0, 220),   # Red
    "sniper_rifle":(255, 150,   0),   # Blue
    "machine_gun": (180,   0, 180),   # Purple
    "revolver":    (0,   220, 220),   # Yellow
}

DEFAULT_COLOR = (200, 200, 200)  # Gray fallback


def draw_boxes(image, results, class_names):
    """Draw bounding boxes with class labels and confidence scores."""
    for box in results.boxes:
        cls_id     = int(box.cls[0])
        confidence = float(box.conf[0])
        label      = class_names[cls_id]
        color      = CLASS_COLORS.get(label, DEFAULT_COLOR)

        # Bounding box coordinates
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        # Draw filled header bar
        text       = f"{label}  {confidence:.0%}"
        font       = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness  = 2
        (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)

        cv2.rectangle(image, (x1, y1 - th - 10), (x1 + tw + 8, y1), color, -1)
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        cv2.putText(image, text, (x1 + 4, y1 - 6), font, font_scale,
                    (255, 255, 255), thickness, cv2.LINE_AA)

    detected_classes = set()
    for box in results.boxes:
        cls_id = int(box.cls[0])
        detected_classes.add(class_names[cls_id])
        
    if detected_classes:
        title_text = f"Detected: {', '.join(detected_classes)}"
        color = (0, 0, 255) # Red
    else:
        title_text = "No Firearm Detected"
        color = (0, 255, 0) # Green
        
    cv2.putText(image, title_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2, cv2.LINE_AA)

    return image


def detect_image(image_path, model, conf, save_dir):
    """Run detection on a single image and save result."""
    image_path = Path(image_path)
    image      = cv2.imread(str(image_path))

    if image is None:
        print(f"  ⚠️  Could not read image: {image_path}")
        return

    start    = time.perf_counter()
    results  = model.predict(source=image, conf=conf, verbose=False)
    elapsed  = (time.perf_counter() - start) * 1000

    detections = results[0]
    annotated  = draw_boxes(image.copy(), detections, model.names)

    # Save annotated image
    save_path = save_dir / f"detected_{image_path.name}"
    cv2.imwrite(str(save_path), annotated)

    # Console summary
    found = [(model.names[int(b.cls[0])], float(b.conf[0])) for b in detections.boxes]
    print(f"\n  📷  {image_path.name}  ({elapsed:.1f} ms)")
    if found:
        for label, conf_val in found:
            print(f"      ✅  {label:<15} {conf_val:.0%} confidence")
    else:
        print(f"      ❌  No firearms detected")
    print(f"      💾  Saved → {save_path}")


def parse_args():
    parser = argparse.ArgumentParser(description="Firearm detection on images")
    parser.add_argument("--source", type=str, required=True,
                        help="Path to image or folder of images")
    parser.add_argument("--model",  type=str, default="models/best.pt",
                        help="Path to trained weights (.pt or .onnx)")
    parser.add_argument("--conf",   type=float, default=0.5,
                        help="Confidence threshold (0.0–1.0)")
    parser.add_argument("--output", type=str, default="output",
                        help="Output folder for annotated images")
    return parser.parse_args()


def main():
    args     = parse_args()
    source   = Path(args.source)
    save_dir = Path(args.output)
    save_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "="*50)
    print("  Firearm Detection — Image Inference")
    print("="*50)
    print(f"  Source    : {source}")
    print(f"  Model     : {args.model}")
    print(f"  Threshold : {args.conf}")
    print(f"  Output    : {save_dir}")
    print("="*50)

    # Load model
    model = YOLO(args.model)

    # Collect image paths
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff"}

    if source.is_file() and source.suffix.lower() in image_extensions:
        images = [source]
    elif source.is_dir():
        images = [p for p in source.iterdir()
                  if p.suffix.lower() in image_extensions]
        if not images:
            print(f"\n⚠️  No images found in: {source}")
            return
    else:
        print(f"\n❌  Invalid source: {source}")
        print("    Provide a valid image file or folder path.")
        return

    print(f"\n  Found {len(images)} image(s) to process...\n")

    # Run detection
    total_start = time.perf_counter()
    for img_path in sorted(images):
        detect_image(img_path, model, args.conf, save_dir)

    total_time = time.perf_counter() - total_start

    print("\n" + "="*50)
    print(f"  ✅  Done!  {len(images)} image(s) processed")
    print(f"  ⏱️   Total time : {total_time:.2f}s")
    if len(images) > 1:
        print(f"  ⚡  Avg per image : {(total_time/len(images))*1000:.1f}ms")
    print(f"  📁  Results saved to: {save_dir}/")
    print("="*50 + "\n")


if __name__ == "__main__":
    main()
