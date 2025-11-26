import streamlit as st
import os
import requests
import json
from PIL import Image
import io
import base64

# --- CONFIGURATION ---
XRAY_SERVICE_URL = "http://localhost:8002"

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="HealthAI Portal",
    page_icon="🏥",
    layout="wide"
)

# --- HEADER ---
col1, col2 = st.columns([1, 5])
with col1:
    logo_path = "assets/logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=100)
    else:
        st.write("LOGO")
with col2:
    st.title("Tammeny")

# --- X-RAY SERVICE FUNCTIONS ---
def check_service_health():
    """Check if X-Ray service is running"""
    try:
        response = requests.get(f"{XRAY_SERVICE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def analyze_xray(image_file, confidence_threshold=0.5):
    """
    Send X-Ray image to the analysis service
    """
    try:
        # Prepare the file for upload
        files = {"file": (image_file.name, image_file.getvalue(), image_file.type)}
        
        # ✅ ADD CONFIDENCE THRESHOLD TO REQUEST
        data = {"confidence_threshold": confidence_threshold}
        
        # Debug: Show what's being sent
        st.sidebar.subheader("🔍 Request Debug")
        st.sidebar.write(f"Sending confidence_threshold: {confidence_threshold}")
        
        response = requests.post(
            f"{XRAY_SERVICE_URL}/analyze/xray", 
            files=files,
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Show received threshold in response
            st.sidebar.write(f"Response confidence_threshold: {result.get('confidence_threshold', 'Not found')}")
            
            return result
        else:
            st.error(f"Service error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Error analyzing X-Ray: {str(e)}")
        return None
    
def display_xray_results(results):
    """
    Display the X-Ray analysis results in a user-friendly format
    """
    if not results:
        st.error("No results to display")
        return
    
    st.subheader("📊 Analysis Results")
    
    # Display overall risk level banner
    risk_level = results.get('overall_risk_level', 'unknown').upper()
    if risk_level == 'HIGH':
        st.error(f"🚨 **HIGH RISK DETECTED** - Urgent Medical Attention Recommended")
    elif risk_level == 'MEDIUM':
        st.warning(f"⚠️ **MEDIUM RISK DETECTED** - Prompt Medical Evaluation Recommended")
    else:
        st.success(f"✅ **LOW RISK** - Routine Follow-up Recommended")
    
    # Create columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🩺 High Severity Conditions:**")
        
        if 'detailed_findings' in results and 'high_severity' in results['detailed_findings']:
            high_findings = results['detailed_findings']['high_severity']
            
            for finding in high_findings:
                condition = finding.get('condition', 'Unknown')
                confidence = finding.get('confidence_percent', 'N/A')
                medical_advice = finding.get('medical_advice', 'Consult healthcare provider.')
                
                st.error(f"🔴 **{condition}**")
                st.write(f"   **Confidence**: {confidence}")
                st.write(f"   **Advice**: {medical_advice}")
                st.write("---")
        else:
            st.success("✅ No high severity conditions detected")
        
        st.markdown("**🟡 Medium Severity Conditions:**")
        
        if 'detailed_findings' in results and 'medium_severity' in results['detailed_findings']:
            medium_findings = results['detailed_findings']['medium_severity']
            
            for finding in medium_findings:
                condition = finding.get('condition', 'Unknown')
                confidence = finding.get('confidence_percent', 'N/A')
                medical_advice = finding.get('medical_advice', 'Follow-up recommended.')
                
                st.warning(f"🟡 **{condition}**")
                st.write(f"   **Confidence**: {confidence}")
                st.write(f"   **Advice**: {medical_advice}")
                st.write("---")
        else:
            st.info("No medium severity conditions detected")
    
    with col2:
        st.markdown("**🟢 Low Severity Conditions:**")
        
        if 'detailed_findings' in results and 'low_severity' in results['detailed_findings']:
            low_findings = results['detailed_findings']['low_severity']
            
            for finding in low_findings:
                condition = finding.get('condition', 'Unknown')
                confidence = finding.get('confidence_percent', 'N/A')
                medical_advice = finding.get('medical_advice', 'Routine monitoring recommended.')
                
                st.success(f"🟢 **{condition}**")
                st.write(f"   **Confidence**: {confidence}")
                if medical_advice:
                    st.write(f"   **Note**: {medical_advice}")
                st.write("---")
        else:
            st.info("No low severity conditions detected")
        
        # Confidence distribution visualization
        st.markdown("**📈 Top Findings by Confidence:**")
        
        if 'detailed_findings' in results:
            all_findings = []
            for severity_level in ['high_severity', 'medium_severity', 'low_severity']:
                if severity_level in results['detailed_findings']:
                    all_findings.extend(results['detailed_findings'][severity_level])
            
            # Sort by confidence (highest first)
            all_findings.sort(key=lambda x: x.get('confidence', 0), reverse=True)
            
            for finding in all_findings[:5]:  # Show top 5 most confident findings
                condition = finding.get('condition', 'Unknown')
                confidence = finding.get('confidence', 0)
                confidence_percent = finding.get('confidence_percent', '0%')
                
                st.write(f"**{condition}**")
                st.write(f"{confidence_percent}")
                st.progress(float(confidence))
                st.write("")

    # Clinical Recommendations
    st.markdown("---")
    st.markdown("**💡 Clinical Recommendations:**")
    
    if 'clinical_recommendations' in results and results['clinical_recommendations']:
        for i, recommendation in enumerate(results['clinical_recommendations']):
            # Clean up markdown formatting
            clean_rec = recommendation.replace("**", "").replace("__", "")
            st.write(f"{i+1}. {clean_rec}")
    else:
        st.write("1. Consult with healthcare provider for final interpretation")
        st.write("2. Follow up as recommended by medical professional")
        st.write("3. Monitor symptoms and report any changes")
    
    # Analysis Information
    st.markdown("---")
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.markdown("**📋 Analysis Information:**")
        if 'analysis_id' in results:
            st.write(f"**Analysis ID**: `{results['analysis_id']}`")
        if 'model_used' in results:
            st.write(f"**AI Model**: {results['model_used']}")
        if 'timestamp' in results:
            # Format timestamp for better readability
            timestamp = results['timestamp'].replace('T', ' ').split('.')[0]
            st.write(f"**Analysis Time**: {timestamp}")
    
    with col_info2:
        st.markdown("**📊 Findings Summary:**")
        if 'findings_summary' in results:
            summary = results['findings_summary']
            st.write(f"**Total Findings**: {summary.get('total_findings', 0)}")
            st.write(f"**High Severity**: {summary.get('high_severity', 0)}")
            st.write(f"**Medium Severity**: {summary.get('medium_severity', 0)}")
            st.write(f"**Low Severity**: {summary.get('low_severity', 0)}")
    
    # Medical Disclaimer
    if 'disclaimer' in results:
        st.markdown("---")
        st.warning(results['disclaimer'])
    else:
        st.markdown("---")
        st.warning("""
        ⚠️ **Medical Disclaimer**
        This AI analysis is for preliminary screening only and is NOT a medical diagnosis. 
        Always consult with qualified healthcare professionals for medical decisions.
        """)# --- DISCLAIMER ---

def show_medical_disclaimer():
    st.warning("""
    ⚠️ **Medical Disclaimer**
    - This AI tool is for assistance only
    - Not a substitute for professional medical diagnosis
    - Always consult with qualified healthcare providers
    - Results should be interpreted by medical professionals
    """)

# -------------------------- MAIN TABS --------------------------
tabs = st.tabs([
    "🏠 Home",
    "💊 Diseases & Treatments", 
    "🤖 AI Diagnostics",
    "📅 Appointments",
    "👨‍⚕️ Doctors",
    "🗺️ Clinic Map",
    "ℹ️ About Us"
])

# ---------------------------------------------------------------
# TAB 3: AI DIAGNOSTICS (Updated with X-Ray Integration)
# ---------------------------------------------------------------
with tabs[2]:
    st.header("AI Diagnostic Tools")
    
    # Medical disclaimer
    show_medical_disclaimer()

    # Check service status first
    service_healthy = check_service_health()
    
    st.subheader("Service Status")
    if service_healthy:
        st.success("✅ X-Ray service is connected and healthy")
    else:
        st.error("❌ X-Ray service is not available")
        st.info("💡 To enable X-Ray analysis, please start the imaging service:")
        st.code("cd services/imaging-service && python server.py")

    ai_choice = st.radio(
        "Choose a diagnostic tool:",
        ["Prescription OCR", "Chest X-Ray Analysis"],
        horizontal=True
    )

    # --- OCR ---
    if ai_choice == "Prescription OCR":
        uploaded = st.file_uploader("Upload Prescription", type=["png", "jpg", "jpeg"])
        if uploaded:
            st.image(uploaded, width=300)
            if st.button("Analyze Prescription"):
                st.success("OCR processing... (connect service here)")

    # --- X-RAY ANALYSIS ---
    else:
        st.subheader("Chest X-Ray Analysis")
        
        if not service_healthy:
            st.warning("X-Ray analysis is currently unavailable. Please start the imaging service.")
        
        uploaded = st.file_uploader(
            "Upload Chest X-Ray Image", 
            type=["png", "jpg", "jpeg"],
            help="Supported formats: PNG, JPG, JPEG",
            disabled=not service_healthy
        )
        
        if uploaded and service_healthy:
            # Display the uploaded image
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image(uploaded, caption="Uploaded X-Ray", use_container_width=True)
                
                # Analysis button
                if st.button("🔍 Analyze X-Ray", type="primary"):
                    with st.spinner("🩻 Analyzing X-Ray image... This may take a few seconds."):
                        results = analyze_xray(uploaded)
                        
                        if results:
                            st.success("✅ Analysis complete!")
                            st.session_state.xray_results = results
                        else:
                            st.error("❌ Failed to analyze image. Please try again.")
            
            with col2:
                if 'xray_results' in st.session_state:
                    display_xray_results(st.session_state.xray_results)

# [Rest of your tabs remain the same...]
with tabs[0]:
    st.header("Welcome to HealthAI")
    st.write("Your AI-powered healthcare assistant.")

    st.subheader("Chat with HealthAI")
    st.info("Voice + Text medical assistant")

with tabs[1]:
    st.header("Disease Encyclopedia")
    search = st.text_input("Search for any condition...")
    if search:
        st.write(f"Searching for: {search}")

with tabs[3]:
    st.header("Book an Appointment")
    date = st.date_input("Select Date")
    time = st.time_input("Select Time")
    st.button("Confirm Booking")

with tabs[4]:
    st.header("Find a Doctor")
    specialty = st.selectbox("Choose specialty", [
        "Bones", "Heart", "Neurology", "Dentist", "Dermatology"
    ])
    st.write(f"Showing doctors for: **{specialty}**")

with tabs[5]:
    st.header("Clinic & Hospital Map")
    user_need = st.text_input("What specialty do you need?")
    if st.button("Search Clinics"):
        st.write(f"Searching for clinics specialized in: {user_need}")

with tabs[6]:
    st.header("About HealthAI")
    st.write("We use AI to revolutionize healthcare.")