"""
Satark.ai - Utility Functions
Google Gemini API Integration
"""

import google.generativeai as genai
from PIL import Image
import json
import os
import re
from dotenv import load_dotenv


load_dotenv()


DEFAULT_API_KEY = os.getenv("GEMINI_API_KEY")


SCAM_DETECTION_PROMPT = """You are "Satark.ai" - a financial scam detection AI agent acting as a protective "Desi Big Brother" for Indian users.

Analyze this screenshot (WhatsApp/SMS/App) and detect if it's a financial scam.

## Your Analysis Process:
1. **OCR & Extract:** Read all text. Identify: Company Name, Phone Numbers, Amounts, URLs, App Names.
2. **Check Red Flags:**
   - Threatening/urgent language ("Pay now or jail", "Digital Arrest", "Last warning")
   - Requests for upfront fees before loan disbursement
   - Unrealistic promises (lottery wins, guaranteed returns >15%)
   - Poor grammar/spelling mistakes
   - Requests for OTP, UPI PIN, or bank details
   - Unknown/suspicious sender numbers
   - Fake government/bank impersonation (RBI, SBI, CBI, Police)
3. **Blacklist Check:** Flag these keywords as SCAM: "Laxmi Chit Fund", "RbiApproved_Loan", "Digital Arrest", "Cyber Cell Arrest", "Nigeria Prince", "Lottery Winner"

## Response Format (STRICT JSON):
{
    "verdict": "SAFE" | "SUSPICIOUS" | "SCAM",
    "risk_score": <0-100>,
    "reasoning": "<2-3 sentence explanation in Hinglish, be protective and slightly savage like a big brother>",
    "red_flags": ["<flag1>", "<flag2>"],
    "extracted_info": {
        "company_name": "<if found>",
        "phone_number": "<if found>",
        "amount": "<if found>"
    },
    "action": "<What user should do - block number, delete app, report to cyber cell, etc.>",
    "blacklisted_entity": <true/false>
}

Remember: You're protecting naive users in Tier-2/3 Indian cities. Be firm, protective, and use Hinglish tone.
ONLY respond with valid JSON. No markdown, no extra text."""


def configure_gemini(api_key: str):
    """Configure the Gemini API with the provided key."""
    genai.configure(api_key=api_key)


def analyze_screenshot(image: Image.Image, api_key: str = None) -> dict:
    """
    Analyze a screenshot for potential scams using Gemini 1.5 Flash.
    
    Args:
        image: PIL Image object of the screenshot
        api_key: Google Gemini API key (optional, uses default if not provided)
    
    Returns:
        dict with verdict, risk_score, reasoning, and action
    """
    # Use provided key or fallback to default from environment
    key = api_key or DEFAULT_API_KEY
    if not key:
        return {
            "verdict": "ERROR",
            "risk_score": 0,
            "reasoning": "Gemini API key missing. Set GEMINI_API_KEY in your environment or .env file.",
            "red_flags": [],
            "extracted_info": {},
            "action": "Configure GEMINI_API_KEY and reload.",
            "blacklisted_entity": False
        }
    configure_gemini(key)
    
    try:
        # Initialize the model (using gemini-2.0-flash for better availability)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Send image with prompt to Gemini
        response = model.generate_content([SCAM_DETECTION_PROMPT, image])
        
        # Parse the JSON response
        response_text = response.text.strip()
        
        # Clean up response if it has markdown code blocks
        if response_text.startswith("```"):
            response_text = re.sub(r'^```json?\s*', '', response_text)
            response_text = re.sub(r'\s*```$', '', response_text)
        
        result = json.loads(response_text)
        
        # Ensure all required keys exist
        result.setdefault("verdict", "SUSPICIOUS")
        result.setdefault("risk_score", 50)
        result.setdefault("reasoning", "Analysis complete.")
        result.setdefault("red_flags", [])
        result.setdefault("extracted_info", {})
        result.setdefault("action", "Stay alert!")
        result.setdefault("blacklisted_entity", False)
        
        return result
        
    except json.JSONDecodeError as e:
        return {
            "verdict": "SUSPICIOUS",
            "risk_score": 50,
            "reasoning": f"Bhai, kuch technical issue hai parsing mein. But stay alert!",
            "red_flags": ["Could not parse AI response"],
            "extracted_info": {},
            "action": "Try again or manually review the message.",
            "blacklisted_entity": False,
            "raw_response": response.text if 'response' in dir() else str(e)
        }
    except Exception as e:
        return {
            "verdict": "ERROR",
            "risk_score": 0,
            "reasoning": f"API Error: {str(e)}",
            "red_flags": [],
            "extracted_info": {},
            "action": "Check your API key and try again.",
            "blacklisted_entity": False
        }


# Simulated blacklist database (Hackathon trick)
BLACKLISTED_KEYWORDS = [
    "laxmi chit fund",
    "rbiapproved_loan",
    "instant loan apk",
    "digital arrest",
    "cyber cell arrest",
    "pay now or jail",
    "lottery winner",
    "nigeria prince",
    "send otp",
    "share otp"
]


# Scam Database - Fake scam apps vs Real banks
SCAM_DATABASE = {
    # Fake Indian Scam Apps (10)
    "scam_apps": [
        {"name": "Laxmi Chit Fund", "type": "Ponzi Scheme", "risk": 100},
        {"name": "EasyLoan 24x7", "type": "Predatory Loan App", "risk": 95},
        {"name": "RBI Approved Loan APK", "type": "Fake RBI Impersonation", "risk": 100},
        {"name": "Shree Ganesh Finance", "type": "Illegal NBFC", "risk": 90},
        {"name": "QuickCash India", "type": "Predatory Loan App", "risk": 95},
        {"name": "Bharat Money Lender", "type": "Harassment App", "risk": 92},
        {"name": "Golden Harvest Scheme", "type": "Ponzi Scheme", "risk": 100},
        {"name": "InstaCred Pro", "type": "Data Theft App", "risk": 88},
        {"name": "PM Yojana Loan", "type": "Govt Impersonation", "risk": 100},
        {"name": "SBI Direct Loan WhatsApp", "type": "Bank Impersonation", "risk": 98},
    ],
    # Real Legitimate Banks (5)
    "real_banks": [
        {"name": "State Bank of India", "type": "PSU Bank", "risk": 0},
        {"name": "HDFC Bank", "type": "Private Bank", "risk": 0},
        {"name": "ICICI Bank", "type": "Private Bank", "risk": 0},
        {"name": "Axis Bank", "type": "Private Bank", "risk": 0},
        {"name": "Punjab National Bank", "type": "PSU Bank", "risk": 0},
    ]
}


def check_database(name: str) -> dict:
    """
    Fuzzy match input text against SCAM_DATABASE.
    
    Args:
        name: Company/app name to check
    
    Returns:
        dict with match_found, entity_type, entity_name, risk_score, is_scam
    """
    if not name:
        return {"match_found": False, "is_scam": False}
    
    name_lower = name.lower().strip()
    
    # Check scam apps first (higher priority)
    for scam in SCAM_DATABASE["scam_apps"]:
        scam_name_lower = scam["name"].lower()
        
        # Fuzzy matching: check if significant words match
        scam_words = set(scam_name_lower.split())
        input_words = set(name_lower.split())
        
        # Direct substring match
        if scam_name_lower in name_lower or name_lower in scam_name_lower:
            return {
                "match_found": True,
                "entity_type": scam["type"],
                "entity_name": scam["name"],
                "risk_score": scam["risk"],
                "is_scam": True,
                "message": f"🚨 BLACKLISTED: {scam['name']} - {scam['type']}"
            }
        
        # Word overlap matching (fuzzy)
        common_words = scam_words.intersection(input_words)
        # Ignore common words
        common_words -= {"loan", "bank", "india", "finance", "money", "cash"}
        
        if len(common_words) >= 2 or (len(common_words) == 1 and len(scam_words) <= 2):
            return {
                "match_found": True,
                "entity_type": scam["type"],
                "entity_name": scam["name"],
                "risk_score": scam["risk"],
                "is_scam": True,
                "message": f"⚠️ POSSIBLE MATCH: {scam['name']} - {scam['type']}"
            }
    
    # Check real banks
    for bank in SCAM_DATABASE["real_banks"]:
        bank_name_lower = bank["name"].lower()
        
        if bank_name_lower in name_lower or name_lower in bank_name_lower:
            return {
                "match_found": True,
                "entity_type": bank["type"],
                "entity_name": bank["name"],
                "risk_score": bank["risk"],
                "is_scam": False,
                "message": f"✅ VERIFIED: {bank['name']} - Legitimate {bank['type']}"
            }
        
        # Check abbreviations (SBI, HDFC, ICICI, etc.)
        abbreviations = {
            "state bank of india": ["sbi"],
            "hdfc bank": ["hdfc"],
            "icici bank": ["icici"],
            "axis bank": ["axis"],
            "punjab national bank": ["pnb"]
        }
        
        if bank_name_lower in abbreviations:
            for abbr in abbreviations[bank_name_lower]:
                if abbr in name_lower.split():
                    return {
                        "match_found": True,
                        "entity_type": bank["type"],
                        "entity_name": bank["name"],
                        "risk_score": bank["risk"],
                        "is_scam": False,
                        "message": f"✅ VERIFIED: {bank['name']} - Legitimate {bank['type']}"
                    }
    
    # No match found
    return {
        "match_found": False,
        "entity_type": "Unknown",
        "entity_name": name,
        "risk_score": 50,
        "is_scam": None,
        "message": "⚠️ NOT IN DATABASE - Proceed with caution"
    }


def check_blacklist(text: str) -> tuple[bool, str]:
    """
    Check if the text contains any blacklisted keywords.
    
    Returns:
        (is_blacklisted, matched_keyword)
    """
    text_lower = text.lower()
    for keyword in BLACKLISTED_KEYWORDS:
        if keyword in text_lower:
            return True, keyword
    return False, ""
