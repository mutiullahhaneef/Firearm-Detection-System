import os
from pathlib import Path

def validate_dataset(dataset_dir="dataset"):
    print("Validating dataset...")
    base_dir = Path(dataset_dir)
    images_dir = base_dir / "images"
    labels_dir = base_dir / "labels"
    
    splits = ["train", "val", "test"]
    
    total_images = 0
    total_labels = 0
    errors = []
    
    for split in splits:
        img_split = images_dir / split
        lbl_split = labels_dir / split
        
        if not img_split.exists() or not lbl_split.exists():
            continue
            
        images = {f.stem: f for f in img_split.iterdir() if f.is_file()}
        labels = {f.stem: f for f in lbl_split.iterdir() if f.is_file()}
        
        total_images += len(images)
        total_labels += len(labels)
        
        # Check orphan images
        for stem, img_path in images.items():
            if stem not in labels:
                errors.append(f"Orphan image (no label): {img_path}")
                
        # Check orphan labels & coordinate bounds
        for stem, lbl_path in labels.items():
            if stem not in images:
                errors.append(f"Orphan label (no image): {lbl_path}")
            else:
                with open(lbl_path, "r") as f:
                    for line_idx, line in enumerate(f):
                        parts = line.strip().split()
                        if len(parts) != 5:
                            errors.append(f"Invalid format {lbl_path}:{line_idx+1}")
                            continue
                        try:
                            cls_id, cx, cy, w, h = map(float, parts)
                            if not (0 <= cx <= 1 and 0 <= cy <= 1 and 0 <= w <= 1 and 0 <= h <= 1):
                                errors.append(f"Out of bounds {lbl_path}:{line_idx+1}")
                            if w * h < 0.0001:
                                errors.append(f"Near-zero area {lbl_path}:{line_idx+1}")
                        except ValueError:
                            errors.append(f"Non-numeric values {lbl_path}:{line_idx+1}")
                            
    print(f"Total Images: {total_images}")
    print(f"Total Labels: {total_labels}")
    print(f"Total Errors: {len(errors)}")
    
    if errors:
        print("First 10 errors:")
        for e in errors[:10]:
            print(f"  - {e}")
        
        with open("reports/validation_report.txt", "w") as f:
            f.write("\n".join(errors))
        print("Full report saved to reports/validation_report.txt")
    else:
        print("Dataset is fully valid! 🚀")

if __name__ == "__main__":
    Path("reports").mkdir(exist_ok=True)
    validate_dataset()
