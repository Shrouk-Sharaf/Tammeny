# nih_processor.py - UPDATED
import torch
from PIL import Image
import numpy as np

class NIHProcessor:
    def __init__(self):
        self.nih_diseases = [
            'Atelectasis', 'Cardiomegaly', 'Effusion', 'Infiltration',
            'Mass', 'Nodule', 'Pneumonia', 'Pneumothorax',
            'Consolidation', 'Edema', 'Emphysema', 'Fibrosis',
            'Pleural_Thickening', 'Hernia'
        ]
    
    def preprocess_image(self, image_file):
        """Preprocess uploaded image for medical model - FIXED VERSION"""
        try:
            img = Image.open(image_file).convert('L')  # Convert to grayscale
            img = img.resize((224, 224))
            
            # Convert to numpy array
            img_array = np.array(img, dtype=np.float32)
            
            print(f"🔍 Original image - Range: {img_array.min()} to {img_array.max()}")
            
            # MEDICAL IMAGE NORMALIZATION FIX:
            # Medical models expect images in Hounsfield units [-1024, 1024]
            # Scale to [0, 1] then map to medical range
            
            # 1. Normalize to [0, 1]
            img_array = img_array / 255.0
            
            # 2. Map to medical image range [-1024, 1024]
            # Typical medical images: air = -1000, water = 0, bone = +1000
            img_array = img_array * 2048 - 1024  # [0,1] -> [-1024, 1024]
            
            print(f"🔍 Medical normalized - Range: {img_array.min():.1f} to {img_array.max():.1f}")
            
            # Add batch and channel dimensions: [1, 1, 224, 224]
            img_array = img_array[None, None, ...]
            
            # Convert to tensor
            img_tensor = torch.from_numpy(img_array).float()
            
            return img_tensor
            
        except Exception as e:
            print(f"❌ Medical preprocessing failed: {e}")
            raise Exception(f"Image processing failed: {e}")
    
    def interpret_nih_results(self, outputs, pathologies, confidence_threshold=0.1):
        significant_findings = []
        
        for i, pathology in enumerate(pathologies):
            if not pathology or pathology.strip() == "":
                continue
                
            confidence = float(outputs[i])
            if confidence > confidence_threshold:
                nih_name = self.map_to_nih_disease(pathology)
                significant_findings.append({
                    'pathology': pathology,
                    'nih_name': nih_name,
                    'confidence': confidence,
                    'confidence_percent': f"{confidence*100:.1f}%",
                    'severity': self.assess_severity(pathology, confidence)
                })
        
        significant_findings.sort(key=lambda x: x['confidence'], reverse=True)
        return significant_findings
    
    def map_to_nih_disease(self, pathology):
        """Map model pathology names to NIH disease names"""
        mapping = {
            'Atelectasis': 'Atelectasis',
            'Cardiomegaly': 'Cardiomegaly', 
            'Consolidation': 'Consolidation',
            'Edema': 'Edema',
            'Effusion': 'Effusion',
            'Emphysema': 'Emphysema',
            'Fibrosis': 'Fibrosis',
            'Hernia': 'Hernia',
            'Infiltration': 'Infiltration',
            'Mass': 'Mass',
            'Nodule': 'Nodule',
            'Pleural_Thickening': 'Pleural Thickening',
            'Pneumonia': 'Pneumonia',
            'Pneumothorax': 'Pneumothorax'
        }
        return mapping.get(pathology, pathology)
    
    def assess_severity(self, pathology, confidence):
        """Assess clinical severity of finding"""
        high_severity = ['Pneumothorax', 'Edema', 'Consolidation', 'Pneumonia']
        medium_severity = ['Effusion', 'Mass', 'Cardiomegaly']
        
        if pathology in high_severity and confidence > 0.3:
            return 'high'
        elif pathology in medium_severity and confidence > 0.4:
            return 'medium'
        else:
            return 'low'
    
    def generate_recommendations(self, findings):
        """Generate clinical recommendations based on findings"""
        high_severity_findings = [f for f in findings if f['severity'] == 'high']
        medium_severity_findings = [f for f in findings if f['severity'] == 'medium']
        
        recommendations = []
        
        if high_severity_findings:
            recommendations.extend([
                "🚨 **Urgent consultation recommended** - seek medical attention promptly",
                "Consider visiting emergency care if experiencing breathing difficulties",
                "Share these results with a healthcare provider immediately"
            ])
        elif medium_severity_findings:
            recommendations.extend([
                "Schedule follow-up with a pulmonologist or radiologist",
                "Monitor symptoms and report any changes to your doctor",
                "Consider additional imaging studies for confirmation"
            ])
        else:
            recommendations.extend([
                "Routine follow-up as recommended by your healthcare provider",
                "Continue with regular health monitoring",
                "No immediate intervention needed based on this analysis"
            ])
        
        return recommendations