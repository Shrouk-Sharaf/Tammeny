import streamlit as st
import os
import requests
import json
from PIL import Image
import io
import base64

st.markdown("""
<style>
    /* Your existing CSS styles remain the same */
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    
    /* Add chatbot specific styles */
    .chatbot-container {
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
        overflow: hidden;
    }
    
    .chatbot-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        text-align: center;
        font-weight: 600;
    }
    
    .chatbot-frame {
        width: 100%;
        height: 500px;
        border: none;
        background: #f8f9fa;
    }
    
    /* Rest of your existing CSS remains the same */
    .logo-container {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        overflow: hidden;
        border: 4px solid #667eea;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: center;
        background: white;
        transition: all 0.3s ease;
    }
    
    .logo-container:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        border-color: #764ba2;
    }
    
    .logo-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
        border-radius: 50%;
    }
    
    .logo-placeholder {
        width: 100%;
        height: 100%;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        transition: transform 0.3s ease;
        height: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .team-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        transition: all 0.3s ease;
        border: 1px solid #e0e0e0;
        height: 100%;
    }
    
    .team-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    .status-healthy {
        background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 600;
        text-align: center;
    }
    
    .status-unhealthy {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 600;
        text-align: center;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #f8f9fa;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        border: 1px solid #e0e0e0;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    .mission-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    
    .disclaimer-box {
        background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
        color: #2c3e50;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #e74c3c;
        margin: 1rem 0;
    }
    
    .finding-high {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .finding-medium {
        background: linear-gradient(135deg, #feca57 0%, #ff9ff3 100%);
        color: #2c3e50;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .finding-low {
        background: linear-gradient(135deg, #48dbfb 0%, #1dd1a1 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .image-container {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 3px solid #f8f9fa;
    }
    
    .stProgress > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

XRAY_SERVICE_URL = "http://localhost:8002"

st.set_page_config(
    page_title="Tammeny",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Your existing logo and header code remains the same
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    logo_path = "assets/logo.jpg"
    logo_found = False
    
    possible_paths = [
        "assets/logo.jpg",
        "healthcare-ai/services/streamlit-ui/assets/logo.jpg",
        "services/streamlit-ui/assets/logo.jpg",
        "logo.jpg"
    ]
    
    logo_path = None
    for path in possible_paths:
        if os.path.exists(path):
            logo_path = path
            break
    
    if logo_path:
        st.markdown(f'''
        <div class="logo-container">
            <img src="data:image/jpeg;base64,{base64.b64encode(open(logo_path, "rb").read()).decode()}" class="logo-image" alt="HealthAI Logo">
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown('''
        <div class="logo-container">
            <div class="logo-placeholder">
                🏥
            </div>
        </div>
        ''', unsafe_allow_html=True)

with col2:
    st.markdown('<h1 class="main-header">Tammeny</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #7f8c8d; font-size: 1.1rem;">AI-Powered Healthcare Diagnostics & Assistance</p>', unsafe_allow_html=True)

with col3:
    st.markdown('<div style="text-align: right; padding: 1rem;">', unsafe_allow_html=True)
    if st.button("Refresh"):
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("   ")
st.markdown("   ")

# Your existing analysis functions remain the same
def analyze_xray(image_file, confidence_threshold=0.5):
    try:
        files = {"file": (image_file.name, image_file.getvalue(), image_file.type)}
        data = {"confidence_threshold": confidence_threshold}
        
        response = requests.post(
            f"{XRAY_SERVICE_URL}/analyze/xray", 
            files=files,
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Service error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Error analyzing X-Ray: {str(e)}")
        return None

def display_xray_results(results):
    # Your existing display_xray_results function remains the same
    if not results:
        st.error("No results to display")
        return
    
    st.markdown('<div class="sub-header">Diagnostic Analysis Results</div>', unsafe_allow_html=True)
    
    risk_level = results.get('overall_risk_level', 'unknown').upper()
    risk_col1, risk_col2, risk_col3 = st.columns([1, 2, 1])
    
    with risk_col2:
        if risk_level == 'HIGH':
            st.markdown('<div style="background: linear-gradient(135deg, #ff6b6b 0%, #c23616 100%); color: white; padding: 1.5rem; border-radius: 15px; text-align: center; margin: 1rem 0;">', unsafe_allow_html=True)
            st.markdown('### 🚨 HIGH RISK DETECTED')
            st.markdown('**Urgent Medical Attention Recommended**')
            st.markdown('</div>', unsafe_allow_html=True)
        elif risk_level == 'MEDIUM':
            st.markdown('<div style="background: linear-gradient(135deg, #feca57 0%, #ff9f43 100%); color: #2c3e50; padding: 1.5rem; border-radius: 15px; text-align: center; margin: 1rem 0;">', unsafe_allow_html=True)
            st.markdown('### ⚠️ MEDIUM RISK DETECTED')
            st.markdown('**Prompt Medical Evaluation Recommended**')
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="background: linear-gradient(135deg, #48dbfb 0%, #0abde3 100%); color: white; padding: 1.5rem; border-radius: 15px; text-align: center; margin: 1rem 0;">', unsafe_allow_html=True)
            st.markdown('### ✅ LOW RISK')
            st.markdown('**Routine Follow-up Recommended**')
            st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔴 High Severity Conditions")
        if 'detailed_findings' in results and 'high_severity' in results['detailed_findings']:
            high_findings = results['detailed_findings']['high_severity']
            for finding in high_findings:
                condition = finding.get('condition', 'Unknown')
                confidence = finding.get('confidence_percent', 'N/A')
                medical_advice = finding.get('medical_advice', 'Consult healthcare provider.')
                
                st.markdown(f'''
                <div class="finding-high">
                    <h4>🔴 {condition}</h4>
                    <p><strong>Confidence:</strong> {confidence}</p>
                    <p><strong>Medical Advice:</strong> {medical_advice}</p>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.markdown('<div style="background: #d5f4e6; color: #27ae60; padding: 1rem; border-radius: 10px; text-align: center;">✅ No high severity conditions detected</div>', unsafe_allow_html=True)
        
        st.markdown("#### 🟡 Medium Severity Conditions")
        if 'detailed_findings' in results and 'medium_severity' in results['detailed_findings']:
            medium_findings = results['detailed_findings']['medium_severity']
            for finding in medium_findings:
                condition = finding.get('condition', 'Unknown')
                confidence = finding.get('confidence_percent', 'N/A')
                medical_advice = finding.get('medical_advice', 'Follow-up recommended.')
                
                st.markdown(f'''
                <div class="finding-medium">
                    <h4>🟡 {condition}</h4>
                    <p><strong>Confidence:</strong> {confidence}</p>
                    <p><strong>Medical Advice:</strong> {medical_advice}</p>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.markdown('<div style="background: #e8f4fd; color: #2980b9; padding: 1rem; border-radius: 10px; text-align: center;">ℹ️ No medium severity conditions detected</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 🟢 Low Severity Conditions")
        if 'detailed_findings' in results and 'low_severity' in results['detailed_findings']:
            low_findings = results['detailed_findings']['low_severity']
            for finding in low_findings:
                condition = finding.get('condition', 'Unknown')
                confidence = finding.get('confidence_percent', 'N/A')
                medical_advice = finding.get('medical_advice', 'Routine monitoring recommended.')
                
                st.markdown(f'''
                <div class="finding-low">
                    <h4>🟢 {condition}</h4>
                    <p><strong>Confidence:</strong> {confidence}</p>
                    <p><strong>Note:</strong> {medical_advice}</p>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.markdown('<div style="background: #e8f4fd; color: #2980b9; padding: 1rem; border-radius: 10px; text-align: center;">ℹ️ No low severity conditions detected</div>', unsafe_allow_html=True)
        
        st.markdown("#### Top Findings by Confidence")
        if 'detailed_findings' in results:
            all_findings = []
            for severity_level in ['high_severity', 'medium_severity', 'low_severity']:
                if severity_level in results['detailed_findings']:
                    all_findings.extend(results['detailed_findings'][severity_level])
            
            all_findings.sort(key=lambda x: x.get('confidence', 0), reverse=True)
            
            for finding in all_findings[:5]:
                condition = finding.get('condition', 'Unknown')
                confidence = finding.get('confidence', 0)
                confidence_percent = finding.get('confidence_percent', '0%')
                
                st.write(f"**{condition}**")
                st.write(f"{confidence_percent}")
                st.progress(float(confidence))

    st.markdown("---")
    st.markdown("#### Clinical Recommendations")
    
    rec_col1, rec_col2 = st.columns(2)
    with rec_col1:
        if 'clinical_recommendations' in results and results['clinical_recommendations']:
            for i, recommendation in enumerate(results['clinical_recommendations']):
                clean_rec = recommendation.replace("**", "").replace("__", "")
                st.markdown(f'''
                <div style="background: #f8f9fa; padding: 1rem; margin: 0.5rem 0; border-radius: 10px; border-left: 4px solid #667eea;">
                    <strong>{i+1}.</strong> {clean_rec}
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("Consult with healthcare provider for personalized recommendations")

    st.markdown("---")
    meta_col1, meta_col2 = st.columns(2)
    
    with meta_col1:
        st.markdown("#### Analysis Information")
        st.markdown(f'''
        <div style="background: white; padding: 1rem; border-radius: 10px; border: 1px solid #e0e0e0;">
            <p><strong>Analysis ID:</strong> <code>{results.get('analysis_id', 'N/A')}</code></p>
            <p><strong>AI Model:</strong> {results.get('model_used', 'N/A')}</p>
            <p><strong>Analysis Time:</strong> {results.get('timestamp', 'N/A').replace('T', ' ').split('.')[0]}</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with meta_col2:
        st.markdown("#### Findings Summary")
        if 'findings_summary' in results:
            summary = results['findings_summary']
            st.markdown(f'''
            <div style="background: white; padding: 1rem; border-radius: 10px; border: 1px solid #e0e0e0;">
                <p><strong>Total Findings:</strong> {summary.get('total_findings', 0)}</p>
                <p><strong style="color: #e74c3c;">High Severity:</strong> {summary.get('high_severity', 0)}</p>
                <p><strong style="color: #f39c12;">Medium Severity:</strong> {summary.get('medium_severity', 0)}</p>
                <p><strong style="color: #27ae60;">Low Severity:</strong> {summary.get('low_severity', 0)}</p>
            </div>
            ''', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('''
    <div class="disclaimer-box">
        <h4>⚠️ Medical Disclaimer</h4>
        <p>This AI analysis is for preliminary screening only and is NOT a medical diagnosis. 
        Always consult with qualified healthcare professionals for medical decisions.</p>
    </div>
    ''', unsafe_allow_html=True)

def show_medical_disclaimer():
    st.markdown('''
    <div class="disclaimer-box">
        <h4>⚠️ Medical Disclaimer</h4>
        <ul>
            <li>This AI tool is for assistance only</li>
            <li>Not a substitute for professional medical diagnosis</li>
            <li>Always consult with qualified healthcare providers</li>
            <li>Results should be interpreted by medical professionals</li>
        </ul>
    </div>
    ''', unsafe_allow_html=True)

# CHATBOT INTEGRATION FUNCTION
def load_chatbot():
    """Load the chatbot interface"""
    try:
        # Option 1: If you have an HTML file for the chatbot
        chatbot_paths = [
            "chatbot_ui.html",
            "web/chatbot_ui.html",
            "streamlit-ui/chatbot_ui.html"
        ]
        
        chatbot_html = None
        for path in chatbot_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    chatbot_html = f.read()
                break
        
        if chatbot_html:
            st.components.v1.html(chatbot_html, height=600)
        else:
            # Option 2: If you have a chatbot service/API
            st.markdown('''
            <div class="chatbot-container">
                <div class="chatbot-header">
                    🤖 Healthcare Assistant Chatbot
                </div>
                <iframe src="http://localhost:8502/chat" class="chatbot-frame"></iframe>
            </div>
            ''', unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Error loading chatbot: {str(e)}")
        # Fallback: Simple chat interface
        st.markdown('''
        <div class="chatbot-container">
            <div class="chatbot-header">
                🤖 Healthcare Assistant Chatbot
            </div>
            <div style="padding: 2rem; text-align: center; color: #666;">
                <p>Chatbot service is currently unavailable.</p>
                <p>Please try again later or contact support.</p>
            </div>
        </div>
        ''', unsafe_allow_html=True)

tabs = st.tabs([
    "Home",
    "Medical Encyclopedia", 
    "AI Diagnostics",
    "Appointments",
    "Find Doctors",
    "Clinic Map",
    "About Us"
])

with tabs[0]:    
    st.markdown("  ")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('''
        <div class="feature-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4>AI Diagnostics</h4>
                <span style="background: #667eea; color: white; padding: 0.2rem 0.5rem; border-radius: 15px; font-size: 0.8rem;">98%</span>
            </div>
            <p>Medical image analysis</p>
            <div style="font-size: 0.9rem; color: #666;">✓ X-Ray Analysis<br>✓ MRI Processing</div>
        </div>
        ''', unsafe_allow_html=True)

    with col2:
        st.markdown('''
        <div class="feature-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4>Medical Library</h4>
                <span style="background: #4ecdc4; color: white; padding: 0.2rem 0.5rem; border-radius: 15px; font-size: 0.8rem;">10K+</span>
            </div>
            <p>Health information database</p>
            <div style="font-size: 0.9rem; color: #666;">✓ Diseases<br>✓ Treatments</div>
        </div>
        ''', unsafe_allow_html=True)

    with col3:
        st.markdown('''
        <div class="feature-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4>Find Doctors</h4>
                <span style="background: #f093fb; color: white; padding: 0.2rem 0.5rem; border-radius: 15px; font-size: 0.8rem;">500+</span>
            </div>
            <p>Specialist network</p>
            <div style="font-size: 0.9rem; color: #666;">✓ Cardiologists<br>✓ Neurologists</div>
        </div>
        ''', unsafe_allow_html=True)

    with col4:
        st.markdown('''
        <div class="feature-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4>Appointments</h4>
                <span style="background: #ff5858; color: white; padding: 0.2rem 0.5rem; border-radius: 15px; font-size: 0.8rem;">24/7</span>
            </div>
            <p>Booking system</p>
            <div style="font-size: 0.9rem; color: #666;">✓ Online Booking<br>✓ Reminders</div>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ADD CHATBOT TO HOME TAB
    st.markdown('<div class="sub-header">🤖 Healthcare Assistant</div>', unsafe_allow_html=True)
    st.markdown('<p style="color: #666; margin-bottom: 1rem;">Get instant answers to your health questions from our AI assistant</p>', unsafe_allow_html=True)
    
    # Load the chatbot
    load_chatbot()

# The rest of your tabs remain exactly the same
with tabs[1]:
    st.markdown('<div class="sub-header">Medical Encyclopedia</div>', unsafe_allow_html=True)
    search = st.text_input("🔍 Search for diseases, symptoms, or treatments...", placeholder="Enter condition name...")
    if search:
        st.write(f"Searching for: **{search}**")

with tabs[2]:
    st.markdown('<div class="sub-header">AI Diagnostic Tools</div>', unsafe_allow_html=True)
    
    show_medical_disclaimer()
    
    ai_choice = st.radio(
        "Choose Diagnostic Tool:",
        ["Prescription OCR", "Chest X-Ray Analysis"],
        horizontal=True,
        label_visibility="collapsed"
    )

    if ai_choice == "Prescription OCR":
        st.markdown("#### Prescription Analysis")
        uploaded = st.file_uploader("Upload Prescription Image", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
        if uploaded:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="image-container">', unsafe_allow_html=True)
                st.image(uploaded, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with col2:
                if st.button("Analyze Prescription", use_container_width=True):
                    with st.spinner("Processing prescription..."):
                        st.success("OCR processing complete!")

    else:
        st.markdown("#### Chest X-Ray Analysis")
        
        uploaded = st.file_uploader(
            "Upload Chest X-Ray Image", 
            type=["png", "jpg", "jpeg"],
            help="Upload a clear chest X-ray image for AI analysis",
            label_visibility="collapsed"
        )
        
        if uploaded:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### Uploaded Image")
                st.markdown('<div class="image-container">', unsafe_allow_html=True)
                st.image(uploaded, caption="Your X-Ray Image", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                if st.button("Analyze X-Ray Image", type="primary", use_container_width=True):
                    with st.spinner("🩻 Analyzing X-Ray image... This may take a few moments."):
                        results = analyze_xray(uploaded)
                        
                        if results:
                            st.success("Analysis complete!")
                            st.session_state.xray_results = results
                            st.rerun()
                        else:
                            st.error("Failed to analyze image. Please try again.")
            
            with col2:
                if 'xray_results' in st.session_state:
                    display_xray_results(st.session_state.xray_results)

with tabs[3]:
    st.markdown('<div class="sub-header">Book Medical Appointment</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Select Date")
    with col2:
        time = st.time_input("Select Time")
    if st.button("Confirm Appointment", use_container_width=True):
        st.success("Appointment booked successfully!")

with tabs[4]:
    st.markdown('<div class="sub-header">Find Healthcare Specialists</div>', unsafe_allow_html=True)
    specialty = st.selectbox("Choose medical specialty", [
        "Cardiology", "Neurology", "Orthopedics", "Dermatology", 
        "Pediatrics", "Oncology", "Psychiatry", "General Practice"
    ])
    st.write(f"Showing **{specialty}** specialists near you")

with tabs[5]:
    st.markdown('<div class="sub-header">Healthcare Facilities Map</div>', unsafe_allow_html=True)
    user_need = st.text_input("Search for clinics or hospitals...", placeholder="Enter specialty or facility name")
    if st.button("Find Healthcare Facilities", use_container_width=True):
        st.write(f"Searching for facilities specialized in: **{user_need}**")

with tabs[6]:    
    st.markdown('''
    <div class="mission-container">
        <h3>Our Mission</h3>
        <p style="font-size: 1.1rem; line-height: 1.6;">
        We leverage cutting-edge artificial intelligence to revolutionize healthcare diagnostics, 
        making advanced medical analysis accessible, accurate, and efficient for healthcare providers worldwide.
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown("  ")
    
    st.markdown("#### Our Team")
    
    team_members = [
        {
            "name": "Amr Sherif",
            "image_path": "assets/Amr.jpg",
            "linkedin": "https://www.linkedin.com/in/amrozz-sherif1",
        },
        {
            "name": "Shrouk Sharaf", 
            "image_path": "assets/Shrouk.jpeg",
            "linkedin": "https://www.linkedin.com/in/shrouk-sayed-ahmed-601b71293/",
        },
        {
            "name": "Mina Antony",
            "image_path": "assets/Mina.jpg",
            "linkedin": "https://linkedin.com/in/mina-antony",
        }
    ]
    
    team_cols = st.columns(3)
    
    for i, member in enumerate(team_members):
        with team_cols[i]:
            image_path = member["image_path"]
            with open(image_path, "rb") as img_file:
                    encoded_image = base64.b64encode(img_file.read()).decode()
                    st.markdown(f'''
                    <div class="team-card">
                        <div style="width: 120px; height: 120px; border-radius: 50%; margin: 0 auto 1rem; overflow: hidden; border: 3px solid #667eea; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);">
                            <img src="data:image/jpeg;base64,{encoded_image}" style="width: 100%; height: 100%; object-fit: cover;">
                        </div>
                        <h4 style="text-align: center;">{member['name']}</h4>
                        <a href="{member['linkedin']}" target="_blank">
                            <button style="background: #0077B5; color: white; border: none; padding: 0.5rem 1rem; border-radius: 20px; cursor: pointer; width: 100%; transition: all 0.3s ease;">
                                LinkedIn
                            </button>
                        </a>
                    </div>
                    ''', unsafe_allow_html=True)