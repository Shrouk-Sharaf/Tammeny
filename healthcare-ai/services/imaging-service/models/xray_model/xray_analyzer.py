import streamlit as st
import torch
import uuid
from model_loader import XRayModelLoader
from nih_processor import NIHProcessor

class XRayAnalyzer:
    def __init__(self):
        self.model_loader = XRayModelLoader()
        self.processor = NIHProcessor()
        self.analysis_history = []
    
    def initialize_model(self):
        return self.model_loader.load_nih_model()
    
    def analyze_xray(self, image_file, confidence_threshold=0.5):
        try:
            if hasattr(image_file, 'seek'):
                image_file.seek(0)
                
            image_tensor = self.processor.preprocess_image(image_file)
            print(f"Input tensor stats - Mean: {image_tensor.mean():.3f}, Std: {image_tensor.std():.3f}")

            with torch.no_grad():
                outputs = self.model_loader.model(image_tensor)
                
            print(f"Model outputs - Shape: {outputs.shape}")
            print(f"Output range: {outputs.min():.3f} to {outputs.max():.3f}")
            
            findings = self.processor.interpret_nih_results(
                outputs[0], 
                self.model_loader.pathologies, 
                confidence_threshold
            )
            
            recommendations = self.processor.generate_recommendations(findings)
            
            analysis_id = str(uuid.uuid4())[:8]
            analysis_record = {
                'analysis_id': analysis_id,
                'findings': findings,
                'recommendations': recommendations,
                'confidence_threshold': confidence_threshold,
                'total_findings': len(findings)
            }
            
            self.analysis_history.append(analysis_record)
            return analysis_record
            
        except Exception as e:
            raise Exception(f"X-Ray analysis failed: {str(e)}")
        
    def get_model_info(self):
        return self.model_loader.get_model_info()
    
    def get_analysis_history(self):
        return self.analysis_history
    
    def clear_history(self):
        self.analysis_history = []