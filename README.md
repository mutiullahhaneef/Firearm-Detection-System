<div align="center">

# 🔫 Firearm Detection System

**A real-time, multi-class firearm detection system powered by YOLOv8n**  
Detect and classify 6 firearm types from images — with a clean web dashboard included.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-purple)](https://github.com/ultralytics/ultralytics)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-Educational-orange)](#-license)
[![CI](https://github.com/YOUR_USERNAME/firearm-detection/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/firearm-detection/actions)

</div>

---

## 🎯 What It Does

Upload an image → the system detects and classifies firearms in milliseconds, draws bounding boxes, and logs every incident. A live web dashboard lets you tune the confidence threshold and review detection history — all in the browser.

---

## 📸 Demo

> Upload an image via the dashboard and see real-time detections with colored bounding boxes.

```
http://localhost:8000
```

---

## 📌 Detected Classes

| ID | Class | Detection Color |
|----|-------|----------------|
| 0 | `pistol` | 🟩 Green |
| 1 | `rifle` | 🟧 Orange |
| 2 | `shotgun` | 🟥 Red |
| 3 | `sniper_rifle` | 🟦 Blue |
| 4 | `machine_gun` | 🟪 Purple |
| 5 | `revolver` | 🟨 Yellow |

---

## 🗂️ Project Structure

```
firearm-detection/
│
├── alerts/                     ← Alert manager & incident logger
│   ├── alert_manager.py
│   ├── incident_logger.py
│   └── alert_config.yaml
│
├── configs/                    ← Runtime configuration
│   ├── inference_config.yaml
│   └── alert_config.yaml
│
├── dashboard/
│   ├── backend/                ← FastAPI server
│   │   ├── app.py
│   │   └── detection_service.py
│   └── frontend/               ← Vanilla JS + CSS UI
│       ├── index.html
│       ├── app.js
│       └── styles.css
│
├── data/                       ← Your dataset (NOT committed)
│   ├── images/train/
│   ├── images/val/
│   ├── labels/train/
│   ├── labels/val/
│   └── dataset.yaml
│
├── inference/                  ← Core inference engine
│   └── run_image.py
│
├── models/                     ← Trained weights (NOT committed)
│   └── best.pt
│
├── monitoring/                 ← System health metrics
├── outputs/                    ← Annotated result images (NOT committed)
├── incidents/                  ← Incident JSON log (NOT committed)
├── scripts/                    ← Utility scripts
│   └── download_dataset.py
├── tests/                      ← Unit tests
│
├── train.py                    ← Fine-tune YOLOv8
├── detect.py                   ← Run inference from CLI
├── evaluate.py                 ← mAP / metric evaluation
├── export.py                   ← Export to ONNX / TorchScript
├── config.yaml                 ← Training config
├── requirements.txt
└── README.md
```

---

## ⚡ Quick Start

### 1. Clone & install

```bash
git clone https://github.com/YOUR_USERNAME/firearm-detection.git
cd firearm-detection
pip install -r requirements.txt
```

### 2. Get a trained model

Either train your own (Step 3) or place a pre-trained `best.pt` in the `models/` folder.

```
models/best.pt
```

### 3. Train on your dataset

Place YOLO-format images and labels in `data/` or download from Roboflow:

```bash
python scripts/download_dataset.py \
  --api-key YOUR_KEY \
  --workspace YOUR_WORKSPACE \
  --project YOUR_PROJECT \
  --version 1
```

Then train:

```bash
python train.py
# Low-end GPU / CPU:
python train.py --imgsz 320 --batch 4 --epochs 50
```

### 4. Run the web dashboard

```bash
python -m dashboard.backend.app
```

Open **http://localhost:8000** — drag and drop an image to detect firearms instantly.

### 5. CLI inference

```bash
# Single image
python detect.py --source path/to/image.jpg

# Folder of images
python detect.py --source data/images/val/

# Custom confidence threshold
python detect.py --source image.jpg --conf 0.6
```

### 6. Evaluate

```bash
python evaluate.py
```

### 7. Export for deployment

```bash
# ONNX (best for CPU)
python export.py --format onnx

# ONNX INT8 — 4× faster, 4× smaller
python export.py --format onnx --int8

# TensorRT (NVIDIA GPU)
python export.py --format engine
```

---

## 🌐 Dashboard Features

| Feature | Description |
|---------|-------------|
| **Drag-and-Drop Upload** | Instantly test any image |
| **Confidence Slider** | Tune detection threshold live (0–100%) |
| **Bounding Box Overlay** | Color-coded per firearm class on the result image |
| **Incident Log** | Persistent audit trail of every detection |
| **Threat Assessment** | Visual alert badge (CLEAR / THREAT DETECTED) |
| **Processing Metrics** | Inference time and object count per scan |

---

## 🔧 Configuration

### Training (`config.yaml`)

| Parameter | Default | Notes |
|-----------|---------|-------|
| `imgsz` | 416 | Use 320 for very low-end hardware |
| `batch` | 8 | Reduce to 4 if VRAM < 4 GB |
| `epochs` | 100 | 50 is enough for fine-tuning |
| `amp` | true | Saves ~40% VRAM via mixed precision |
| `freeze` | 10 | Freeze backbone layers for faster training |
| `device` | auto | `cpu` or `0` for first GPU |

### Inference (`configs/inference_config.yaml`)

```yaml
confidence_threshold: 0.50   # minimum confidence to show a detection
nms_iou_threshold: 0.45      # overlap threshold for NMS
model_path: "models/best.pt"
output_dir: "outputs"
save_json: true
save_annotated: true
```

---

## 📊 Performance

| Model | Size | mAP\@50 | Speed (CPU) |
|-------|------|---------|-------------|
| YOLOv8n (PyTorch) | ~6 MB | ~85%* | ~80 ms/img |
| YOLOv8n (ONNX) | ~12 MB | ~85%* | ~40 ms/img |
| YOLOv8n (ONNX INT8) | ~3 MB | ~83%* | ~20 ms/img |

> \*Accuracy depends on dataset quality and size.

---

## 🚀 Deployment Tips

| Target | Recommended format |
|--------|--------------------|
| CPU / low-end machine | `python export.py --format onnx --int8` |
| NVIDIA GPU / Jetson | `python export.py --format engine` |
| Cross-platform server | ONNX + `onnxruntime` |

---

## 📁 Dataset Format (YOLO)

Each `.txt` label file — one line per object:

```
<class_id> <x_center> <y_center> <width> <height>
```

All values normalized 0–1. Example:

```
0 0.512 0.431 0.124 0.210
```

> 💡 Recommended: Search `"gun detection"` on [Roboflow Universe](https://universe.roboflow.com)

---

## 🛠️ Requirements

- Python 3.8+
- 4 GB RAM minimum (8 GB recommended)
- GPU optional — CPU works fine for inference

---

## 🤝 Contributing

Pull requests are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "feat: add my feature"`
4. Push and open a PR

---

## ⚠️ Ethical Use

This system is built for **educational and research purposes only**.  
It must **not** be used for surveillance, illegal activity, or any harmful purpose.  
The authors are not responsible for misuse.

---

## 📄 License

[MIT License](LICENSE) — © 2024 Firearm Detection Project Contributors
