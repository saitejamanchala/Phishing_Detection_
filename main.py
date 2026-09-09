import streamlit as st
import requests
from feature_extractor import extract_url_features

# MUST BE THE FIRST STREAMLIT COMMAND EXECUTED
st.set_page_config(
    page_title="Phishing URL Detector", 
    page_icon="🛡️", 
    layout="wide"
)

# Custom CSS Injection for Modern Cards & Styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .safe-card {
        background-color: #0e2a1f;
        padding: 24px;
        border-radius: 12px;
        border-left: 6px solid #00c853;
        margin-bottom: 20px;
    }
    .danger-card {
        background-color: #3b1111;
        padding: 24px;
        border-radius: 12px;
        border-left: 6px solid #ff1744;
        margin-bottom: 20px;
    }
    .result-title {
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 8px;
    }
    .result-desc {
        color: #d1d5db;
        font-size: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Header Section
st.title("🛡️ Real-Time Phishing Detector")
st.caption("AI-powered threat analysis powered by Random Forest classification")

st.markdown("---")

# Input Area
col_input, col_btn = st.columns([4, 1])

with col_input:
    url_input = st.text_input("Target URL", placeholder="https://example.com", label_visibility="collapsed")

with col_btn:
    analyze_btn = st.button("Analyze URL", use_container_width=True, type="primary")

# Analysis & Result Processing
if analyze_btn:
    if not url_input.strip():
        st.warning("Please enter a valid URL.")
    else:
        with st.spinner("Analyzing structural indicators..."):
            try:
                # Extract features locally
                extracted_dict = extract_url_features(url_input)
                
                # POST to FastAPI
                response = requests.post(
                    "http://127.0.0.1:8000/predict",
                    json={"features": extracted_dict}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    is_phishing = data["prediction"] == 1
                    confidence = data["confidence"] * 100
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Display Visual Cards
                    if is_phishing:
                        st.markdown(f"""
                            <div class="danger-card">
                                <div class="result-title">🚨 Warning: Malicious / Phishing URL Detected</div>
                                <div class="result-desc">This website exhibits high-risk indicators associated with deceptive websites.</div>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div class="safe-card">
                                <div class="result-title">✅ Safe: Legitimate URL Identified</div>
                                <div class="result-desc">Structural analysis shows no immediate phishing patterns detected.</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    # Metrics Display
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Classification", data["label"])
                    m2.metric("Confidence Score", f"{confidence:.2f}%")
                    m3.metric("Features Analyzed", len(extracted_dict))

                else:
                    st.error(f"API Error {response.status_code}: {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to FastAPI server. Ensure `app.py` is running on port 8000.")