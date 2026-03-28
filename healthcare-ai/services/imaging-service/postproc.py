"""
Tammeny — Imaging Result Formatter
Adds plain-language patient summaries on top of raw model output.
"""

from datetime import datetime


# ── Condition metadata ────────────────────────────────────────────────────────

CONDITION_INFO = {
    "Atelectasis": {
        "advice": "May require breathing exercises or respiratory therapy. Monitor for breathing difficulties.",
        "plain":  "Part of the lung appears partially collapsed or compressed. This is often treatable with breathing exercises.",
    },
    "Cardiomegaly": {
        "advice": "Cardiology consultation recommended. May indicate heart disease.",
        "plain":  "The heart looks larger than usual. This can have several causes and your doctor will want to investigate further.",
    },
    "Consolidation": {
        "advice": "Suggests pneumonia or infection. Antibiotic treatment may be needed.",
        "plain":  "There are areas in the lung that look filled with fluid or tissue — this can be a sign of infection like pneumonia.",
    },
    "Edema": {
        "advice": "May indicate heart failure or fluid overload. Urgent evaluation recommended.",
        "plain":  "There appears to be excess fluid in the lungs. This needs prompt medical evaluation.",
    },
    "Effusion": {
        "advice": "Fluid in pleural space. Needs diagnosis of underlying cause.",
        "plain":  "There is fluid around the lung. The doctor will need to find out why and may need to drain it.",
    },
    "Emphysema": {
        "advice": "Chronic lung condition. Smoking cessation and pulmonary rehab may help.",
        "plain":  "The lung tissue looks damaged — this is commonly linked to long-term smoking. Quitting smoking helps slow progression.",
    },
    "Fibrosis": {
        "advice": "Scarring of lung tissue. Pulmonology consultation recommended.",
        "plain":  "There is scarring in the lung tissue. A lung specialist (pulmonologist) should evaluate this further.",
    },
    "Hernia": {
        "advice": "Diaphragmatic hernia. Surgical consultation may be needed.",
        "plain":  "Part of the stomach or intestine may have moved up into the chest. A surgeon should evaluate this.",
    },
    "Infiltration": {
        "advice": "May indicate inflammation or infection. Further evaluation needed.",
        "plain":  "There are areas in the lung that look hazy — this could be infection or inflammation.",
    },
    "Mass": {
        "advice": "Requires follow-up imaging and possibly biopsy to rule out malignancy.",
        "plain":  "There is a growth in the chest area that needs further investigation with additional scans.",
    },
    "Nodule": {
        "advice": "Small growth. Follow-up CT scan recommended to monitor changes.",
        "plain":  "There is a small spot on the lung. Most lung nodules are benign, but your doctor will want to monitor it.",
    },
    "Pleural_Thickening": {
        "advice": "May be benign or indicate asbestos exposure. Monitor with imaging.",
        "plain":  "The lining of the lung appears thicker than usual. This should be monitored over time.",
    },
    "Pneumonia": {
        "advice": "Typically requires antibiotic treatment. Rest and hydration important.",
        "plain":  "The scan shows signs of pneumonia (a lung infection). This is usually treated with antibiotics — rest and fluids also help.",
    },
    "Pneumothorax": {
        "advice": "MEDICAL EMERGENCY — Requires immediate medical attention.",
        "plain":  "⚠️ Air appears to be trapped outside the lung, which can be dangerous. Please seek medical help immediately.",
    },
}

DEFAULT_INFO = {
    "advice": "Consult with your healthcare provider for proper diagnosis and treatment.",
    "plain":  "Your doctor should review this finding and explain what it means for your specific situation.",
}


def get_condition_advice(condition: str) -> str:
    return CONDITION_INFO.get(condition, DEFAULT_INFO)["advice"]


def get_condition_plain(condition: str) -> str:
    return CONDITION_INFO.get(condition, DEFAULT_INFO)["plain"]


# ── Main formatter ────────────────────────────────────────────────────────────

def format_imaging_results(raw_results: dict, analysis_id: str, include_visualization: bool = False) -> dict:
    findings = raw_results.get("findings", [])

    high   = [f for f in findings if f["severity"] == "high"]
    medium = [f for f in findings if f["severity"] == "medium"]
    low    = [f for f in findings if f["severity"] == "low"]

    if high:
        overall_risk = "high"
    elif medium:
        overall_risk = "medium"
    else:
        overall_risk = "low"

    def enrich(finding: dict, include_plain: bool = True) -> dict:
        cond = finding["nih_name"]
        out = {
            "condition":          cond,
            "confidence":         finding["confidence"],
            "confidence_percent": finding["confidence_percent"],
            "medical_advice":     get_condition_advice(cond),
        }
        if include_plain:
            out["plain_language"] = get_condition_plain(cond)
        return out

    # Patient-friendly summary sentence
    if not findings:
        patient_summary = (
            "✅ No significant findings detected. Your X-ray looks normal based on this AI scan. "
            "Always confirm results with your doctor."
        )
    elif overall_risk == "high":
        conditions = ", ".join(f["nih_name"] for f in high)
        patient_summary = (
            f"⚠️ The scan flagged some findings that need prompt medical attention ({conditions}). "
            "Please contact your doctor or visit a clinic as soon as possible."
        )
    elif overall_risk == "medium":
        conditions = ", ".join(f["nih_name"] for f in medium)
        patient_summary = (
            f"The scan found some areas to watch ({conditions}). "
            "Schedule a follow-up with your doctor to discuss next steps."
        )
    else:
        patient_summary = (
            "The scan shows minor findings of low severity. "
            "Discuss these with your doctor at your next routine visit."
        )

    return {
        "analysis_id":       analysis_id,
        "timestamp":         datetime.utcnow().isoformat(),
        "model_used":        "DenseNet-121 / NIH ChestX-ray14",
        "overall_risk_level": overall_risk,
        "patient_summary":   patient_summary,
        "findings_summary": {
            "total_findings":  raw_results.get("total_findings", len(findings)),
            "high_severity":   len(high),
            "medium_severity": len(medium),
            "low_severity":    len(low),
        },
        "detailed_findings": {
            "high_severity":   [enrich(f) for f in high],
            "medium_severity": [enrich(f) for f in medium],
            "low_severity":    [enrich(f, include_plain=False) for f in low[:5]],
        },
        "clinical_recommendations": raw_results.get("recommendations", []),
        "disclaimer": (
            "This AI analysis is for preliminary screening only and is NOT a medical diagnosis. "
            "Always consult with a qualified healthcare professional before making any health decisions."
        ),
    }
