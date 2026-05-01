import os
import argparse
from ultralytics import YOLO

"""
SDIRS Disaster Computer Vision Fine-tuning Script
-------------------------------------------------
This script provides the framework for fine-tuning YOLOv8 on disaster-specific 
imagery (e.g., xBD dataset, FloodNet, or custom drone footage).

Prerequisites:
1. Prepare your dataset in YOLO format (images/ and labels/ directories).
2. Create a data.yaml file defining classes (e.g., flood, fire, collapsed_building).
3. Recommended dataset: xBD (https://xview2.org/dataset)

Usage:
python train_cv.py --data path/to/disaster_data.yaml --epochs 50 --img 640
"""

def train_model(data_yaml, epochs=50, imgsz=640, model_type='yolov8n.pt'):
    print(f"--- Starting SDIRS CV Fine-tuning ({model_type}) ---")
    
    # Load a pretrained YOLOv8 model
    model = YOLO(model_type)
    
    # Train the model
    # Results will be saved in 'runs/detect/train'
    results = model.train(
        data=data_yaml, 
        epochs=epochs, 
        imgsz=imgsz, 
        device='cpu', # Change to '0' if GPU is available
        project='sdirs_cv',
        name='disaster_v1'
    )
    
    print("\n--- Training Complete ---")
    print(f"Best model saved to: {results.save_dir}/weights/best.pt")
    
    # Recommend next step
    target_path = os.path.join(os.path.dirname(__file__), '..', '..', 'models_data', 'disaster_cv_best.pt')
    print(f"ACTION: Copy the best.pt file to {target_path} and update config.py")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SDIRS CV Training')
    parser.add_argument('--data', type=str, default='disaster_data.yaml', help='Path to data.yaml')
    parser.add_argument('--epochs', type=int, default=10, help='Number of epochs')
    parser.add_argument('--model', type=str, default='yolov8n.pt', help='Base model (n, s, m, l, x)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.data):
        print(f"ERROR: Dataset configuration {args.data} not found.")
        print("To run a mock training for demonstration, create a dummy yaml or provided a valid path.")
    else:
        train_model(args.data, epochs=args.epochs, model_type=args.model)
