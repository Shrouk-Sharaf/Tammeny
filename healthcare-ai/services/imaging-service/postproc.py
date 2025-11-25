# services/imaging-service/postproc.py
from datetime import datetime

def format_imaging_results(raw_results, analysis_id, include_visualization=False):
    """Format imaging results for API response"""
    
    # Categorize findings by severity
    high_severity = [f for f in raw_results['findings'] if f['severity'] == 'high']
    medium_severity = [f for f in raw_results['findings'] if f['severity'] == 'medium']
    low_severity = [f for f in raw_results['findings'] if f['severity'] == 'low']
    
    # Calculate overall risk level
    if high_severity:
        overall_risk = "high"
    elif medium_severity:
        overall_risk = "medium" 
    else:
        overall_risk = "low"
    
    formatted_results = {
        "analysis_id": analysis_id,
        "timestamp": datetime.utcnow().isoformat(),
        "model_used": "chest-xray-nih",
        "overall_risk_level": overall_risk,
        "findings_summary": {
            "total_findings": raw_results['total_findings'],
            "high_severity": len(high_severity),
            "medium_severity": len(medium_severity),
            "low_severity": len(low_severity)
        },
        "detailed_findings": {
            "high_severity": [
                {
                    "condition": finding['nih_name'],
                    "confidence": finding['confidence'],
                    "confidence_percent": finding['confidence_percent'],
                    "medical_advice": get_condition_advice(finding['nih_name'])
                }
                for finding in high_severity
            ],
            "medium_severity": [
                {
                    "condition": finding['nih_name'],
                    "confidence": finding['confidence'],
                    "confidence_percent": finding['confidence_percent'],
                    "medical_advice": get_condition_advice(finding['nih_name'])
                }
                for finding in medium_severity
            ],
            "low_severity": [
                {
                    "condition": finding['nih_name'],
                    "confidence": finding['confidence'], 
                    "confidence_percent": finding['confidence_percent']
                }
                for finding in low_severity[:5]  # Limit low severity findings
            ]
        },
        "clinical_recommendations": raw_results['recommendations'],
        "disclaimer": "This AI analysis is for preliminary screening only and is NOT a medical diagnosis. Always consult with qualified healthcare professionals for medical decisions."
    }
    
    return formatted_results

def get_condition_advice(condition):
    """Get basic medical advice for conditions"""
    advice_map = {
        "Atelectasis": "May require breathing exercises or respiratory therapy. Monitor for breathing difficulties.",
        "Cardiomegaly": "Cardiology consultation recommended. May indicate heart disease.",
        "Consolidation": "Suggests pneumonia or infection. Antibiotic treatment may be needed.",
        "Edema": "May indicate heart failure or fluid overload. Urgent evaluation recommended.",
        "Effusion": "Fluid in pleural space. Needs diagnosis of underlying cause.",
        "Emphysema": "Chronic lung condition. Smoking cessation and pulmonary rehab may help.",
        "Fibrosis": "Scarring of lung tissue. Pulmonology consultation recommended.",
        "Hernia": "Diaphragmatic hernia. Surgical consultation may be needed.",
        "Infiltration": "May indicate inflammation or infection. Further evaluation needed.",
        "Mass": "Requires follow-up imaging and possibly biopsy to rule out malignancy.",
        "Nodule": "Small growth. Follow-up CT scan recommended to monitor changes.",
        "Pleural Thickening": "May be benign or indicate asbestos exposure. Monitor with imaging.",
        "Pneumonia": "Typically requires antibiotic treatment. Rest and hydration important.",
        "Pneumothorax": "MEDICAL EMERGENCY - Requires immediate medical attention. Can be life-threatening."
    }
    return advice_map.get(condition, "Consult with healthcare provider for proper diagnosis and treatment.")