# data/

Dataset images and labels are not tracked in this repository.

**Expected structure:**

```
data/
├── images/
│   ├── train/
│   └── val/
├── labels/
│   ├── train/
│   └── val/
└── dataset.yaml
```

**Download from Roboflow:**

```bash
python scripts/download_dataset.py \
  --api-key YOUR_KEY \
  --workspace YOUR_WORKSPACE \
  --project YOUR_PROJECT \
  --version 1
```
