# models/

Model weights are not tracked in this repository due to file size.

**To get weights:**

```bash
# Train from scratch
python train.py

# or place a pre-trained best.pt here
models/best.pt
```

To track large files with Git LFS:
```bash
git lfs install
git lfs track "models/*.pt"
git add .gitattributes
```
