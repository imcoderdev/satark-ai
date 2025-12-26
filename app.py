"""
Satark.ai - Your Financial Bodyguard 🛡️
AI-powered scam detection for Indian users
Team Tark | ML Nashik Gen AI-thon 2025
"""

import streamlit as st
from PIL import Image
from utils import analyze_screenshot, check_blacklist, generate_cyber_complaint
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

# 3-Step Visual Flow - High Contrast
st.markdown("""
<div style='background: linear-gradient(90deg, #1565c0, #7b1fa2, #2e7d32); 
            padding: 1rem 2rem; border-radius: 12px; text-align: center; 
            margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.2);'>
    <span style='font-size: 1.4rem; font-weight: 600; color: white; letter-spacing: 0.5px;'>
        📸 Upload &nbsp;&nbsp;➡️&nbsp;&nbsp; 🧠 AI Analysis &nbsp;&nbsp;➡️&nbsp;&nbsp; 🛡️ Safety Advice
    </span>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "WhatsApp/SMS ka screenshot yahan daalo",
    type=["png", "jpg", "jpeg"],
    help="Supported formats: PNG, JPG, JPEG",
    key="file_uploader"
)

# Track if a new file was uploaded (reset analysis)
if "last_uploaded_file" not in st.session_state:
    st.session_state.last_uploaded_file = None

if uploaded_file is not None:
    # Check if this is a new file (different from last analyzed)
    current_file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    if st.session_state.last_uploaded_file != current_file_id:
        # New file uploaded - reset analysis
        st.session_state.analysis_result = None
        st.session_state.last_uploaded_file = current_file_id
    
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
    
    # Analyze Button - only triggers analysis, results shown from session state
    if st.button("🔍 Analyze Karo!", type="primary", use_container_width=True, key="analyze_btn"):
        
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
            
            # Store result in session state for persistence
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
    
    # Display Results from Session State (persists across reruns)
    if st.session_state.analysis_result is not None:
        result = st.session_state.analysis_result
        
        # Display Results with Tabs
        st.header("🤖 Autonomous Agent Decision")
        
        # Create tabs for different views
        citizen_tab, dev_tab = st.tabs(["🛡️ Citizen View", "🛠️ Developer/Debug View"])
        
        # ==================== CITIZEN VIEW ====================
        with citizen_tab:
            # Verdict Display
            risk_score = result.get("risk_score", 0)
            verdict = result.get("verdict", "UNKNOWN")
            
            # Main Alert Box (Professional)
            if verdict == "SAFE":
                st.balloons()
                st.markdown("""
                <div style='background: linear-gradient(135deg, #00c853, #69f0ae); 
                            color: white; padding: 2rem; border-radius: 15px; 
                            text-align: center; margin: 1rem 0;
                            box-shadow: 0 4px 15px rgba(0,200,83,0.4);'>
                    <h1 style='margin:0; font-size: 3rem;'>✅ SAFE</h1>
                    <p style='font-size: 1.3rem; margin-top: 0.5rem;'>This content appears to be legitimate.</p>
                </div>
                """, unsafe_allow_html=True)
                # Desi Note - separate from professional alert
                st.info("💬 **Desi Note:** _Yeh legit lagta hai, tension mat le bhai!_")
                
            elif verdict == "SUSPICIOUS":
                st.markdown("""
                <div style='background: linear-gradient(135deg, #ff9800, #ffb74d); 
                            color: white; padding: 2rem; border-radius: 15px; 
                            text-align: center; margin: 1rem 0;
                            box-shadow: 0 4px 15px rgba(255,152,0,0.4);'>
                    <h1 style='margin:0; font-size: 3rem;'>⚠️ SUSPICIOUS</h1>
                    <p style='font-size: 1.3rem; margin-top: 0.5rem;'>This content has some red flags. Proceed with caution.</p>
                </div>
                """, unsafe_allow_html=True)
                # Desi Note
                st.warning("💬 **Desi Note:** _Thoda shak hai... Sambhal ke re bhai!_")
                
            else:  # SCAM
                st.markdown("""
                <div style='background: linear-gradient(135deg, #d32f2f, #f44336); 
                            color: white; padding: 2rem; border-radius: 15px; 
                            text-align: center; margin: 1rem 0;
                            box-shadow: 0 8px 25px rgba(211,47,47,0.5);
                            animation: pulse 1s infinite;'>
                    <h1 style='margin:0; font-size: 3.5rem;'>🚨 SCAM DETECTED! 🚨</h1>
                    <p style='font-size: 1.5rem; margin-top: 0.5rem; font-weight: bold;'>
                        This is a confirmed fraudulent message. Do NOT engage!
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
                # Desi Note - the savage advice
                st.markdown("""
                > 💬 **Desi Big Brother Says:**  
                > _"BHAAG JA YAHAN SE! Yeh 100% fraud hai! Isko block kar aur cyber cell mein report kar!"_
                """)
                
                # Recommended Actions - Quick Action Buttons
                st.markdown("#### ⚡ Recommended Actions")
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                
                with btn_col1:
                    st.button("🚫 Block Sender", type="primary", use_container_width=True, key="btn_block", disabled=True)
                    st.caption("_Coming soon_")
                
                with btn_col2:
                    st.button("🗑️ Delete Message", use_container_width=True, key="btn_delete", disabled=True)
                    st.caption("_Coming soon_")
                
                with btn_col3:
                    st.button("📞 Call 1930", use_container_width=True, key="btn_report", disabled=True)
                    st.caption("_Cyber Helpline_")
                
                # Legal Action - Generate Cyber Complaint PDF (Direct Download)
                st.divider()
                st.markdown("#### 📝 Legal Action - Draft Official Complaint")
                
                # Generate PDF directly and show download button
                entities = result.get("extracted_entities", {})
                scam_details = {
                    "scam_type": result.get("scam_type", "Financial Fraud"),
                    "phone_number": entities.get("phone_number"),
                    "company_name": entities.get("company_name"),
                    "amount": entities.get("amount"),
                    "extracted_text": result.get("reasoning", ""),
                    "risk_score": result.get("risk_score", 0),
                    "red_flags": result.get("red_flags", []),
                    "reasoning": result.get("reasoning", "")
                }
                
                # Generate PDF on demand
                pdf_bytes = generate_cyber_complaint(scam_details)
                pdf_filename = f"Cyber_Complaint_{datetime.now().strftime('%Y%m%d')}.pdf"
                
                st.download_button(
                    label="👮 Download Cyber Complaint PDF",
                    data=pdf_bytes,
                    file_name=pdf_filename,
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary",
                    key="download_complaint"
                )
                st.caption("_📄 Ready-to-file complaint for cybercrime.gov.in_")
            
            st.divider()
            
            # Visual Risk Meter with Color-Coded Metric
            st.subheader("📊 Risk Meter")
            
            meter_score = result.get("risk_score", 50)
            
            # Color-coded risk level
            if meter_score < 20:
                risk_label = "🟢 Low Risk (Safe)"
                risk_color = "#00c853"
                delta_text = "You're safe!"
            elif meter_score <= 80:
                risk_label = "🟡 Medium Risk (Caution)"
                risk_color = "#ff9800"
                delta_text = "Proceed carefully"
            else:
                risk_label = "🔴 High Risk (Critical Alert)"
                risk_color = "#d32f2f"
                delta_text = "Danger zone!"
            
            # Display metric with styled container
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, {risk_color}22, {risk_color}11); 
                        border: 2px solid {risk_color}; border-radius: 15px; 
                        padding: 1.5rem; text-align: center; margin: 0.5rem 0;'>
                <p style='font-size: 1rem; color: #666; margin: 0;'>Scam Probability</p>
                <h1 style='font-size: 3rem; color: {risk_color}; margin: 0.3rem 0;'>{meter_score}%</h1>
                <p style='font-size: 1.2rem; font-weight: bold; color: {risk_color}; margin: 0;'>{risk_label}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Progress bar for visual effect
            st.progress(min(meter_score, 100) / 100)
            
            # "Why?" box with top 3 red flags
            red_flags = result.get("red_flags", [])
            if red_flags:
                top_flags = red_flags[:3]  # Get top 3
                flags_text = " • ".join(top_flags)
                st.caption(f"❓ **Why?** {flags_text}")
            else:
                if meter_score < 20:
                    st.caption("❓ **Why?** No red flags detected. Content appears legitimate.")
                else:
                    st.caption("❓ **Why?** AI detected potential risk patterns in the content.")
            
            # Show scam type if detected
            scam_type = result.get("scam_type", "N/A")
            if scam_type and scam_type not in ["N/A", "None", "null"] and verdict != "SAFE":
                st.markdown(f"<p style='text-align: center; color: #666; font-size: 1rem; margin-top: 0.5rem;'>🏷️ Detected Type: <b>{scam_type}</b></p>", unsafe_allow_html=True)
            
            st.divider()
            
            # Actionable Advice Section
            st.subheader("💡 What Should You Do?")
            
            hinglish = result.get("hinglish_advice", result.get("action", "Sambhal ke reh bhai!"))
            
            if verdict == "SCAM":
                st.error(f"🚫 **Immediate Action Required:** {hinglish}")
                st.markdown("""
                **Recommended Steps:**
                1. 🚫 Block this number/sender immediately
                2. 🗑️ Delete the message/app
                3. 📞 Report to Cyber Cell: **1930** (National Helpline)
                4. ⚠️ Warn your family and friends
                """)
            elif verdict == "SUSPICIOUS":
                st.warning(f"⚠️ **Caution:** {hinglish}")
                st.markdown("""
                **Recommended Steps:**
                1. 🔍 Verify the sender through official channels
                2. 🚫 Do NOT share OTP or personal details
                3. 📱 Check official app/website directly
                """)
            else:
                st.success(f"✅ **All Clear:** {hinglish}")
            
            # Red flags summary for citizens
            if result.get("red_flags"):
                with st.expander("🚩 Red Flags Detected", expanded=False):
                    for flag in result["red_flags"]:
                        st.write(f"• {flag}")
            
            # Local Impact Footer
            st.divider()
            st.markdown("<p style='text-align: center; color: #888; font-size: 0.9rem;'>🌐 <b>Hindi / Marathi support coming soon</b> — Apni boli mein suraksha!</p>", unsafe_allow_html=True)
        
        # ==================== DEVELOPER VIEW ====================
        with dev_tab:
            st.markdown("#### 🔬 Gemini API Response (Single Source of Truth)")
            
            # Build the trace data from actual analysis
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
            
            st.markdown("#### 📜 System Trace / Execution Log")
            
            # Generate real execution log
            timestamp = st.session_state.scan_timestamp or datetime.now().isoformat()
            latency = result.get("latency_ms", 0)
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
            
            for flag in red_flags[:3]:
                log_lines.append(f"[{timestamp}] WARN  - Red flag detected: {flag}")
            
            if verdict == "SCAM":
                log_lines.append(f"[{timestamp}] ERROR - 🚨 SCAM DETECTED! Type: {scam_type}")
            elif verdict == "SUSPICIOUS":
                log_lines.append(f"[{timestamp}] WARN  - ⚠️ Suspicious activity detected")
            else:
                log_lines.append(f"[{timestamp}] INFO  - ✅ Content appears safe")
            
            log_lines.append(f"[{timestamp}] INFO  - Final verdict: {verdict} (Risk: {risk_score}/100)")
            log_lines.append(f"[{timestamp}] INFO  - Analysis complete. Scan ID: {st.session_state.scan_id}")
            
            st.code("\n".join(log_lines), language="log")
            
            # Performance metrics
            st.markdown("#### ⚡ Performance Metrics")
            col1, col2, col3 = st.columns(3)
            with col1:
                latency_sec = latency / 1000 if latency else 0
                st.metric("⏱️ Latency", f"{latency_sec:.2f}s")
            with col2:
                st.metric("🧠 Model", result.get('model', 'gemini-2.5-flash'))
            with col3:
                st.metric("📊 Parse", "Success ✅" if parse_success else "Fallback ⚠️")
            
            # Extracted Entities
            st.markdown("#### 📝 Extracted Entities")
            extracted = result.get("extracted_entities", result.get("extracted_info", {}))
            if extracted and any(v for v in extracted.values() if v):
                entity_data = {k: v for k, v in extracted.items() if v}
                st.json(entity_data)
            else:
                st.info("No entities extracted from this image.")
            
            # Technical reasoning
            st.markdown("#### 🔬 Technical Analysis")
            st.code(result.get("reasoning", "N/A"), language="text")
            
            # Raw response if parsing failed
            if not parse_success and result.get("raw_response"):
                st.markdown("#### ⚠️ Raw API Response (Parse Failed)")
                st.code(result.get("raw_response", ""), language="text")
            
            st.caption(f"_Agent trace exported for audit compliance. Session ID: {st.session_state.scan_id}_")

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
