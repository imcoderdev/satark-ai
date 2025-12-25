"""
Satark.ai - Your Financial Bodyguard 🛡️
AI-powered scam detection for Indian users
Team Tark | ML Nashik Gen AI-thon 2025
"""

import streamlit as st
from PIL import Image
from utils import analyze_screenshot, check_blacklist
import uuid
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Satark.ai - Scam Detector",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize session state for storing analysis results
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "scan_id" not in st.session_state:
    st.session_state.scan_id = None
if "scan_timestamp" not in st.session_state:
    st.session_state.scan_timestamp = None

# Custom CSS for clean, trustworthy look
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
    }
    .verdict-safe {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .verdict-suspicious {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .verdict-scam {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .stButton > button {
        width: 100%;
        background-color: #2E86AB;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<div class='main-header'>", unsafe_allow_html=True)
st.title("🛡️ Satark.ai")
st.subheader("Tera Apna Financial Bodyguard")
st.caption("Upload karo screenshot, hum batayenge real hai ya scam! 💪")
st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# API Key Input (Sidebar)
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Check if API key is set in environment
    import os
    env_key_set = bool(os.getenv("GEMINI_API_KEY"))
    
    if env_key_set:
        st.success("✅ API Key loaded from .env file!")
        api_key = None  # Will use env var in utils.py
    else:
        api_key = st.text_input(
            "Google Gemini API Key",
            type="password",
            help="Or set GEMINI_API_KEY in .env file"
        )
        if api_key:
            st.success("API Key configured! ✅")
        else:
            st.info("💡 Tip: Add GEMINI_API_KEY to .env file")

# Main Upload Section
st.header("📸 Screenshot Upload Karo")

uploaded_file = st.file_uploader(
    "WhatsApp/SMS ka screenshot yahan daalo",
    type=["png", "jpg", "jpeg"],
    help="Supported formats: PNG, JPG, JPEG"
)

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.image(image, caption="Uploaded Screenshot", use_container_width=True)
    
    with col2:
        st.info("📋 **Image Details**")
        st.write(f"**File:** {uploaded_file.name}")
        st.write(f"**Size:** {uploaded_file.size / 1024:.1f} KB")
        st.write(f"**Dimensions:** {image.size[0]} x {image.size[1]}")
    
    st.divider()
    
    # Analyze Button
    if st.button("🔍 Analyze Karo!", type="primary", use_container_width=True):
        
        # Generate scan ID and timestamp
        st.session_state.scan_id = f"SATARK-{str(uuid.uuid4())[:8].upper()}"
        st.session_state.scan_timestamp = datetime.now().isoformat()
        
        # Use st.status for detailed progress
        with st.status("🤖 Satark Agent Activated...", expanded=True) as status:
            st.write("📷 Screenshot received...")
            st.write("🔍 Extracting text using OCR...")
            st.write("🧠 Analyzing with Gemini AI...")
            st.write("🔎 Checking against scam database...")
            
            # Call the analysis function (uses default API key if none provided)
            result = analyze_screenshot(image, api_key if api_key else None)
            
            # Store result in session state for Debug Mode
            st.session_state.analysis_result = result
            
            verdict = result.get("verdict", "UNKNOWN")
            if verdict == "SCAM":
                status.update(label="🚨 SCAM DETECTED!", state="error", expanded=False)
            elif verdict == "SUSPICIOUS":
                status.update(label="⚠️ Analysis Complete - Suspicious!", state="running", expanded=False)
            elif verdict == "SAFE":
                status.update(label="✅ Analysis Complete - Safe!", state="complete", expanded=False)
            else:
                status.update(label="📊 Analysis Complete", state="complete", expanded=False)
        
        # Display Results
        st.header("📊 Analysis Result")
        
        # Verdict Display
        risk_score = result.get("risk_score", 0)
        
        # Show balloons for SAFE verdict
        if verdict == "SAFE":
            st.balloons()
            st.markdown("""
            <div style='background: linear-gradient(135deg, #00c853, #69f0ae); 
                        color: white; padding: 2rem; border-radius: 15px; 
                        text-align: center; margin: 1rem 0;
                        box-shadow: 0 4px 15px rgba(0,200,83,0.4);'>
                <h1 style='margin:0; font-size: 3rem;'>✅ SAFE</h1>
                <p style='font-size: 1.3rem; margin-top: 0.5rem;'>Yeh legit lagta hai, tension mat le bhai!</p>
            </div>
            """, unsafe_allow_html=True)
            
        elif verdict == "SUSPICIOUS":
            st.markdown("""
            <div style='background: linear-gradient(135deg, #ff9800, #ffb74d); 
                        color: white; padding: 2rem; border-radius: 15px; 
                        text-align: center; margin: 1rem 0;
                        box-shadow: 0 4px 15px rgba(255,152,0,0.4);'>
                <h1 style='margin:0; font-size: 3rem;'>⚠️ SUSPICIOUS</h1>
                <p style='font-size: 1.3rem; margin-top: 0.5rem;'>Thoda shak hai... Sambhal ke re!</p>
            </div>
            """, unsafe_allow_html=True)
            
        else:  # SCAM
            st.markdown("""
            <div style='background: linear-gradient(135deg, #d32f2f, #f44336); 
                        color: white; padding: 2rem; border-radius: 15px; 
                        text-align: center; margin: 1rem 0;
                        box-shadow: 0 8px 25px rgba(211,47,47,0.5);
                        animation: pulse 1s infinite;'>
                <h1 style='margin:0; font-size: 3.5rem;'>🚨 SCAM ALERT! 🚨</h1>
                <p style='font-size: 1.5rem; margin-top: 0.5rem; font-weight: bold;'>
                    BHAAG JA YAHAN SE! YEH 100% FRAUD HAI!
                </p>
            </div>
            <style>
                @keyframes pulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.02); }
                    100% { transform: scale(1); }
                }
            </style>
            """, unsafe_allow_html=True)
            st.error("⛔ DANGER: Do NOT share any OTP, PIN, or bank details!")
        
        st.divider()
        
        # Risk Score Metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Color based on risk
            delta_color = "inverse" if risk_score < 50 else "normal"
            st.metric(
                label="🎯 Risk Score",
                value=f"{risk_score}/100",
                delta=f"{'Low' if risk_score < 30 else 'Medium' if risk_score < 70 else 'High'} Risk",
                delta_color=delta_color
            )
        
        with col2:
            st.metric(
                label="📋 Verdict",
                value=verdict,
                delta=None
            )
        
        with col3:
            blacklisted = "YES 🚫" if result.get("blacklisted_entity") else "NO ✅"
            st.metric(
                label="🗃️ Blacklisted",
                value=blacklisted,
                delta=None
            )
        
        # Visual Risk Meter - Use actual risk_score from API
        st.subheader("📊 Visual Risk Meter")
        
        # Use actual risk score from API response
        meter_score = result.get("risk_score", 50)
        
        # Progress bar for risk
        st.progress(min(meter_score, 100) / 100)
        
        # Caption with color based on risk
        if meter_score >= 70:
            st.markdown(f"<p style='text-align: center; color: #d32f2f; font-weight: bold; font-size: 1.2rem;'>🚨 Scam Probability: {meter_score}%</p>", unsafe_allow_html=True)
        elif meter_score >= 40:
            st.markdown(f"<p style='text-align: center; color: #ff9800; font-weight: bold; font-size: 1.2rem;'>⚠️ Scam Probability: {meter_score}%</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='text-align: center; color: #00c853; font-weight: bold; font-size: 1.2rem;'>✅ Scam Probability: {meter_score}%</p>", unsafe_allow_html=True)
        
        # Show scam type if detected
        scam_type = result.get("scam_type", "N/A")
        if scam_type and scam_type != "N/A" and scam_type != "None" and verdict != "SAFE":
            st.markdown(f"<p style='text-align: center; color: #666; font-size: 1rem;'>🏷️ Detected Type: <b>{scam_type}</b></p>", unsafe_allow_html=True)
        
        st.divider()
        
        # Detailed Analysis
        st.subheader("🔎 Detailed Analysis")
        
        with st.expander("See Full Report", expanded=True):
            # Technical reasoning
            st.write("**🔬 Technical Analysis:**")
            st.info(result.get("reasoning", "N/A"))
            
            # Hinglish advice (the savage Desi Big Brother advice)
            st.write("**💪 Desi Big Brother Says:**")
            hinglish = result.get("hinglish_advice", result.get("action", "Sambhal ke reh bhai!"))
            st.warning(hinglish)
            
            # Extracted Info - use new field name
            extracted = result.get("extracted_entities", result.get("extracted_info", {}))
            if extracted and any(extracted.values()):
                st.write("**📝 Extracted Information:**")
                if extracted.get("company_name"):
                    st.write(f"• Company: `{extracted['company_name']}`")
                if extracted.get("phone_number"):
                    st.write(f"• Phone: `{extracted['phone_number']}`")
                if extracted.get("amount"):
                    st.write(f"• Amount: `{extracted['amount']}`")
                if extracted.get("upi_id"):
                    st.write(f"• UPI ID: `{extracted['upi_id']}`")
                if extracted.get("url"):
                    st.write(f"• URL: `{extracted['url']}`")
            
            if result.get("red_flags"):
                st.write("**🚩 Red Flags Found:**")
                for flag in result["red_flags"]:
                    st.error(f"• {flag}")
            
            # Show scam type badge
            scam_type = result.get("scam_type", "N/A")
            if scam_type and scam_type not in ["N/A", "None", "null"] and verdict != "SAFE":
                st.markdown(f"""
                <div style='background: #1a1a2e; color: #ff6b6b; padding: 0.8rem; 
                            border-radius: 8px; text-align: center; 
                            border: 2px solid #ff6b6b; margin-top: 1rem;'>
                    <b>🏷️ Scam Category: {scam_type}</b>
                </div>
                """, unsafe_allow_html=True)
            
            if result.get("blacklisted_entity"):
                st.markdown("""
                <div style='background: #000; color: #ff0000; padding: 1rem; 
                            border-radius: 10px; text-align: center; 
                            border: 3px solid #ff0000; margin-top: 1rem;'>
                    <h3>🚫 BLACKLISTED ENTITY DETECTED! 🚫</h3>
                    <p>This entity is in our scam database!</p>
                </div>
                """, unsafe_allow_html=True)

else:
    # Empty state
    st.info("👆 Screenshot upload karo analysis shuru karne ke liye!")
    
    # Sample use cases
    st.subheader("🎯 Yeh App Kab Use Karna Hai?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 💰")
        st.write("**Loan App Messages**")
        st.caption("Jab koi loan offer kare random message se")
    
    with col2:
        st.markdown("### 🎰")
        st.write("**Lottery Scams**")
        st.caption("'Aapne 50 lakh jeete!' wale messages")
    
    with col3:
        st.markdown("### 👮")
        st.write("**Digital Arrest**")
        st.caption("Fake police/CBI threat calls")

# Debug Mode - Agent Logic Viewer (Real Data - Single Source of Truth! 🏆)
st.divider()
with st.expander("🛠️ View Agent Logic (Debug Mode)", expanded=False):
    
    # Check if we have analysis results
    if st.session_state.analysis_result is not None:
        result = st.session_state.analysis_result
        
        st.markdown("#### 🔬 Gemini API Response (Single Source of Truth)")
        
        # Build the real trace data from actual analysis
        trace_data = {
            "scan_id": st.session_state.scan_id,
            "timestamp": st.session_state.scan_timestamp,
            "verdict": result.get("verdict", "N/A"),
            "risk_score": result.get("risk_score", 0),
            "scam_type": result.get("scam_type", "N/A"),
            "extracted_entities": result.get("extracted_entities", {}),
            "red_flags": result.get("red_flags", []),
            "reasoning": result.get("reasoning", "N/A"),
            "hinglish_advice": result.get("hinglish_advice", "N/A"),
            "model": result.get("model", "gemini-2.5-flash"),
            "latency_ms": result.get("latency_ms", 0),
            "parse_success": result.get("parse_success", False)
        }
        
        st.json(trace_data)
        
        st.markdown("#### 📜 Execution Log")
        
        # Generate real execution log based on actual data
        timestamp = st.session_state.scan_timestamp or datetime.now().isoformat()
        latency = result.get("latency_ms", 0)
        verdict = result.get("verdict", "UNKNOWN")
        risk_score = result.get("risk_score", 0)
        scam_type = result.get("scam_type", "N/A")
        parse_success = result.get("parse_success", False)
        red_flags = result.get("red_flags", [])
        
        log_lines = [
            f"[{timestamp}] INFO  - Satark.ai Agent initialized",
            f"[{timestamp}] INFO  - Image received, starting analysis...",
            f"[{timestamp}] INFO  - Sending to Gemini 2.5 Flash API...",
            f"[{timestamp}] INFO  - API response received in {latency}ms",
            f"[{timestamp}] {'INFO ' if parse_success else 'WARN '} - JSON parse: {'SUCCESS' if parse_success else 'FALLBACK MODE'}",
        ]
        
        # Add red flag detections
        for flag in red_flags[:3]:  # Limit to 3 for readability
            log_lines.append(f"[{timestamp}] WARN  - Red flag detected: {flag}")
        
        if verdict == "SCAM":
            log_lines.append(f"[{timestamp}] ERROR - 🚨 SCAM DETECTED! Type: {scam_type}")
        elif verdict == "SUSPICIOUS":
            log_lines.append(f"[{timestamp}] WARN  - ⚠️ Suspicious activity detected")
        else:
            log_lines.append(f"[{timestamp}] INFO  - ✅ Content appears safe")
        
        log_lines.append(f"[{timestamp}] INFO  - Final verdict: {verdict} (Risk: {risk_score}/100)")
        log_lines.append(f"[{timestamp}] INFO  - Analysis complete. Scan ID: {st.session_state.scan_id}")
        
        real_log = "\n".join(log_lines)
        st.code(real_log, language="log")
        
        # Performance metrics - REAL DATA
        col1, col2, col3 = st.columns(3)
        with col1:
            latency_sec = latency / 1000 if latency else 0
            st.info(f"⏱️ **Latency:** {latency_sec:.2f}s")
        with col2:
            st.info(f"🧠 **Model:** {result.get('model', 'gemini-2.5-flash')}")
        with col3:
            status_icon = "✅" if parse_success else "⚠️"
            st.info(f"{status_icon} **Parse:** {'Success' if parse_success else 'Fallback'}")
        
        # Show raw response if parsing failed
        if not parse_success and result.get("raw_response"):
            st.markdown("#### ⚠️ Raw API Response (Parse Failed)")
            st.code(result.get("raw_response", ""), language="text")
        
        st.caption(f"_Agent trace exported for audit compliance. Session ID: {st.session_state.scan_id}_")
        
    else:
        st.info("📷 Upload and analyze a screenshot to see real agent logs here!")
        st.caption("Debug Mode shows the actual Gemini API response - no fake data!")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; padding: 2rem 0;'>
    <p style='color: #888; font-size: 0.9rem; font-style: italic; margin-bottom: 0.5rem;'>
        "Apni mehnat ka paisa hai, aise mat udaao." - Satark.ai
    </p>
    <p style='color: #888; font-size: 0.85rem; margin-bottom: 0.3rem;'>
        Made with ❤️ by Team Tark
    </p>
    <p style='color: #aaa; font-size: 0.75rem;'>
        © 2025 Satark.ai | ML Nashik Gen AI-thon
    </p>
    <p style='color: #aaa; font-size: 0.7rem; margin-top: 0.5rem;'>
        ⚠️ Disclaimer: Yeh tool sirf awareness ke liye hai. Legal advice ke liye proper authorities se contact karo.
    </p>
</div>
""", unsafe_allow_html=True)
