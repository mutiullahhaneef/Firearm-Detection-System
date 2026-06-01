"""
scripts/download_dataset.py — Helper to download a sample firearm dataset
Uses Roboflow public API (free tier).

Usage:
    python scripts/download_dataset.py --workspace <workspace> --project <project> --version <n> --api-key <key>

Or just use the Roboflow web UI to download in YOLOv8 format and place:
    images → data/images/train/  and  data/images/val/
    labels → data/labels/train/  and  data/labels/val/

Recommended datasets (search on roboflow.com/universe):
    - "gun detection"
    - "weapon detection"
    - "firearm classification"
"""

import argparse
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="Download dataset from Roboflow")
    parser.add_argument("--api-key",   type=str, required=True,  help="Roboflow API key")
    parser.add_argument("--workspace", type=str, required=True,  help="Roboflow workspace name")
    parser.add_argument("--project",   type=str, required=True,  help="Roboflow project name")
    parser.add_argument("--version",   type=int, default=1,      help="Dataset version number")
    return parser.parse_args()


def download(args):
    try:
        from roboflow import Roboflow
    except ImportError:
        print("❌  roboflow package not installed.")
        print("    Run: pip install roboflow")
        sys.exit(1)

    print(f"\n📦  Downloading dataset from Roboflow...")
    print(f"    Workspace : {args.workspace}")
    print(f"    Project   : {args.project}")
    print(f"    Version   : {args.version}\n")

    rf      = Roboflow(api_key=args.api_key)
    project = rf.workspace(args.workspace).project(args.project)
    dataset = project.version(args.version).download(
        model_format  = "yolov8",
        location      = "./data",
        overwrite     = True,
    )

    print(f"\n✅  Dataset downloaded to: {dataset.location}")
    print("    Update data/dataset.yaml with your class names if needed.\n")


if __name__ == "__main__":
    args = parse_args()
    download(args)
