import streamlit as st
import pandas as pd
import joblib
from feature_extractor import extract_url_features

# 1. Streamlit Page Config (MUST BE FIRST)
st.set_page_config(
    page_title="Phishing URL Detector", 
    page_icon="🛡️", 
    layout="wide"
)

# 2. Cache Model Artifacts for fast inference
@st.cache_resource
def load_artifacts():
    model = joblib.load("phishing_model.pkl")
    selected_features = joblib.load("selected_features.pkl")
    return model, selected_features

model, selected_features = load_artifacts()

# 3. Custom CSS Injection
st.markdown("""
    <style>
    .main { padding: 2rem; }
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
    .result-title { font-size: 22px; font-weight: bold; margin-bottom: 8px; }
    .result-desc { color: #d1d5db; font-size: 15px; }
    </style>
""", unsafe_allow_html=True)

# 4. Header Section
st.title("🛡️ Real-Time Phishing Detector")
st.caption("AI-powered threat analysis powered by Random Forest classification")
st.markdown("---")

# 5. Input Layout
col_input, col_btn = st.columns([4, 1])

with col_input:
    url_input = st.text_input("Target URL", placeholder="https://example.com", label_visibility="collapsed")

with col_btn:
    analyze_btn = st.button("Analyze URL", use_container_width=True, type="primary")

# 6. Direct Model Inference
if analyze_btn:
    if not url_input.strip():
        st.warning("Please enter a valid URL.")
    else:
        with st.spinner("Extracting features and classifying..."):
            try:
                # Extract URL features
                extracted_dict = extract_url_features(url_input)
                
                # Fill missing schema values safely
                for feat in selected_features:
                    if feat not in extracted_dict:
                        extracted_dict[feat] = 0

                # Reorder columns to match selected_features.pkl
                df_input = pd.DataFrame([extracted_dict])[selected_features]

                # Run predictions directly
                prediction = model.predict(df_input)[0]
                probs = model.predict_proba(df_input)[0]
                
                is_phishing = prediction == 1
                confidence = float(max(probs)) * 100
                label = "Phishing" if is_phishing else "Legitimate"

                st.markdown("<br>", unsafe_allow_html=True)

                # Render Results
                if is_phishing:
                    st.markdown("""
                        <div class="danger-card">
                            <div class="result-title">🚨 Warning: Malicious / Phishing URL Detected</div>
                            <div class="result-desc">This website exhibits high-risk indicators associated with deceptive websites.</div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                        <div class="safe-card">
                            <div class="result-title">✅ Safe: Legitimate URL Identified</div>
                            <div class="result-desc">Structural analysis shows no immediate phishing patterns detected.</div>
                        </div>
                    """, unsafe_allow_html=True)

                m1, m2, m3 = st.columns(3)
                m1.metric("Classification", label)
                m2.metric("Confidence Score", f"{confidence:.2f}%")
                m3.metric("Features Analyzed", len(selected_features))

            except Exception as e:
                st.error(f"Inference Error: {str(e)}")