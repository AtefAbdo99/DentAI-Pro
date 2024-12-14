"""
Handles all model-related operations and predictions for the dental X-ray analyzer.
"""

import os
import torch
import torch.nn.functional as F
from torchvision import models
import numpy as np
from PIL import Image
import albumentations as A
from albumentations.pytorch import ToTensorV2
from PyQt6.QtCore import QThread, pyqtSignal
from typing import List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelHandler:
    """Handles model loading, configuration and inference."""
    
    def __init__(self, model_path: str = 'initial_model.pth'):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_path = model_path
        self.class_names = [
            'Nil control', 
            'condensing osteitis', 
            'diffuse lesion', 
            'periapical abcess', 
            'periapical granuloma', 
            'periapical widening', 
            'pericoronitis', 
            'radicular cyst'
        ]
        
        self.transform = A.Compose([
            A.Resize(224, 224),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2()
        ])
        
        self.model = self._initialize_model()

    def _initialize_model(self) -> torch.nn.Module:
        """Initialize and load the model."""
        try:
            model = models.efficientnet_b0(weights=None)
            model.classifier = torch.nn.Sequential(
                torch.nn.Dropout(p=0.2),
                torch.nn.Linear(1280, len(self.class_names))  # Fixed output size to match classes
            )
            
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model file '{self.model_path}' not found!")
                
            checkpoint = torch.load(self.model_path, map_location=self.device)
            
            if 'model_state_dict' in checkpoint:
                model.load_state_dict(checkpoint['model_state_dict'], strict=True)
            else:
                raise KeyError("Invalid checkpoint format")
            
            model = model.to(self.device)
            model.eval()
            return model
            
        except Exception as e:
            logger.error(f"Failed to initialize model: {str(e)}")
            raise

    def preprocess_image(self, image_path: str) -> Optional[torch.Tensor]:
        """Preprocess image for model input."""
        try:
            image = Image.open(image_path).convert('RGB')
            image_array = np.array(image)
            transformed = self.transform(image=image_array)
            return transformed['image'].unsqueeze(0).to(self.device)
        except Exception as e:
            logger.error(f"Error preprocessing image {image_path}: {str(e)}")
            return None

    @torch.no_grad()
    def predict(self, image_tensor: torch.Tensor, top_k: int = 3) -> List[Tuple[str, float]]:
        """Make prediction with confidence scores."""
        try:
            outputs = self.model(image_tensor)
            probabilities = F.softmax(outputs, dim=1)
            confidences, predictions = torch.topk(probabilities, top_k)
            
            results = []
            for pred, conf in zip(predictions[0], confidences[0]):
                results.append((self.class_names[pred.item()], conf.item()))
            return results
            
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            return [("Error", 0.0)]

class PredictionWorker(QThread):
    """Worker thread for handling predictions."""
    
    finished = pyqtSignal(list, str)
    progress = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, model_handler: ModelHandler, image_path: str, top_k: int = 3):
        super().__init__()
        self.model_handler = model_handler
        self.image_path = image_path
        self.top_k = top_k

    def run(self):
        """Run prediction in separate thread."""
        try:
            image_tensor = self.model_handler.preprocess_image(self.image_path)
            if image_tensor is None:
                raise ValueError("Failed to preprocess image")
                
            results = self.model_handler.predict(image_tensor, self.top_k)
            self.finished.emit(results, self.image_path)
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            self.error.emit(str(e))
            self.finished.emit([("Error", 0.0)], self.image_path)