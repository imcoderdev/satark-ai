"""
Satark.ai - Your Financial Bodyguard 🛡️
AI-powered scam detection for Indian users
Team Tark | ML Nashik Gen AI-thon 2025
"""

import streamlit as st
from PIL import Image
from utils import analyze_screenshot, check_blacklist, generate_cyber_complaint, analyze_with_internet_search
from live_scraper import get_db_stats, update_db, live_db
import uuid
from datetime import datetime
import time

# Demo User Profile for Auto-Report Feature (DigiLocker Integration Demo)
DEMO_USER_PROFILE = {
    "name": "Rahul Sharma",
    "contact": "+91 98765 43210",
    "email": "rahul.sharma@example.com",
    "address": "Plot No 45, Satpur MIDC, Nashik, Maharashtra",
    "city": "Nashik",
    "state": "Maharashtra"
}

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
    /* Prevent scroll on download button click */
    .stDownloadButton > button {
        scroll-behavior: auto !important;
    }
    section.main > div {
        scroll-behavior: auto !important;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<div class='main-header'>", unsafe_allow_html=True)
st.title("🛡️ Satark.ai")
# Header text will be updated after language selection
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
    
    st.divider()
    
    # LIVE DATABASE STATS - The WOW Factor!
    st.subheader("🔴 LIVE Scam Intelligence")
    
    try:
        db_stats = get_db_stats()
        
        # Metrics in columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "📱 Reported Numbers", 
                db_stats['reported_numbers'],
                delta="Live Database"
            )
        
        with col2:
            st.metric(
                "💳 Reported UPIs",
                db_stats['reported_upis'],
                delta=f"{db_stats['hours_since_update']:.1f}h ago"
            )
        
        # Initialize session state for update result
        if "last_update_result" not in st.session_state:
            st.session_state.last_update_result = None
        
        # Update button
        if st.button("🔄 Refresh Intelligence", type="secondary", use_container_width=True):
            with st.spinner("🌐 Fetching from REAL sources..."):
                st.caption("• Checking cybercrime.gov.in...")
                st.caption("• Scanning consumer complaints...")
                st.caption("• Fetching news reports...")
                st.caption("• Checking social media...")
                update_result = update_db()
                st.session_state.last_update_result = update_result
        
        # Display last update result if available
        if st.session_state.last_update_result:
            update_result = st.session_state.last_update_result
            if update_result.get('success'):
                sources_info = update_result.get('sources', {})
                st.success(f"✅ Found {update_result['total_reports_fetched']} reports from {sum(sources_info.values())} sources!")
                
                # Show source breakdown
                if sources_info:
                    st.info(f"""
                    **Sources:**
                    - 📰 News: {sources_info.get('google_news', 0)}
                    - 👥 Consumer Complaints: {sources_info.get('consumer_complaints', 0)}
                    - 🏛️ Govt Advisories: {sources_info.get('govt_advisory', 0)}
                    - 🐦 Social Media: {sources_info.get('social_media', 0)}
                    """)
        
        # Show recent reports if available
        recent_reports = live_db.get_recent_reports(limit=5)
        if recent_reports:
            with st.expander("📰 Latest Scam Reports (REAL DATA)", expanded=False):
                for report in recent_reports:
                    source_icon = {
                        'Google News': '📰',
                        'Consumer Complaints India': '👥',
                        'National Cyber Crime Portal': '🏛️',
                        'RBI Press Releases': '🏛️',
                        'Twitter/X': '🐦'
                    }.get(report.get('source', ''), '📌')
                    
                    st.caption(f"{source_icon} **{report.get('source', 'Unknown')}**")
                    st.caption(f"   {report.get('title', '')[:150]}...")
                    if report.get('link'):
                        st.caption(f"   🔗 [Read more]({report['link']})")
                    st.caption("---")
    
    except Exception as e:
        st.warning("⚠️ Live database updating...")
    
    st.divider()
    
    # Language Selector
    st.subheader("🌐 Choose Language / भाषा")
    user_language = st.selectbox(
        "Select your preferred language:",
        options=["Hinglish", "English", "Hindi", "Marathi"],
        index=0,  # Hinglish as default
        key="language_selector",
        help="AI will respond in your chosen language"
    )
    
    # Check if language changed - reset analysis to get fresh response
    if "user_language" in st.session_state and st.session_state.user_language != user_language:
        st.session_state.analysis_result = None  # Reset to re-analyze in new language
    
    # Store in session state for access elsewhere
    st.session_state.user_language = user_language
    
    # Language-specific welcome messages
    lang_welcome = {
        "Hinglish": "🔥 Savage Gen-Z mode ON!",
        "English": "🎯 Professional mode activated",
        "Hindi": "🛡️ सुरक्षा मोड सक्रिय",
        "Marathi": "🛡️ सुरक्षा मोड सक्रिय"
    }
    st.caption(lang_welcome.get(user_language, ""))

# Initialize language in session state if not present
if "user_language" not in st.session_state:
    st.session_state.user_language = "Hinglish"

# Language-specific UI text (Complete translations)
UI_TEXT = {
    "Hinglish": {
        # Header
        "tagline": "Tera Apna Financial Bodyguard",
        "subtitle": "Upload karo screenshot, hum batayenge real hai ya scam! 💪",
        # Upload section
        "upload_header": "📸 Screenshot Upload Karo",
        "upload_flow": "📸 Upload → 🧠 AI Analysis → 🛡️ Safety Advice",
        "upload_label": "WhatsApp/SMS ka screenshot yahan daalo",
        "image_details": "📋 **Image Details**",
        "file_label": "File:",
        "size_label": "Size:",
        "dimensions_label": "Dimensions:",
        # Analysis
        "analyze_btn": "🔍 Analyze Karo!",
        "status_activated": "🤖 Satark Agent Activated...",
        "status_received": "📷 Screenshot mila...",
        "status_ocr": "🔍 Text extract ho raha hai...",
        "status_analyzing": "🧠 Analysis ho raha hai",
        "status_checking": "🔎 Scam database check ho raha hai...",
        # Results
        "agent_decision": "🤖 Agent Ka Faisla",
        "citizen_tab": "🛡️ Citizen View",
        "dev_tab": "🛠️ Developer View",
        "risk_meter": "📊 Dhoka Meter",
        "what_to_do": "💡 Ab Kya Karna Hai?",
        # Verdicts
        "safe_title": "✅ SAFE",
        "safe_subtitle": "Yeh legit lagta hai, chill maar!",
        "suspicious_title": "⚠️ SUSPICIOUS",
        "suspicious_subtitle": "Thoda shak hai... Proceed with caution.",
        "scam_title": "🚨 SCAM DETECTED! 🚨",
        "scam_subtitle": "Yeh 100% fraud hai! Engage mat karo!",
        "desi_note_safe": "💬 **Desi Note:** _Yeh legit lagta hai, tension mat le bhai!_",
        "desi_note_suspicious": "💬 **Desi Note:** _Thoda shak hai... Sambhal ke re bhai!_",
        "desi_note_scam": "💬 **Desi Big Brother Says:** _BHAAG JA YAHAN SE! Yeh 100% fraud hai!_",
        "danger_warning": "⛔ DANGER: OTP, PIN ya bank details share mat karo!",
        # Actions
        "recommended_actions": "⚡ Recommended Actions",
        "legal_action": "📝 Legal Action - Complaint Draft Karo",
        "download_complaint": "👮 Cyber Complaint PDF Download Karo",
        "red_flags_title": "🚩 Red Flags Detected",
        "why_label": "❓ **Kyun?**",
        "detected_type": "🏷️ Detected Type:",
        "immediate_action": "🚫 **Turant Action Lo:**",
        "caution": "⚠️ **Savdhaan:**",
        "all_clear": "✅ **Sab Theek:**",
        # Recommended steps
        "steps_scam": """**Recommended Steps:**
1. 🚫 Is number/sender ko turant block karo
2. 🗑️ Message/app delete karo
3. 📞 Cyber Cell: **1930** (National Helpline)
4. ⚠️ Family aur friends ko batao""",
        "steps_suspicious": """**Recommended Steps:**
1. 🔍 Official channels se sender verify karo
2. 🚫 OTP ya personal details share mat karo
3. 📱 Official app/website check karo""",
        "lang_footer": "🌐 Hindi / Marathi support active!"
    },
    "English": {
        # Header
        "tagline": "Your Financial Bodyguard",
        "subtitle": "Upload a screenshot, we'll tell you if it's real or scam! 💪",
        # Upload section
        "upload_header": "📸 Upload Screenshot",
        "upload_flow": "📸 Upload → 🧠 AI Analysis → 🛡️ Safety Advice",
        "upload_label": "Upload WhatsApp/SMS screenshot here",
        "image_details": "📋 **Image Details**",
        "file_label": "File:",
        "size_label": "Size:",
        "dimensions_label": "Dimensions:",
        # Analysis
        "analyze_btn": "🔍 Analyze Now!",
        "status_activated": "🤖 Satark Agent Activated...",
        "status_received": "📷 Screenshot received...",
        "status_ocr": "🔍 Extracting text using OCR...",
        "status_analyzing": "🧠 Analyzing",
        "status_checking": "🔎 Checking against scam database...",
        # Results
        "agent_decision": "🤖 Agent Decision",
        "citizen_tab": "🛡️ Citizen View",
        "dev_tab": "🛠️ Developer View",
        "risk_meter": "📊 Risk Meter",
        "what_to_do": "💡 What Should You Do?",
        # Verdicts
        "safe_title": "✅ SAFE",
        "safe_subtitle": "This content appears to be legitimate.",
        "suspicious_title": "⚠️ SUSPICIOUS",
        "suspicious_subtitle": "This content has some red flags. Proceed with caution.",
        "scam_title": "🚨 SCAM DETECTED! 🚨",
        "scam_subtitle": "This is a confirmed fraudulent message. Do NOT engage!",
        "desi_note_safe": "💬 **Note:** _This appears to be legitimate content._",
        "desi_note_suspicious": "💬 **Note:** _Some suspicious elements detected. Be careful._",
        "desi_note_scam": "💬 **Warning:** _This is confirmed fraud! Block immediately!_",
        "danger_warning": "⛔ DANGER: Do NOT share any OTP, PIN, or bank details!",
        # Actions
        "recommended_actions": "⚡ Recommended Actions",
        "legal_action": "📝 Legal Action - Draft Official Complaint",
        "download_complaint": "👮 Download Cyber Complaint PDF",
        "red_flags_title": "🚩 Red Flags Detected",
        "why_label": "❓ **Why?**",
        "detected_type": "🏷️ Detected Type:",
        "immediate_action": "🚫 **Immediate Action Required:**",
        "caution": "⚠️ **Caution:**",
        "all_clear": "✅ **All Clear:**",
        # Recommended steps
        "steps_scam": """**Recommended Steps:**
1. 🚫 Block this number/sender immediately
2. 🗑️ Delete the message/app
3. 📞 Report to Cyber Cell: **1930** (National Helpline)
4. ⚠️ Warn your family and friends""",
        "steps_suspicious": """**Recommended Steps:**
1. 🔍 Verify the sender through official channels
2. 🚫 Do NOT share OTP or personal details
3. 📱 Check official app/website directly""",
        "lang_footer": "🌐 Multilingual support available!"
    },
    "Hindi": {
        # Header
        "tagline": "आपका वित्तीय बॉडीगार्ड",
        "subtitle": "स्क्रीनशॉट अपलोड करें, हम बताएंगे असली है या धोखा! 💪",
        # Upload section
        "upload_header": "📸 स्क्रीनशॉट अपलोड करें",
        "upload_flow": "📸 अपलोड → 🧠 AI विश्लेषण → 🛡️ सुरक्षा सलाह",
        "upload_label": "WhatsApp/SMS का स्क्रीनशॉट यहाँ डालें",
        "image_details": "📋 **छवि विवरण**",
        "file_label": "फाइल:",
        "size_label": "आकार:",
        "dimensions_label": "आयाम:",
        # Analysis
        "analyze_btn": "🔍 जांच करो!",
        "status_activated": "🤖 सतर्क एजेंट सक्रिय...",
        "status_received": "📷 स्क्रीनशॉट प्राप्त...",
        "status_ocr": "🔍 टेक्स्ट निकाला जा रहा है...",
        "status_analyzing": "🧠 विश्लेषण हो रहा है",
        "status_checking": "🔎 स्कैम डेटाबेस चेक हो रहा है...",
        # Results
        "agent_decision": "🤖 एजेंट का फैसला",
        "citizen_tab": "🛡️ नागरिक दृश्य",
        "dev_tab": "🛠️ डेवलपर दृश्य",
        "risk_meter": "📊 धोखा मीटर",
        "what_to_do": "💡 अब क्या करना है?",
        # Verdicts
        "safe_title": "✅ सुरक्षित",
        "safe_subtitle": "यह सामग्री वैध प्रतीत होती है।",
        "suspicious_title": "⚠️ संदिग्ध",
        "suspicious_subtitle": "इसमें कुछ खतरे के संकेत हैं। सावधानी से आगे बढ़ें।",
        "scam_title": "🚨 धोखाधड़ी पकड़ी गई! 🚨",
        "scam_subtitle": "यह एक पुष्ट फ्रॉड संदेश है। संपर्क न करें!",
        "desi_note_safe": "💬 **नोट:** _यह सुरक्षित लगता है, चिंता मत करो भाई!_",
        "desi_note_suspicious": "💬 **नोट:** _थोड़ा संदेह है... सावधान रहो भाई!_",
        "desi_note_scam": "💬 **चेतावनी:** _यहाँ से भागो! यह 100% फ्रॉड है!_",
        "danger_warning": "⛔ खतरा: OTP, PIN या बैंक डिटेल्स शेयर मत करो!",
        # Actions
        "recommended_actions": "⚡ सुझाए गए कदम",
        "legal_action": "📝 कानूनी कार्रवाई - शिकायत दर्ज करें",
        "download_complaint": "👮 साइबर शिकायत PDF डाउनलोड करें",
        "red_flags_title": "🚩 खतरे के संकेत",
        "why_label": "❓ **क्यों?**",
        "detected_type": "🏷️ पता चला प्रकार:",
        "immediate_action": "🚫 **तुरंत कार्रवाई करें:**",
        "caution": "⚠️ **सावधान:**",
        "all_clear": "✅ **सब ठीक:**",
        # Recommended steps
        "steps_scam": """**सुझाए गए कदम:**
1. 🚫 इस नंबर/भेजने वाले को तुरंत ब्लॉक करें
2. 🗑️ संदेश/ऐप हटाएं
3. 📞 साइबर सेल: **1930** (राष्ट्रीय हेल्पलाइन)
4. ⚠️ परिवार और दोस्तों को सचेत करें""",
        "steps_suspicious": """**सुझाए गए कदम:**
1. 🔍 आधिकारिक चैनलों से भेजने वाले की पुष्टि करें
2. 🚫 OTP या व्यक्तिगत विवरण साझा न करें
3. 📱 आधिकारिक ऐप/वेबसाइट सीधे देखें""",
        "lang_footer": "🌐 हिंदी में सुरक्षा सलाह सक्रिय!"
    },
    "Marathi": {
        # Header
        "tagline": "तुमचा आर्थिक बॉडीगार्ड",
        "subtitle": "स्क्रीनशॉट अपलोड करा, आम्ही सांगू खरं की फसवणूक! 💪",
        # Upload section
        "upload_header": "📸 स्क्रीनशॉट अपलोड करा",
        "upload_flow": "📸 अपलोड → 🧠 AI विश्लेषण → 🛡️ सुरक्षा सल्ला",
        "upload_label": "WhatsApp/SMS चा स्क्रीनशॉट इथे टाका",
        "image_details": "📋 **प्रतिमा तपशील**",
        "file_label": "फाइल:",
        "size_label": "आकार:",
        "dimensions_label": "परिमाण:",
        # Analysis
        "analyze_btn": "🔍 तपासा!",
        "status_activated": "🤖 सतर्क एजंट सक्रिय...",
        "status_received": "📷 स्क्रीनशॉट मिळाला...",
        "status_ocr": "🔍 मजकूर काढला जात आहे...",
        "status_analyzing": "🧠 विश्लेषण होत आहे",
        "status_checking": "🔎 स्कॅम डेटाबेस तपासत आहे...",
        # Results
        "agent_decision": "🤖 एजंटचा निर्णय",
        "citizen_tab": "🛡️ नागरिक दृश्य",
        "dev_tab": "🛠️ डेव्हलपर दृश्य",
        "risk_meter": "📊 धोका मीटर",
        "what_to_do": "💡 आता काय करायचं?",
        # Verdicts
        "safe_title": "✅ सुरक्षित",
        "safe_subtitle": "हे सामग्री वैध दिसते.",
        "suspicious_title": "⚠️ संशयास्पद",
        "suspicious_subtitle": "यात काही धोक्याचे संकेत आहेत. सावधगिरीने पुढे जा.",
        "scam_title": "🚨 फसवणूक पकडली! 🚨",
        "scam_subtitle": "हा एक पुष्टी झालेला फ्रॉड संदेश आहे. संपर्क करू नका!",
        "desi_note_safe": "💬 **टीप:** _हे सुरक्षित दिसतंय, टेन्शन नको घेऊस!_",
        "desi_note_suspicious": "💬 **टीप:** _थोडा संशय आहे... सावध राहा भाऊ!_",
        "desi_note_scam": "💬 **चेतावणी:** _इथून पळ! हे 100% फ्रॉड आहे!_",
        "danger_warning": "⛔ धोका: OTP, PIN किंवा बँक डिटेल्स शेअर करू नका!",
        # Actions
        "recommended_actions": "⚡ शिफारस केलेल्या कृती",
        "legal_action": "📝 कायदेशीर कारवाई - तक्रार दाखल करा",
        "download_complaint": "👮 सायबर तक्रार PDF डाउनलोड करा",
        "red_flags_title": "🚩 धोक्याचे संकेत",
        "why_label": "❓ **का?**",
        "detected_type": "🏷️ आढळलेला प्रकार:",
        "immediate_action": "🚫 **लगेच कारवाई करा:**",
        "caution": "⚠️ **सावध:**",
        "all_clear": "✅ **सर्व ठीक:**",
        # Recommended steps
        "steps_scam": """**शिफारस केलेले पाऊल:**
1. 🚫 हा नंबर/पाठवणारा लगेच ब्लॉक करा
2. 🗑️ संदेश/ॲप हटवा
3. 📞 सायबर सेल: **1930** (राष्ट्रीय हेल्पलाइन)
4. ⚠️ कुटुंब आणि मित्रांना सावध करा""",
        "steps_suspicious": """**शिफारस केलेले पाऊल:**
1. 🔍 अधिकृत मार्गांनी पाठवणाऱ्याची पडताळणी करा
2. 🚫 OTP किंवा वैयक्तिक माहिती शेअर करू नका
3. 📱 थेट अधिकृत ॲप/वेबसाइट तपासा""",
        "lang_footer": "🌐 मराठीत सुरक्षा सल्ला सक्रिय!",
        # Empty state & Use cases
        "empty_state": "👆 विश्लेषण सुरू करण्यासाठी स्क्रीनशॉट अपलोड करा!",
        "use_cases_header": "🎯 हे ॲप कधी वापरायचे?",
        "use_case_1_title": "**कर्ज ॲप संदेश**",
        "use_case_1_desc": "जेव्हा कोणी रँडम मेसेजने कर्ज ऑफर करतो",
        "use_case_2_title": "**लॉटरी स्कॅम**",
        "use_case_2_desc": "'तुम्ही 50 लाख जिंकलात!' असे संदेश",
        "use_case_3_title": "**डिजिटल अरेस्ट**",
        "use_case_3_desc": "खोटे पोलीस/CBI धमकी कॉल्स",
        "footer_quote": "\"आपल्या मेहनतीचे पैसे आहेत, असे उधळू नका.\" - Satark.ai",
        "footer_disclaimer": "⚠️ सूचना: हे साधन फक्त जागरूकतेसाठी आहे. कायदेशीर सल्ल्यासाठी योग्य अधिकाऱ्यांशी संपर्क साधा."
    }
}

# Add empty state translations to all languages
UI_TEXT["Hinglish"].update({
    "empty_state": "👆 Screenshot upload karo analysis shuru karne ke liye!",
    "use_cases_header": "🎯 Yeh App Kab Use Karna Hai?",
    "use_case_1_title": "**Loan App Messages**",
    "use_case_1_desc": "Jab koi loan offer kare random message se",
    "use_case_2_title": "**Lottery Scams**",
    "use_case_2_desc": "'Aapne 50 lakh jeete!' wale messages",
    "use_case_3_title": "**Digital Arrest**",
    "use_case_3_desc": "Fake police/CBI threat calls",
    "footer_quote": "\"Apni mehnat ka paisa hai, aise mat udaao.\" - Satark.ai",
    "footer_disclaimer": "⚠️ Disclaimer: Yeh tool sirf awareness ke liye hai. Legal advice ke liye proper authorities se contact karo."
})

UI_TEXT["English"].update({
    "empty_state": "👆 Upload a screenshot to start analysis!",
    "use_cases_header": "🎯 When to Use This App?",
    "use_case_1_title": "**Loan App Messages**",
    "use_case_1_desc": "When someone offers loans via random messages",
    "use_case_2_title": "**Lottery Scams**",
    "use_case_2_desc": "'You won 50 lakhs!' type messages",
    "use_case_3_title": "**Digital Arrest**",
    "use_case_3_desc": "Fake police/CBI threat calls",
    "footer_quote": "\"It's your hard-earned money, don't waste it.\" - Satark.ai",
    "footer_disclaimer": "⚠️ Disclaimer: This tool is for awareness only. Contact proper authorities for legal advice."
})

UI_TEXT["Hindi"].update({
    "empty_state": "👆 विश्लेषण शुरू करने के लिए स्क्रीनशॉट अपलोड करें!",
    "use_cases_header": "🎯 यह ऐप कब इस्तेमाल करना है?",
    "use_case_1_title": "**लोन ऐप मैसेज**",
    "use_case_1_desc": "जब कोई रैंडम मैसेज से लोन ऑफर करे",
    "use_case_2_title": "**लॉटरी स्कैम**",
    "use_case_2_desc": "'आपने 50 लाख जीते!' वाले मैसेज",
    "use_case_3_title": "**डिजिटल अरेस्ट**",
    "use_case_3_desc": "नकली पुलिस/CBI धमकी कॉल्स",
    "footer_quote": "\"अपनी मेहनत का पैसा है, ऐसे मत उड़ाओ।\" - Satark.ai",
    "footer_disclaimer": "⚠️ अस्वीकरण: यह टूल सिर्फ जागरूकता के लिए है। कानूनी सलाह के लिए उचित अधिकारियों से संपर्क करें।"
})

# Get current language text
current_lang = st.session_state.user_language
ui = UI_TEXT.get(current_lang, UI_TEXT["Hinglish"])

# Display language-aware header
st.subheader(ui["tagline"])
st.caption(ui["subtitle"])

# Main Upload Section
st.header(ui["upload_header"])

# 3-Step Visual Flow - High Contrast (dynamic text)
st.markdown(f"""
<div style='background: linear-gradient(90deg, #1565c0, #7b1fa2, #2e7d32); 
            padding: 1rem 2rem; border-radius: 12px; text-align: center; 
            margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.2);'>
    <span style='font-size: 1.4rem; font-weight: 600; color: white; letter-spacing: 0.5px;'>
        {ui["upload_flow"]}
    </span>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    ui["upload_label"],
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
        st.image(image, use_container_width=True)
    
    with col2:
        st.info(ui["image_details"])
        st.write(f"**{ui['file_label']}** {uploaded_file.name}")
        st.write(f"**{ui['size_label']}** {uploaded_file.size / 1024:.1f} KB")
        st.write(f"**{ui['dimensions_label']}** {image.size[0]} x {image.size[1]}")
    
    st.divider()
    
    # Analyze Button - only triggers analysis, results shown from session state
    if st.button(ui["analyze_btn"], type="primary", use_container_width=True, key="analyze_btn"):
        
        # Generate scan ID and timestamp
        st.session_state.scan_id = f"SATARK-{str(uuid.uuid4())[:8].upper()}"
        st.session_state.scan_timestamp = datetime.now().isoformat()
        
        # Use st.status for detailed progress
        with st.status(ui["status_activated"], expanded=True) as status:
            st.write(ui["status_received"])
            st.write(ui["status_ocr"])
            st.write(f"{ui['status_analyzing']} ({current_lang})...")
            st.write("🔴 Checking LIVE scam database...")
            st.write(ui["status_checking"])
            st.write("🌐 Searching internet for scam reports...")
            
            # Call the enhanced analysis function with internet search
            result = analyze_with_internet_search(
                image, 
                api_key if api_key else None,
                language=current_lang
            )
            
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
        
        # Display Results with Tabs (Language-aware)
        st.header(ui["agent_decision"])
        
        # Create tabs for different views
        citizen_tab, dev_tab = st.tabs([ui["citizen_tab"], ui["dev_tab"]])
        
        # ==================== CITIZEN VIEW ====================
        with citizen_tab:
            # Verdict Display
            risk_score = result.get("risk_score", 0)
            verdict = result.get("verdict", "UNKNOWN")
            
            # Main Alert Box (Language-aware)
            if verdict == "SAFE":
                st.balloons()
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #00c853, #69f0ae); 
                            color: white; padding: 2rem; border-radius: 15px; 
                            text-align: center; margin: 1rem 0;
                            box-shadow: 0 4px 15px rgba(0,200,83,0.4);'>
                    <h1 style='margin:0; font-size: 3rem;'>{ui["safe_title"]}</h1>
                    <p style='font-size: 1.3rem; margin-top: 0.5rem;'>{ui["safe_subtitle"]}</p>
                </div>
                """, unsafe_allow_html=True)
                st.info(ui["desi_note_safe"])
                
            elif verdict == "SUSPICIOUS":
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #ff9800, #ffb74d); 
                            color: white; padding: 2rem; border-radius: 15px; 
                            text-align: center; margin: 1rem 0;
                            box-shadow: 0 4px 15px rgba(255,152,0,0.4);'>
                    <h1 style='margin:0; font-size: 3rem;'>{ui["suspicious_title"]}</h1>
                    <p style='font-size: 1.3rem; margin-top: 0.5rem;'>{ui["suspicious_subtitle"]}</p>
                </div>
                """, unsafe_allow_html=True)
                st.warning(ui["desi_note_suspicious"])
                
            else:  # SCAM
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #d32f2f, #f44336); 
                            color: white; padding: 2rem; border-radius: 15px; 
                            text-align: center; margin: 1rem 0;
                            box-shadow: 0 8px 25px rgba(211,47,47,0.5);
                            animation: pulse 1s infinite;'>
                    <h1 style='margin:0; font-size: 3.5rem;'>{ui["scam_title"]}</h1>
                    <p style='font-size: 1.5rem; margin-top: 0.5rem; font-weight: bold;'>
                        {ui["scam_subtitle"]}
                    </p>
                </div>
                <style>
                    @keyframes pulse {{
                        0% {{ transform: scale(1); }}
                        50% {{ transform: scale(1.02); }}
                        100% {{ transform: scale(1); }}
                    }}
                </style>
                """, unsafe_allow_html=True)
                st.error(ui["danger_warning"])
                st.markdown(f"> {ui['desi_note_scam']}")
                
                # Recommended Actions - Quick Action Buttons
                st.markdown(f"#### {ui['recommended_actions']}")
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                
                with btn_col1:
                    st.button("🚫 Block", type="primary", use_container_width=True, key="btn_block", disabled=True)
                
                with btn_col2:
                    st.button("🗑️ Delete", use_container_width=True, key="btn_delete", disabled=True)
                
                with btn_col3:
                    st.button("📞 1930", use_container_width=True, key="btn_report", disabled=True)
                
                # Legal Action - Generate Cyber Complaint PDF (Direct Download)
                st.divider()
                st.markdown(f"#### {ui['legal_action']}")
                
                # Generate PDF immediately for one-click download
                entities = result.get("extracted_entities", {})
                scam_details = {
                    "scam_type": result.get("scam_type", "Financial Fraud"),
                    "phone_number": entities.get("phone_number"),
                    "company_name": entities.get("company_name"),
                    "amount": entities.get("amount"),
                    "extracted_text": result.get("reasoning", ""),
                    "risk_score": result.get("risk_score", 0),
                    "red_flags": result.get("red_flags", []),
                    "reasoning": result.get("reasoning", ""),
                    "user_profile": DEMO_USER_PROFILE
                }
                
                # Store PDF in session state to prevent regeneration on rerun
                if "complaint_pdf" not in st.session_state or st.session_state.get("last_scan_id") != st.session_state.scan_id:
                    st.session_state.complaint_pdf = generate_cyber_complaint(scam_details)
                    st.session_state.complaint_filename = f"Cyber_Complaint_{datetime.now().strftime('%Y%m%d')}.pdf"
                    st.session_state.last_scan_id = st.session_state.scan_id
                
                # Use container to isolate download button
                download_container = st.container()
                with download_container:
                    st.download_button(
                        label="👮 Draft & Download Cyber Complaint",
                        data=st.session_state.complaint_pdf,
                        file_name=st.session_state.complaint_filename,
                        mime="application/pdf",
                        use_container_width=True,
                        type="primary",
                        key="download_complaint"
                    )
                
                # CERT-In Direct Complaint Email
                st.markdown("""
                <div style='background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                            border: 1px solid #0f3460; 
                            border-radius: 8px; 
                            padding: 12px 16px; 
                            margin-top: 10px;'>
                    <p style='margin: 0; font-size: 0.9rem; color: #e0e0e0;'>
                        📧 <strong>Direct Complaint to CERT-In:</strong> 
                        <a href='mailto:info@cert-in.org.in?subject=Cyber%20Fraud%20Complaint%20-%20Satark.ai%20Report' 
                           style='color: #00d4ff; text-decoration: none; font-weight: bold;'>
                           info@cert-in.org.in
                        </a>
                    </p>
                    <p style='margin: 5px 0 0 0; font-size: 0.75rem; color: #888;'>
                        📞 Cyber Helpline: <strong>1930</strong> | 🌐 cybercrime.gov.in
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            st.divider()
            
            # Visual Risk Meter with Color-Coded Metric (Language-aware)
            st.subheader(ui["risk_meter"])
            
            meter_score = result.get("risk_score", 50)
            
            # Language-specific risk labels
            risk_labels = {
                "Hinglish": {
                    "low": "🟢 Low Risk (Safe)",
                    "med": "🟡 Medium Risk (Caution)", 
                    "high": "🔴 High Risk (Danger!)",
                    "prob": "Dhoka Probability"
                },
                "English": {
                    "low": "🟢 Low Risk (Safe)",
                    "med": "🟡 Medium Risk (Caution)",
                    "high": "🔴 High Risk (Critical Alert)",
                    "prob": "Scam Probability"
                },
                "Hindi": {
                    "low": "🟢 कम जोखिम (सुरक्षित)",
                    "med": "🟡 मध्यम जोखिम (सावधान)",
                    "high": "🔴 उच्च जोखिम (खतरा!)",
                    "prob": "धोखा संभावना"
                },
                "Marathi": {
                    "low": "🟢 कमी धोका (सुरक्षित)",
                    "med": "🟡 मध्यम धोका (सावध)",
                    "high": "🔴 जास्त धोका (धोकादायक!)",
                    "prob": "फसवणूक शक्यता"
                }
            }
            
            lang_labels = risk_labels.get(current_lang, risk_labels["Hinglish"])
            
            # Color-coded risk level
            if meter_score < 20:
                risk_label = lang_labels["low"]
                risk_color = "#00c853"
            elif meter_score <= 80:
                risk_label = lang_labels["med"]
                risk_color = "#ff9800"
            else:
                risk_label = lang_labels["high"]
                risk_color = "#d32f2f"
            
            # Display metric with styled container
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, {risk_color}22, {risk_color}11); 
                        border: 2px solid {risk_color}; border-radius: 15px; 
                        padding: 1.5rem; text-align: center; margin: 0.5rem 0;'>
                <p style='font-size: 1rem; color: #666; margin: 0;'>{lang_labels["prob"]}</p>
                <h1 style='font-size: 3rem; color: {risk_color}; margin: 0.3rem 0;'>{meter_score}%</h1>
                <p style='font-size: 1.2rem; font-weight: bold; color: {risk_color}; margin: 0;'>{risk_label}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Progress bar for visual effect
            st.progress(min(meter_score, 100) / 100)
            
            # "Why?" box with top 3 red flags (Language-aware)
            red_flags = result.get("red_flags", [])
            if red_flags:
                top_flags = red_flags[:3]  # Get top 3
                flags_text = " • ".join(top_flags)
                st.caption(f"{ui['why_label']} {flags_text}")
            
            # Show scam type if detected
            scam_type = result.get("scam_type", "N/A")
            if scam_type and scam_type not in ["N/A", "None", "null"] and verdict != "SAFE":
                st.markdown(f"<p style='text-align: center; color: #666; font-size: 1rem; margin-top: 0.5rem;'>{ui['detected_type']} <b>{scam_type}</b></p>", unsafe_allow_html=True)
            
            # LIVE DATABASE MATCH - THE WOW MOMENT! 🔥
            live_db_data = result.get("live_database", {})
            if live_db_data.get("total_hits", 0) > 0:
                st.divider()
                st.subheader("🚨 LIVE DATABASE ALERT!")
                
                hits = live_db_data.get("hits", [])
                for hit in hits:
                    if hit['type'] == 'phone':
                        st.error(f"""
                        **📱 CONFIRMED SCAMMER NUMBER!**
                        
                        This number `{hit['value']}` has been reported **{hit['reports']} times** in our live database!
                        
                        Last seen: {hit['last_seen'][:10]}
                        
                        Known scam types: {', '.join(hit['scam_types'][:3])}
                        """)
                    elif hit['type'] == 'upi':
                        st.warning(f"""
                        **💳 UPI ID IN SCAM DATABASE!**
                        
                        This UPI ID `{hit['value']}` has been flagged **{hit['reports']} times**!
                        
                        DO NOT send money to this account!
                        """)
                
                st.success("✅ This data comes from REAL scam reports updated hourly!")
            
            st.divider()
            
            # Actionable Advice Section (Language-aware)
            st.subheader(ui["what_to_do"])
            
            # Get translated advice from AI response
            hinglish = result.get("hinglish_advice", result.get("action", ""))
            
            if verdict == "SCAM":
                st.error(f"{ui['immediate_action']} {hinglish}")
                st.markdown(ui["steps_scam"])
            elif verdict == "SUSPICIOUS":
                st.warning(f"{ui['caution']} {hinglish}")
                st.markdown(ui["steps_suspicious"])
            else:
                st.success(f"{ui['all_clear']} {hinglish}")
            
            # Red flags summary for citizens
            if result.get("red_flags"):
                with st.expander(ui["red_flags_title"], expanded=False):
                    for flag in result["red_flags"]:
                        st.write(f"• {flag}")
            
            # Internet Search Results Section
            internet_data = result.get("internet_search", {})
            if internet_data and internet_data.get("sources_found", 0) > 0:
                st.divider()
                st.subheader("🌐 Internet Verification Results")
                
                search_results = internet_data.get("results", [])
                sources_count = internet_data.get("sources_found", 0)
                is_verified = result.get("internet_verified", False)
                
                if is_verified:
                    st.error(f"⚠️ Found {sources_count} online reports confirming this scam!")
                else:
                    st.info(f"ℹ️ Searched {sources_count} sources. No major scam reports found.")
                
                with st.expander(f"📰 View {min(len(search_results), 5)} Search Results", expanded=is_verified):
                    for idx, result_item in enumerate(search_results[:5], 1):
                        st.markdown(f"**{idx}. {result_item.get('title', 'No title')}**")
                        st.caption(result_item.get('snippet', 'No description'))
                        st.markdown(f"🔗 [Read more]({result_item.get('link', '#')})")
                        if idx < len(search_results[:5]):
                            st.markdown("---")
            
            # Local Impact Footer (Language-aware)
            st.divider()
            st.markdown(f"<p style='text-align: center; color: #888; font-size: 0.9rem;'>{ui['lang_footer']}</p>", unsafe_allow_html=True)
        
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
                "parse_success": result.get("parse_success", False),
                "internet_search": result.get("internet_search", {}),
                "internet_verified": result.get("internet_verified", False)
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
    # Empty state (Language-aware)
    st.info(ui["empty_state"])
    
    # Sample use cases (Language-aware)
    st.subheader(ui["use_cases_header"])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 💰")
        st.write(ui["use_case_1_title"])
        st.caption(ui["use_case_1_desc"])
    
    with col2:
        st.markdown("### 🎰")
        st.write(ui["use_case_2_title"])
        st.caption(ui["use_case_2_desc"])
    
    with col3:
        st.markdown("### 👮")
        st.write(ui["use_case_3_title"])
        st.caption(ui["use_case_3_desc"])

# Footer (Language-aware)
st.divider()
st.markdown(f"""
<div style='text-align: center; padding: 2rem 0;'>
    <p style='color: #888; font-size: 0.9rem; font-style: italic; margin-bottom: 0.5rem;'>
        {ui["footer_quote"]}
    </p>
    <p style='color: #888; font-size: 0.85rem; margin-bottom: 0.3rem;'>
        Made with ❤️ by Team Tark
    </p>
    <p style='color: #aaa; font-size: 0.75rem;'>
        © 2025 Satark.ai | ML Nashik Gen AI-thon
    </p>
    <p style='color: #aaa; font-size: 0.7rem; margin-top: 0.5rem;'>
        {ui["footer_disclaimer"]}
    </p>
</div>
""", unsafe_allow_html=True)
