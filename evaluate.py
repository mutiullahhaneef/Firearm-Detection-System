"""
evaluate.py — Evaluate trained model on validation set
Usage:
    python evaluate.py
    python evaluate.py --model models/best.pt --data data/dataset.yaml
"""

import argparse
from ultralytics import YOLO


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate firearm detection model")
    parser.add_argument("--model", type=str, default="models/best.pt",
                        help="Path to trained weights")
    parser.add_argument("--data",  type=str, default="data/dataset.yaml",
                        help="Dataset config path")
    parser.add_argument("--imgsz", type=int, default=416,
                        help="Image size for evaluation")
    parser.add_argument("--conf",  type=float, default=0.5,
                        help="Confidence threshold")
    parser.add_argument("--iou",   type=float, default=0.6,
                        help="IoU threshold for NMS")
    return parser.parse_args()


def evaluate(args):
    print("\n" + "="*50)
    print("  Firearm Detection — Model Evaluation")
    print("="*50)
    print(f"  Model    : {args.model}")
    print(f"  Data     : {args.data}")
    print(f"  ImgSize  : {args.imgsz}")
    print("="*50 + "\n")

    model   = YOLO(args.model)
    metrics = model.val(
        data    = args.data,
        imgsz   = args.imgsz,
        conf    = args.conf,
        iou     = args.iou,
        project = "runs/eval",
        name    = "firearm_eval",
        verbose = True,
    )

    print("\n" + "="*50)
    print("  📊  Evaluation Results")
    print("="*50)
    print(f"  mAP@50       : {metrics.box.map50:.4f}")
    print(f"  mAP@50-95    : {metrics.box.map:.4f}")
    print(f"  Precision    : {metrics.box.mp:.4f}")
    print(f"  Recall       : {metrics.box.mr:.4f}")
    print("="*50)

    print("\n  Per-class results:")
    for i, name in model.names.items():
        try:
            ap = metrics.box.ap50[i]
            print(f"    {name:<15} AP@50: {ap:.4f}")
        except (IndexError, AttributeError):
            pass

    print(f"\n  Full results: runs/eval/firearm_eval/\n")


if __name__ == "__main__":
    args = parse_args()
    evaluate(args)
