"""
train.py — Fine-tune YOLOv8n for multi-class firearm detection
Usage:
    python train.py
    python train.py --epochs 50 --batch 4 --imgsz 320
"""

import argparse
from pathlib import Path
from ultralytics import YOLO


def parse_args():
    parser = argparse.ArgumentParser(description="Train firearm detection model")
    parser.add_argument("--model",   type=str,   default="yolov8n.pt",       help="Base model weights")
    parser.add_argument("--data",    type=str,   default="data/dataset.yaml", help="Dataset config path")
    parser.add_argument("--epochs",  type=int,   default=100,                 help="Training epochs")
    parser.add_argument("--imgsz",   type=int,   default=416,                 help="Image size (320 or 416)")
    parser.add_argument("--batch",   type=int,   default=8,                   help="Batch size (use 4 for low VRAM)")
    parser.add_argument("--device",  type=str,   default="",                  help="Device: '' = auto, 'cpu', '0' = GPU 0")
    parser.add_argument("--workers", type=int,   default=2,                   help="Dataloader workers (0 on Windows)")
    parser.add_argument("--freeze",  type=int,   default=10,                  help="Freeze first N backbone layers")
    return parser.parse_args()


def train(args):
    print("\n" + "="*50)
    print("  Firearm Detection — Training Started")
    print("="*50)
    print(f"  Model   : {args.model}")
    print(f"  Epochs  : {args.epochs}")
    print(f"  ImgSize : {args.imgsz}")
    print(f"  Batch   : {args.batch}")
    print(f"  Device  : {'auto' if args.device == '' else args.device}")
    print("="*50 + "\n")

    # Load pretrained YOLOv8n
    model = YOLO(args.model)

    # Train
    results = model.train(
        data         = args.data,
        epochs       = args.epochs,
        imgsz        = args.imgsz,
        batch        = args.batch,
        device       = args.device,
        workers      = args.workers,
        freeze       = args.freeze,
        amp          = True,          # Mixed precision — saves VRAM
        optimizer    = "AdamW",
        lr0          = 0.001,
        lrf          = 0.01,
        warmup_epochs= 3,
        hsv_h        = 0.015,
        hsv_s        = 0.7,
        hsv_v        = 0.4,
        degrees      = 5.0,
        flipud       = 0.0,
        fliplr       = 0.5,
        mosaic       = 1.0,
        project      = "runs/train",
        name         = "firearm_multiclass",
        exist_ok     = True,
        save         = True,
        plots        = True,
    )

    # Copy best weights to models/
    best_weights = Path("runs/train/firearm_multiclass/weights/best.pt")
    if best_weights.exists():
        import shutil
        Path("models").mkdir(exist_ok=True)
        shutil.copy(best_weights, "models/best.pt")
        print(f"\n✅ Best weights saved to: models/best.pt")

    print("\n✅ Training complete!")
    print(f"   Results saved to: runs/train/firearm_multiclass/")
    return results


if __name__ == "__main__":
    args = parse_args()
    train(args)
