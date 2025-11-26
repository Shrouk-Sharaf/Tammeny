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
        try:
            if hasattr(image_file, 'seek'):
                image_file.seek(0)
                
            img = Image.open(image_file).convert('L')
            img = img.resize((224, 224))
            
            img_array = np.array(img, dtype=np.float32)
            
            print(f"🔍 ORIGINAL - Range: {img_array.min()} to {img_array.max()}")
                            
            img_array = img_array / 255.0
            img_array = img_array * 2048 - 1024  
            
            print(f"🔍 MEDICAL NORMALIZED - Range: {img_array.min():.1f} to {img_array.max():.1f}")
            
            img_array = img_array[None, None, ...]
            
            img_tensor = torch.from_numpy(img_array).float()
            
            print(f"🔍 FINAL TENSOR - Range: {img_tensor.min():.1f} to {img_tensor.max():.1f}")
            
            return img_tensor
                
        except Exception as e:
            print(f"Medical preprocessing failed: {e}")
            raise Exception(f"Image processing failed: {e}")

    def interpret_nih_results(self, outputs, pathologies, confidence_threshold=0.5):
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
        high_severity = ['Pneumothorax', 'Edema', 'Consolidation', 'Pneumonia']
        medium_severity = ['Effusion', 'Mass', 'Cardiomegaly']
        
        if pathology in high_severity and confidence > 0.3:
            return 'high'
        elif pathology in medium_severity and confidence > 0.4:
            return 'medium'
        else:
            return 'low'
    
    def generate_recommendations(self, findings):
        high_severity_findings = [f for f in findings if f['severity'] == 'high']
        medium_severity_findings = [f for f in findings if f['severity'] == 'medium']
        
        recommendations = []
        
        if high_severity_findings:
            recommendations.extend([
                "**Urgent consultation recommended** - seek medical attention promptly",
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

    def debug_preprocessing(self, image_file):
        """Debug method to see what's happening in preprocessing"""
        try:
            # Reset file position
            if hasattr(image_file, 'seek'):
                image_file.seek(0)
                
            img = Image.open(image_file).convert('L')
            original_img = img.copy()
            img = img.resize((224, 224))
            
            img_array = np.array(img, dtype=np.float32)
            print(f"🚨 DEBUG - ORIGINAL: Range {img_array.min():.1f} to {img_array.max():.1f}")
            
            # Your current preprocessing
            img_array = img_array / 255.0
            print(f"🚨 DEBUG - AFTER /255: Range {img_array.min():.3f} to {img_array.max():.3f}")
            
            img_array = img_array * 2048 - 1024  # This might be the problem!
            print(f"🚨 DEBUG - AFTER MEDICAL: Range {img_array.min():.1f} to {img_array.max():.1f}")
            
            return img_array[None, None, ...]
            
        except Exception as e:
            print(f"Debug preprocessing failed: {e}")
            return None