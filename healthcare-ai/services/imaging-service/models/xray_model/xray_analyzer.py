import uuid
import torch
from model_loader import XRayModelLoader
from nih_processor import NIHProcessor


class XRayAnalyzer:
    def __init__(self):
        self.model_loader = XRayModelLoader()
        self.processor    = NIHProcessor()
        self.analysis_history = []

    def initialize_model(self) -> bool:
        return self.model_loader.load_nih_model()

    def analyze_xray(self, image_file, confidence_threshold: float = 0.5) -> dict:
        try:
            if hasattr(image_file, "seek"):
                image_file.seek(0)

            tensor = self.processor.preprocess_image(image_file)

            print(f"  Tensor  mean={tensor.mean():.3f}  std={tensor.std():.3f}")

            with torch.no_grad():
                outputs = self.model_loader.model(tensor)

            print(f"  Output  shape={outputs.shape}  "
                  f"range=[{outputs.min():.3f}, {outputs.max():.3f}]")

            findings = self.processor.interpret_nih_results(
                outputs[0], self.model_loader.pathologies, confidence_threshold
            )
            recommendations = self.processor.generate_recommendations(findings)

            record = {
                "analysis_id":          str(uuid.uuid4())[:8],
                "findings":             findings,
                "recommendations":      recommendations,
                "confidence_threshold": confidence_threshold,
                "total_findings":       len(findings),
            }
            self.analysis_history.append(record)
            return record

        except Exception as e:
            raise RuntimeError(f"X-Ray analysis failed: {e}") from e

    def get_model_info(self) -> dict:
        return self.model_loader.get_model_info()

    def get_analysis_history(self) -> list:
        return self.analysis_history

    def clear_history(self):
        self.analysis_history = []
