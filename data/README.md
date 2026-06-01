# Dataset directory
#
# Place your images and YOLO-format labels here:
#
#   data/
#   ├── images/
#   │   ├── train/    ← training images (.jpg / .png)
#   │   └── val/      ← validation images
#   ├── labels/
#   │   ├── train/    ← label .txt files (same names as images)
#   │   └── val/
#   └── dataset.yaml  ← dataset config (already committed)
#
# The images/ and labels/ sub-directories are gitignored.
# Only dataset.yaml is tracked.
#
# To download a dataset from Roboflow:
#   python scripts/download_dataset.py \
#     --api-key YOUR_KEY \
#     --workspace YOUR_WORKSPACE \
#     --project YOUR_PROJECT \
#     --version 1
