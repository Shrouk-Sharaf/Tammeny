import torch
import torchxrayvision as xrv

class XRayModelLoader:
    def __init__(self):
        self.model = None
        self.pathologies = []
    
    def load_nih_model(self):
        try:
            print("Loading NIH-trained medical AI model...")
            self.model = xrv.models.DenseNet(weights="densenet121-res224-nih")
            self.model.eval()
            self.pathologies = self.model.pathologies
            return True
        except Exception as e:
            print(f"Model loading failed: {e}")
            return False
    
    def get_model_info(self):
        if self.model is None:
            return "No model loaded"
        
        return {
            "model_type": "DenseNet121",
            "training_data": "NIH ChestX-ray8",
            "pathologies": self.pathologies,
            "input_size": (224, 224),
            "pathology_count": len(self.pathologies)
        }
    
    def get_available_pathologies(self):
        return self.pathologies if self.model else []