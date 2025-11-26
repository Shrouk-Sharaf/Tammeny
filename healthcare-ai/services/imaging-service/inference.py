import sys
import os
import io

current_dir = os.path.dirname(os.path.abspath(__file__))
xray_model_path = os.path.join(current_dir, 'models', 'xray_model')

sys.path.insert(0, xray_model_path)

print(f"Python path updated. Looking for models in: {xray_model_path}")

try:
    files = os.listdir(xray_model_path)
    print(f"Files in xray_model: {files}")
except Exception as e:
    print(f"Cannot list xray_model directory: {e}")

try:
    from model_loader import XRayModelLoader
    from nih_processor import NIHProcessor
    from xray_analyzer import XRayAnalyzer
    print("SUCCESS: All X-Ray modules imported directly!")
    
except ImportError as e:
    print(f"Import failed: {e}")
    print("Trying alternative import methods...")
    
    try:
        from models.xray_model import model_loader, nih_processor, xray_analyzer
        XRayModelLoader = model_loader.XRayModelLoader
        NIHProcessor = nih_processor.NIHProcessor  
        XRayAnalyzer = xray_analyzer.XRayAnalyzer
        print("SUCCESS: Imported as package!")
    except ImportError as e2:
        print(f"Package import also failed: {e2}")
        raise ImportError("Cannot import X-Ray model files. Check file paths and contents.")

_analyzer = None

def get_analyzer():
    global _analyzer
    if _analyzer is None:
        print("Initializing X-Ray analyzer...")
        _analyzer = XRayAnalyzer()
        if not _analyzer.initialize_model():
            raise RuntimeError("Failed to initialize X-Ray model")
        print("X-Ray analyzer initialized successfully")
    return _analyzer

async def analyze_xray_image(
    file,
    confidence_threshold: float = 0.5  # ✅ Make sure this matches
):
    """Analyze X-Ray image and return results"""
    try:
        analyzer = get_analyzer()
        
        # Handle both BytesIO and UploadFile objects
        if hasattr(file, 'read'):
            # It's already a file-like object (BytesIO)
            image_file = file
            # Reset to beginning in case it was already read
            image_file.seek(0)
        else:
            # It's an UploadFile, read its content
            contents = await file.read()
            image_file = io.BytesIO(contents)
        
        print(f"🔍 Processing image - Type: {type(image_file)}")
        print(f"🎯 Confidence threshold: {confidence_threshold}")  # ✅ Debug print
        
        # Perform analysis - pass the confidence threshold
        results = analyzer.analyze_xray(
            image_file, 
            confidence_threshold=confidence_threshold  # ✅ Pass it through
        )
        
        return results
        
    except Exception as e:
        raise Exception(f"X-Ray analysis error: {str(e)}")