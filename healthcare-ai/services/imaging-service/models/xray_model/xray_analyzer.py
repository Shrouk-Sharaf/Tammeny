# xray_analyzer.py
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
        """Initialize the pre-trained model"""
        return self.model_loader.load_nih_model()
    
    def analyze_xray(self, image_file, confidence_threshold=0.1):
        """Main analysis pipeline for X-Ray images"""
        try:
            # Preprocess image
            image_tensor = self.processor.preprocess_image(image_file)
            
            # Run model prediction
            with torch.no_grad():
                outputs = self.model_loader.model(image_tensor)
            
            # Interpret results
            findings = self.processor.interpret_nih_results(
                outputs[0], 
                self.model_loader.pathologies, 
                confidence_threshold
            )
            
            # Generate recommendations
            recommendations = self.processor.generate_recommendations(findings)
            
            # Create analysis record
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
        """Get information about the loaded model"""
        return self.model_loader.get_model_info()
    
    def get_analysis_history(self):
        """Get history of analyses performed"""
        return self.analysis_history
    
    def clear_history(self):
        """Clear analysis history"""
        self.analysis_history = []

# Convenience function for quick analysis
def quick_analyze(image_file):
    """One-line function for quick X-Ray analysis"""
    analyzer = XRayAnalyzer()
    if analyzer.initialize_model():
        return analyzer.analyze_xray(image_file)
    else:
        raise Exception("Failed to initialize X-Ray model")