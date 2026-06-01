"""
export.py — Export trained model to ONNX or TorchScript for fast deployment
Usage:
    python export.py                          # ONNX (default)
    python export.py --format torchscript
    python export.py --format onnx --int8     # INT8 quantized (fastest)
    python export.py --format onnx --imgsz 320
"""

import argparse
from pathlib import Path
from ultralytics import YOLO


def parse_args():
    parser = argparse.ArgumentParser(description="Export firearm detection model")
    parser.add_argument("--model",  type=str, default="models/best.pt",
                        help="Path to trained .pt weights")
    parser.add_argument("--format", type=str, default="onnx",
                        choices=["onnx", "torchscript", "engine"],
                        help="Export format")
    parser.add_argument("--imgsz",  type=int, default=416,
                        help="Export image size")
    parser.add_argument("--int8",   action="store_true",
                        help="INT8 quantization — 4x smaller, 2-3x faster (slight accuracy drop)")
    parser.add_argument("--half",   action="store_true",
                        help="FP16 half precision — 2x smaller, faster on GPU")
    return parser.parse_args()


def export(args):
    model_path = Path(args.model)

    if not model_path.exists():
        print(f"\n❌  Model not found: {model_path}")
        print("    Train first with: python train.py")
        return

    print("\n" + "="*50)
    print("  Firearm Detection — Model Export")
    print("="*50)
    print(f"  Model    : {args.model}")
    print(f"  Format   : {args.format}")
    print(f"  ImgSize  : {args.imgsz}")
    print(f"  INT8     : {args.int8}")
    print(f"  FP16     : {args.half}")
    print("="*50 + "\n")

    model = YOLO(str(model_path))

    exported = model.export(
        format  = args.format,
        imgsz   = args.imgsz,
        int8    = args.int8,
        half    = args.half,
        dynamic = False,      # fixed shape = faster inference
        simplify= True,       # simplify ONNX graph
    )

    print(f"\n✅  Export complete!")
    print(f"   Exported model: {exported}")

    # Usage hint
    ext = {"onnx": ".onnx", "torchscript": ".torchscript", "engine": ".engine"}
    out_path = model_path.with_suffix(ext.get(args.format, ".onnx"))

    print(f"\n💡  Use exported model in detect.py:")
    print(f"    python detect.py --source image.jpg --model {out_path}\n")

    print("📊  Format Comparison:")
    print("    onnx         → Best for CPU deployment, cross-platform")
    print("    torchscript  → Best for Python/C++ without ONNX runtime")
    print("    engine       → Best for NVIDIA GPU (TensorRT, Jetson)")


if __name__ == "__main__":
    args = parse_args()
    export(args)
