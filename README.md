# Firearm Detection System

A real-time, multi-class firearm detection system built with YOLOv8n. Detects and classifies 6 firearm types from images via a web dashboard or CLI.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-purple)](https://github.com/ultralytics/ultralytics)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-orange)](LICENSE)
[![CI](https://github.com/mutiullahhaneef/firearm-detection/actions/workflows/ci.yml/badge.svg)](https://github.com/mutiullahhaneef/firearm-detection/actions)

---

## Detected Classes

| ID | Class | Color |
|----|-------|-------|
| 0 | pistol | Green |
| 1 | rifle | Orange |
| 2 | shotgun | Red |
| 3 | sniper_rifle | Blue |
| 4 | machine_gun | Purple |
| 5 | revolver | Yellow |

---

## Project Structure

```
firearm-detection/
├── alerts/                     # Alert manager & incident logger
├── configs/                    # Runtime configuration
├── dashboard/
│   ├── backend/                # FastAPI server
│   └── frontend/               # Vanilla JS + CSS UI
├── data/                       # Dataset (not committed — see data/README.md)
├── docs/                       # Model card, data card, privacy policy
├── inference/                  # Core inference engine
├── models/                     # Trained weights (not committed — see models/README.md)
├── monitoring/                 # System health metrics
├── scripts/                    # Utility scripts
├── tests/                      # Unit tests
├── train.py
├── detect.py
├── evaluate.py
├── export.py
├── config.yaml
└── requirements.txt
```

---

## Quick Start

### 1. Install

```bash
git clone https://github.com/YOUR_USERNAME/firearm-detection.git
cd firearm-detection
pip install -r requirements.txt
```

### 2. Add model weights

Place a trained `best.pt` in `models/`, or train from scratch (Step 3).

### 3. Train

```bash
python train.py

# Low-end hardware
python train.py --imgsz 320 --batch 4 --epochs 50
```

Download a dataset from Roboflow:

```bash
python scripts/download_dataset.py \
  --api-key YOUR_KEY \
  --workspace YOUR_WORKSPACE \
  --project YOUR_PROJECT \
  --version 1
```

### 4. Web Dashboard

```bash
python -m dashboard.backend.app
```

Open [http://localhost:8000](http://localhost:8000). Drag and drop an image to run inference.

### 5. CLI Inference

```bash
python detect.py --source path/to/image.jpg
python detect.py --source data/images/val/
python detect.py --source image.jpg --conf 0.6
```

### 6. Evaluate

```bash
python evaluate.py
```

### 7. Export

```bash
# ONNX
python export.py --format onnx

# ONNX INT8 (faster, smaller)
python export.py --format onnx --int8

# TensorRT (NVIDIA GPU)
python export.py --format engine
```

---

## Dashboard Features

| Feature | Description |
|---------|-------------|
| Drag-and-Drop Upload | Test any image instantly |
| Confidence Slider | Adjust detection threshold live (0–100%) |
| Bounding Box Overlay | Color-coded per firearm class |
| Incident Log | Persistent audit trail of every detection |
| Threat Assessment | Visual alert (CLEAR / THREAT DETECTED) |
| Processing Metrics | Inference time and object count per scan |

---

## Configuration

**Training** — `config.yaml`

| Parameter | Default | Notes |
|-----------|---------|-------|
| `imgsz` | 416 | Use 320 for low-end hardware |
| `batch` | 8 | Reduce to 4 if VRAM < 4 GB |
| `epochs` | 100 | 50 is sufficient for fine-tuning |
| `amp` | true | Mixed precision — saves ~40% VRAM |
| `freeze` | 10 | Frozen backbone layers |
| `device` | auto | `cpu` or `0` for first GPU |

**Inference** — `configs/inference_config.yaml`

```yaml
confidence_threshold: 0.50
nms_iou_threshold: 0.45
model_path: "models/best.pt"
output_dir: "outputs"
save_json: true
save_annotated: true
```

---

## Performance

| Model | Size | mAP@50 | Speed (CPU) |
|-------|------|---------|-------------|
| YOLOv8n (PyTorch) | ~6 MB | ~85%* | ~80 ms/img |
| YOLOv8n (ONNX) | ~12 MB | ~85%* | ~40 ms/img |
| YOLOv8n (ONNX INT8) | ~3 MB | ~83%* | ~20 ms/img |

*Depends on dataset quality and size.

---

## Dataset Format

YOLO label files — one detection per line:

```
<class_id> <x_center> <y_center> <width> <height>
```

All values normalized 0–1. Example: `0 0.512 0.431 0.124 0.210`

Recommended source: [Roboflow Universe](https://universe.roboflow.com) — search "gun detection".

---

## Requirements

- Python 3.8+
- 4 GB RAM minimum
- GPU optional (CPU sufficient for inference)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

[MIT License](LICENSE)

This software is for educational and research purposes only. It must not be used for unauthorized surveillance, illegal activity, or any harmful purpose.
