"""
Tammeny — Main UI  (Improved)
Run: streamlit run app.py
"""

import streamlit as st
import requests
import json

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Tammeny | طمّني",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Service URLs ──────────────────────────────────────────────────────────────
CHATBOT_URL = "http://127.0.0.1:8000"
VISION_URL  = "http://127.0.0.1:8001"
IMAGING_URL = "http://127.0.0.1:8002"

# ── Session state ─────────────────────────────────────────────────────────────
for key, default in [
    ("lang",              "en"),
    ("page",              "home"),
    ("prev_page",         "home"),
    ("chat_history",      []),
    ("session_id",        "tammeny_ui"),
    ("chat_input_field",  ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Translations ──────────────────────────────────────────────────────────────
T = {
    "en": {
        "app":           "Tammeny",
        "tagline":       "AI-Powered Healthcare Communication",
        "nav_home":      "Home",
        "nav_xray":      "X-Ray Analyzer",
        "nav_vision":    "Vision AI",
        "nav_chat":      "Health Assistant",
        "lang_label":    "Language",
        "back":          "Back",
        "hero":          "Understand Your Health,\nIn Your Language.",
        "hero_sub":      "Tammeny bridges the gap between complex medical AI and real patient understanding — plain-language explanations, document Q&A, and intelligent health guidance.",
        "c1_title":      "X-Ray Analyzer",
        "c1_desc":       "Upload a chest X-ray for AI screening with plain-language results. Powered by DenseNet-121 trained on 100k+ NIH images.",
        "c2_title":      "Vision AI",
        "c2_desc":       "Upload any medical image and ask a question. Our vision model explains what it sees in language you can understand.",
        "c3_title":      "Health Assistant",
        "c3_desc":       "Ask health questions and get warm, evidence-based answers. Upload a medical PDF for document-grounded responses.",
        "open_tool":     "",
        "stats_svc":     "AI Services",
        "stats_cond":    "Detectable Conditions",
        "stats_lang":    "Languages",
        "stats_plain":   "Plain Language Results",
        "xray_title":    "Chest X-Ray Analyzer",
        "xray_sub":      "AI screening for 14 thoracic conditions — powered by DenseNet-121 / NIH ChestX-ray14",
        "xray_upload":   "Upload chest X-ray (JPG / PNG)",
        "xray_thresh":   "Confidence threshold",
        "xray_btn":      "Analyze X-Ray",
        "xray_patient":  "Patient Summary",
        "xray_findings": "Detailed Findings",
        "xray_recs":     "Clinical Recommendations",
        "vision_title":  "Vision AI — Medical Image Q&A",
        "vision_sub":    "Upload any medical image and ask a plain-language question",
        "vision_upload": "Upload medical image",
        "vision_q":      "Your question (Arabic or English)",
        "vision_q_ph":   "e.g. What do you see in this image?",
        "vision_btn":    "Ask Vision AI",
        "chat_title":    "Health Assistant",
        "chat_sub":      "Ask health questions in Arabic or English",
        "chat_pdf":      "📎  Attach a Medical PDF (optional)",
        "chat_load":     "Load Document",
        "chat_ph":       "Ask a health question...",
        "chat_send":     "Send",
        "chat_clear":    "Clear chat",
        "chat_welcome":  "Hello! I'm Tammeny, your health assistant. Ask me anything!",
        "loading":       "Analyzing...",
        "no_file":       "Please upload a file first.",
        "svc_offline":   "Service offline",
        "risk_high":     "High Risk",
        "risk_medium":   "Medium Risk",
        "risk_low":      "Low / Normal",
        "services":      "Services",
        "online":        "online",
        "offline":       "offline",
    },
    "ar": {
        "app":           "طمّني",
        "tagline":       "التواصل الصحي بالذكاء الاصطناعي",
        "nav_home":      "الرئيسية",
        "nav_xray":      "محلل الأشعة",
        "nav_vision":    "الرؤية الذكية",
        "nav_chat":      "المساعد الصحي",
        "lang_label":    "اللغة",
        "back":          "العودة",
        "hero":          "افهم صحتك\nبلغتك.",
        "hero_sub":      "طمّني يجسر الهوة بين الذكاء الاصطناعي الطبي المعقد وفهم المريض الحقيقي — تفسيرات بلغة بسيطة، وأسئلة على الوثائق، وإرشادات صحية ذكية.",
        "c1_title":      "محلل الأشعة",
        "c1_desc":       "ارفع صورة أشعة للفحص الذكي مع نتائج بلغة بسيطة. مدعوم بنموذج DenseNet-121 المدرب على أكثر من ١٠٠ ألف صورة.",
        "c2_title":      "الرؤية الذكية",
        "c2_desc":       "ارفع أي صورة طبية واسأل سؤالاً. يشرح نموذج الرؤية ما يراه بلغة تستطيع فهمها.",
        "c3_title":      "المساعد الصحي",
        "c3_desc":       "اسأل عن صحتك واحصل على إجابات دافئة مبنية على الأدلة. ارفع ملف PDF طبي للإجابة منه.",
        "open_tool":     "",
        "stats_svc":     "خدمات ذكاء اصطناعي",
        "stats_cond":    "حالة قابلة للكشف",
        "stats_lang":    "لغتان",
        "stats_plain":   "نتائج بلغة بسيطة",
        "xray_title":    "محلل الأشعة السينية",
        "xray_sub":      "فحص ذكي لـ ١٤ حالة صدرية — مدعوم بـ DenseNet-121 / NIH ChestX-ray14",
        "xray_upload":   "ارفع صورة الأشعة (JPG / PNG)",
        "xray_thresh":   "عتبة الثقة",
        "xray_btn":      "حلّل الأشعة",
        "xray_patient":  "ملخص للمريض",
        "xray_findings": "النتائج التفصيلية",
        "xray_recs":     "التوصيات السريرية",
        "vision_title":  "الرؤية الذكية — أسئلة على الصور الطبية",
        "vision_sub":    "ارفع أي صورة طبية واسأل سؤالاً بلغتك",
        "vision_upload": "ارفع صورة طبية",
        "vision_q":      "سؤالك (عربي أو إنجليزي)",
        "vision_q_ph":   "مثال: ماذا ترى في هذه الصورة؟",
        "vision_btn":    "اسأل الذكاء الاصطناعي",
        "chat_title":    "المساعد الصحي",
        "chat_sub":      "اسأل عن صحتك بالعربية أو الإنجليزية",
        "chat_pdf":      "📎  إرفاق ملف PDF طبي (اختياري)",
        "chat_load":     "تحميل المستند",
        "chat_ph":       "اكتب سؤالك الصحي...",
        "chat_send":     "إرسال",
        "chat_clear":    "مسح المحادثة",
        "chat_welcome":  "مرحباً! أنا طمّني، مساعدك الصحي. اسألني أي شيء!",
        "loading":       "جارٍ التحليل...",
        "no_file":       "يرجى رفع ملف أولاً.",
        "svc_offline":   "الخدمة غير متاحة",
        "risk_high":     "خطر مرتفع",
        "risk_medium":   "خطر متوسط",
        "risk_low":      "منخفض / طبيعي",
        "services":      "الخدمات",
        "online":        "متصل",
        "offline":       "غير متصل",
    },
}

L   = T[st.session_state.lang]
RTL = st.session_state.lang == "ar"

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500&family=Noto+Kufi+Arabic:wght@300;400;500;600;700&display=swap');

:root {{
    --bg:        #07111f;
    --surface:   rgba(12, 26, 46, 0.85);
    --surface2:  rgba(14, 28, 56, 0.75);
    --surface3:  rgba(10, 22, 42, 0.9);
    --border:    rgba(27, 51, 84, 0.65);
    --border2:   rgba(40, 70, 110, 0.5);
    --teal:      #00d4a0;
    --teal-d:    rgba(0,212,160,0.10);
    --teal-m:    rgba(0,212,160,0.40);
    --teal-b:    rgba(0,212,160,0.20);
    --blue:      #4fa3ff;
    --blue-d:    rgba(79,163,255,0.10);
    --blue-m:    rgba(79,163,255,0.35);
    --amber:     #ffb845;
    --amber-d:   rgba(255,184,69,0.10);
    --red:       #ff6b6b;
    --red-d:     rgba(255,107,107,0.10);
    --text:      #ddeeff;
    --text2:     #b0ccdd;
    --muted:     #6a90b0;
    --faint:     #2a4a6a;
    --font:      'Sora','Noto Kufi Arabic',sans-serif;
    --mono:      'IBM Plex Mono',monospace;
    --r:         14px;
    --r-lg:      20px;
    --shadow:    0 8px 32px rgba(0,0,0,0.35);
    --shadow-teal: 0 4px 20px rgba(0,212,160,0.18);
}}

/* ── Reset & Base ── */
html, body, [data-testid="stAppViewContainer"] {{
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
}}
[data-testid="stAppViewContainer"] {{
    background:
        radial-gradient(ellipse 75% 55% at 3% 0%,  #081c38 0%, transparent 52%),
        radial-gradient(ellipse 55% 45% at 97% 95%, #071e15 0%, transparent 50%),
        radial-gradient(ellipse 40% 30% at 50% 50%, #06121e 0%, transparent 70%),
        var(--bg) !important;
}}
[data-testid="stHeader"],
[data-testid="stToolbar"],
#MainMenu {{ display:none !important; }}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: var(--surface3) !important;
    border-right: 1px solid var(--border) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
}}
[data-testid="stSidebar"] > div:first-child {{ padding:0 !important; }}

/* Hide default sidebar nav button labels (we render our own) */
[data-testid="stSidebar"] .stButton > button {{
    opacity: 0 !important;
    position: absolute !important;
    pointer-events: auto !important;
    width: 100% !important;
    height: 44px !important;
    top: 0; left: 0;
    z-index: 1;
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    transform: none !important;
    box-shadow: none !important;
}}

/* ── Main Buttons ── */
.stButton > button {{
    background: linear-gradient(135deg, var(--teal) 0%, #00b385 100%) !important;
    color: #041020 !important;
    font-family: var(--font) !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 20px !important;
    transition: all .22s cubic-bezier(.4,0,.2,1) !important;
    letter-spacing: .01em !important;
    box-shadow: 0 2px 12px rgba(0,212,160,0.15) !important;
}}
.stButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-teal) !important;
    filter: brightness(1.06) !important;
}}
.stButton > button:active {{
    transform: translateY(0px) !important;
}}

/* Back button override */
[data-testid="stMainBlockContainer"] .stButton:first-child > button {{
    background: var(--surface2) !important;
    color: var(--text2) !important;
    border: 1px solid var(--border2) !important;
    box-shadow: none !important;
    font-weight: 500 !important;
    font-size: .82rem !important;
    padding: 6px 14px !important;
}}
[data-testid="stMainBlockContainer"] .stButton:first-child > button:hover {{
    border-color: var(--teal) !important;
    color: var(--teal) !important;
    box-shadow: none !important;
}}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {{
    background: var(--surface2) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
    transition: border-color .18s, box-shadow .18s !important;
    {'text-align: right !important;' if RTL else ''}
}}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
    border-color: var(--teal) !important;
    box-shadow: 0 0 0 3px var(--teal-d) !important;
    outline: none !important;
}}

/* ── Slider ── */
.stSlider > div > div > div {{ background: var(--teal) !important; }}
.stSlider [data-testid="stThumbValue"] {{ color: var(--teal) !important; font-family: var(--mono) !important; }}

/* ── File uploader ── */
[data-testid="stFileUploader"] {{
    background: var(--surface2) !important;
    border: 2px dashed var(--border2) !important;
    border-radius: var(--r-lg) !important;
    transition: border-color .18s !important;
}}
[data-testid="stFileUploader"]:hover {{ border-color: var(--teal) !important; }}
[data-testid="stFileUploader"] p {{ color: var(--muted) !important; }}

/* ── Expander ── */
.streamlit-expanderHeader {{
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    color: var(--text2) !important;
    font-family: var(--font) !important;
}}
.streamlit-expanderContent {{
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 var(--r) var(--r) !important;
}}

/* ── Spinner ── */
.stSpinner > div {{ border-top-color: var(--teal) !important; }}

/* ── Alerts ── */
.stAlert {{
    background: var(--surface2) !important;
    border-radius: var(--r) !important;
    border: 1px solid var(--border) !important;
}}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width:5px; height:5px; }}
::-webkit-scrollbar-track {{ background:transparent; }}
::-webkit-scrollbar-thumb {{ background:var(--faint); border-radius:3px; }}
::-webkit-scrollbar-thumb:hover {{ background:var(--muted); }}

/* ── Chat input row ── */
.chat-input-row {{
    display: flex;
    gap: 10px;
    align-items: flex-end;
    margin-top: 8px;
}}

/* ── Tooltip ── */
[title]:hover::after {{
    content: attr(title);
    position: absolute;
    background: var(--surface3);
    color: var(--text2);
    font-size: .72rem;
    padding: 4px 8px;
    border-radius: 6px;
    border: 1px solid var(--border);
    white-space: nowrap;
    pointer-events: none;
    z-index: 999;
}}

/* ── Fade-in animation ── */
@keyframes fadeUp {{
    from {{ opacity:0; transform:translateY(14px); }}
    to   {{ opacity:1; transform:translateY(0); }}
}}
.fade-up {{ animation: fadeUp .4s cubic-bezier(.4,0,.2,1) both; }}

/* ── Lang toggle pill ── */
.lang-pill {{
    display: inline-flex;
    align-items: center;
    gap: 0;
    background: var(--surface2);
    border: 1.5px solid var(--border2);
    border-radius: 50px;
    overflow: hidden;
    height: 36px;
}}
.lang-option {{
    padding: 0 14px;
    font-family: var(--font);
    font-size: .78rem;
    font-weight: 600;
    color: var(--muted);
    cursor: pointer;
    height: 100%;
    display: flex;
    align-items: center;
    gap: 5px;
    transition: all .18s;
    user-select: none;
    white-space: nowrap;
}}
.lang-option.active {{
    background: linear-gradient(135deg, var(--teal) 0%, #00b385 100%);
    color: #041020;
}}
.lang-option:not(.active):hover {{
    color: var(--text2);
    background: var(--surface);
}}
</style>
""", unsafe_allow_html=True)


# ── HTML helpers ──────────────────────────────────────────────────────────────

def _rtl(extra=""):
    return f'direction:rtl;text-align:right;{extra}' if RTL else extra


def back_button():
    if st.session_state.page != "home":
        col1, _ = st.columns([1, 9])
        with col1:
            lbl = ("→ " if RTL else "← ") + L["back"]
            if st.button(lbl, key="global_back_btn"):
                st.session_state.page = st.session_state.prev_page
                st.session_state.prev_page = "home"
                st.rerun()


def section_header(title, sub=""):
    st.markdown(f"""
    <div class="fade-up" style="margin-bottom:28px;padding-bottom:16px;
                border-bottom:1px solid var(--border);{_rtl()}">
        <h2 style="font-family:var(--font);font-size:1.6rem;font-weight:800;
                   color:var(--text);margin:0 0 6px;letter-spacing:-.01em;">{title}</h2>
        <p style="color:var(--muted);font-size:0.85rem;margin:0;line-height:1.6;">{sub}</p>
    </div>""", unsafe_allow_html=True)


def card(icon, title, desc, color="teal"):
    c_map = {
        "teal":  ("var(--teal)",  "var(--teal-d)",  "var(--teal-m)"),
        "blue":  ("var(--blue)",  "var(--blue-d)",  "var(--blue-m)"),
        "amber": ("var(--amber)", "var(--amber-d)", "rgba(255,184,69,0.3)"),
    }[color]
    st.markdown(f"""
    <div class="fade-up" style="background:var(--surface);border:1px solid var(--border);
                border-radius:var(--r-lg);padding:24px;height:100%;position:relative;
                overflow:hidden;transition:border-color .2s,transform .2s;
                box-shadow:var(--shadow);">
        <div style="position:absolute;top:0;right:0;width:90px;height:90px;
                    background:radial-gradient(circle at top right,{c_map[1]},transparent 68%);
                    border-radius:0 var(--r-lg) 0 0;"></div>
        <div style="position:absolute;bottom:-30px;left:-20px;width:80px;height:80px;
                    background:radial-gradient(circle,{c_map[1]},transparent 70%);
                    filter:blur(20px);"></div>
        <div style="font-size:1.8rem;margin-bottom:12px;">{icon}</div>
        <div style="font-weight:700;font-size:.95rem;color:{c_map[0]};margin-bottom:8px;
                    letter-spacing:-.01em;">{title}</div>
        <div style="color:var(--muted);font-size:.83rem;line-height:1.7;">{desc}</div>
    </div>""", unsafe_allow_html=True)


def result_panel(title, body, color="teal", icon="✦"):
    c = {"teal": "var(--teal)", "blue": "var(--blue)",
         "amber": "var(--amber)", "red": "var(--red)"}[color]
    st.markdown(f"""
    <div class="fade-up" style="background:var(--surface2);border:1px solid {c}28;
                border-left:4px solid {c};border-radius:var(--r);
                padding:18px 22px;margin-top:14px;{_rtl()}">
        <div style="color:{c};font-size:.7rem;font-weight:700;
                    letter-spacing:.12em;text-transform:uppercase;margin-bottom:10px;
                    display:flex;align-items:center;gap:6px;">
            <span>{icon}</span><span>{title}</span>
        </div>
        <div style="color:var(--text);font-size:.9rem;line-height:1.75;
                    white-space:pre-wrap;">{body}</div>
    </div>""", unsafe_allow_html=True)


def risk_badge(risk: str):
    meta = {
        "high":   (L["risk_high"],   "var(--red)",   "var(--red-d)",   "🔴"),
        "medium": (L["risk_medium"], "var(--amber)",  "var(--amber-d)", "🟡"),
        "low":    (L["risk_low"],    "var(--teal)",   "var(--teal-d)",  "🟢"),
    }.get(risk, (risk, "var(--muted)", "var(--surface2)", "⚪"))
    st.markdown(f"""
    <div style="display:inline-flex;align-items:center;gap:10px;
                background:{meta[2]};border:1px solid {meta[1]}55;
                border-radius:50px;padding:8px 18px;margin:14px 0;">
        <span style="width:9px;height:9px;border-radius:50%;background:{meta[1]};
                     box-shadow:0 0 10px {meta[1]};display:inline-block;
                     animation:pulse 2s ease-in-out infinite;"></span>
        <span style="color:{meta[1]};font-weight:700;font-size:.84rem;
                     letter-spacing:.03em;">{meta[0]}</span>
    </div>
    <style>
    @keyframes pulse {{
        0%,100% {{ opacity:1; transform:scale(1); }}
        50%      {{ opacity:.6; transform:scale(1.15); }}
    }}
    </style>""", unsafe_allow_html=True)


def chat_bubble(role, content):
    if role == "user":
        align = "flex-end"
        bubble_style = (
            "background:linear-gradient(135deg,#0d3562,#092646);"
            "border:1px solid rgba(79,163,255,.25);"
            f"border-radius:18px 18px {'3px 18px' if not RTL else '18px 3px'};"
            f"color:var(--text);{_rtl()}"
        )
    else:
        align = "flex-start"
        bubble_style = (
            "background:var(--surface2);"
            "border:1px solid var(--border);"
            f"border-radius:18px 18px {'18px 3px' if not RTL else '3px 18px'};"
            f"color:var(--text);{_rtl()}"
        )
    label = f'<span style="color:var(--teal);font-size:.7rem;font-weight:700;display:block;margin-bottom:5px;">🩺 {L["app"]}</span>' if role == "assistant" else ""
    st.markdown(f"""
    <div style="display:flex;justify-content:{align};margin-bottom:12px;">
        <div style="{bubble_style}padding:12px 16px;max-width:74%;
                    font-size:.88rem;line-height:1.68;box-shadow:var(--shadow);">
            {label}{content}
        </div>
    </div>""", unsafe_allow_html=True)


# ── Language Toggle (inline pill) ─────────────────────────────────────────────

def lang_toggle_pill():
    """Render a visual EN | AR pill; clicking triggers a toggle button underneath."""
    en_active = "active" if st.session_state.lang == "en" else ""
    ar_active  = "active" if st.session_state.lang == "ar"  else ""
    st.markdown(f"""
    <div style="padding:14px 18px 4px;">
        <div style="font-size:.65rem;text-transform:uppercase;letter-spacing:.1em;
                    color:var(--faint);margin-bottom:8px;">{L['lang_label']}</div>
        <div class="lang-pill">
            <div class="lang-option {en_active}">🇬🇧 EN</div>
            <div class="lang-option {ar_active}">🇸🇦 AR</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Actual functional button — invisible overlay handled by CSS above
    c1, c2 = st.sidebar.columns(2)
    with c1:
        if st.button("🇬🇧 EN", key="lang_en",
                     disabled=(st.session_state.lang == "en"),
                     use_container_width=True):
            st.session_state.lang = "en"
            st.rerun()
    with c2:
        if st.button("🇸🇦 AR", key="lang_ar",
                     disabled=(st.session_state.lang == "ar"),
                     use_container_width=True):
            st.session_state.lang = "ar"
            st.rerun()


# ── Callbacks & Logic ──────────────────────────────────────────────────────────

def handle_chat_logic():
    user_text = st.session_state.chat_input_field.strip()
    if not user_text:
        return
    st.session_state.chat_input_field = ""
    st.session_state.chat_history.append({"role": "user", "content": user_text})

    # Detect the language of the user's message automatically.
    # Simple heuristic: if majority of letters are Arabic script → Arabic, else English.
    arabic_chars = sum(1 for c in user_text if '\u0600' <= c <= '\u06ff')
    detected_lang = "Arabic" if arabic_chars > len(user_text) * 0.3 else "English"

    # Prepend a language-enforcement instruction so the backend always replies
    # in the same language the user typed, regardless of the app's UI language.
    lang_instruction = (
        f"IMPORTANT: The user wrote in {detected_lang}. "
        f"You MUST reply ENTIRELY in {detected_lang}. Do not mix languages.\n\n"
    )
    prompted_text = lang_instruction + user_text

    try:
        r = requests.post(
            f"{CHATBOT_URL}/chat",
            json={"prompt": prompted_text, "session_id": st.session_state.session_id},
            timeout=40,
        )
        answer = (r.json().get("answer") or r.json().get("response")) if r.status_code == 200 else f"Error {r.status_code}"
    except Exception:
        answer = f"⚠️ {L['svc_offline']}"
    st.session_state.chat_history.append({"role": "assistant", "content": answer})


# ── Sidebar ───────────────────────────────────────────────────────────────────

def sidebar():
    # ── Logo
    st.sidebar.markdown(f"""
    <div style="padding:24px 18px 16px;border-bottom:1px solid var(--border);">
        <div style="display:flex;align-items:center;gap:11px;margin-bottom:6px;">
            <div style="width:36px;height:36px;border-radius:10px;
                        background:linear-gradient(135deg,var(--teal),var(--blue));
                        display:flex;align-items:center;justify-content:center;
                        font-size:1.1rem;box-shadow:0 4px 14px var(--teal-m);">🩺</div>
            <span style="font-family:var(--font);font-size:1.3rem;font-weight:800;
                         background:linear-gradient(135deg,var(--teal) 30%,var(--blue));
                         -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                {L['app']}
            </span>
        </div>
        <div style="color:var(--muted);font-size:.68rem;letter-spacing:.1em;
                    text-transform:uppercase;padding-left:3px;">{L['tagline']}</div>
    </div>""", unsafe_allow_html=True)

    st.sidebar.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Navigation
    nav = [
        (L["nav_home"],   "🏠", "home",   "var(--teal)"),
        (L["nav_xray"],   "🔬", "xray",   "var(--teal)"),
        (L["nav_vision"], "👁", "vision", "var(--blue)"),
        (L["nav_chat"],   "💬", "chat",   "var(--amber)"),
    ]
    for label, icon, key, accent in nav:
        active = st.session_state.page == key
        bg     = f"background:linear-gradient(90deg,{accent}18,transparent);" if active else ""
        border = f"border-left:3px solid {accent};color:{accent};" if active else "border-left:3px solid transparent;color:var(--muted);"
        st.sidebar.markdown(f"""
        <div style="position:relative;padding:10px 18px;font-family:var(--font);
                    font-size:.85rem;font-weight:{'600' if active else '400'};
                    display:flex;align-items:center;gap:10px;
                    {border}{bg}transition:all .15s;border-radius:0 8px 8px 0;
                    margin:0 8px 2px 0;">
            <span style="font-size:1rem;">{icon}</span>
            <span>{label}</span>
            {'<span style="margin-left:auto;width:6px;height:6px;border-radius:50%;background:' + accent + ';box-shadow:0 0 8px ' + accent + ';"></span>' if active else ''}
        </div>""", unsafe_allow_html=True)
        if st.sidebar.button(label, key=f"nav_{key}", use_container_width=True):
            if st.session_state.page != key:
                st.session_state.prev_page = st.session_state.page
                st.session_state.page = key
            st.rerun()

    # ── Language Selector
    st.sidebar.markdown("""
    <div style='height:8px'></div>
    <div style='height:1px;background:var(--border);margin:0 16px'></div>""",
    unsafe_allow_html=True)

    st.sidebar.markdown(f"""
    <div style="padding:12px 18px 6px;">
        <div style="font-size:.65rem;text-transform:uppercase;letter-spacing:.1em;
                    color:var(--faint);margin-bottom:10px;">🌐 {L['lang_label']}</div>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.sidebar.columns(2)
    en_style = "border:1.5px solid var(--teal) !important;color:var(--teal) !important;" if st.session_state.lang == "en" else ""
    ar_style = "border:1.5px solid var(--teal) !important;color:var(--teal) !important;" if st.session_state.lang == "ar"  else ""
    with c1:
        if st.button("🇬🇧  EN", key="lang_en",
                     disabled=(st.session_state.lang == "en"),
                     use_container_width=True,
                     help="Switch to English"):
            st.session_state.lang = "en"
            st.rerun()
    with c2:
        if st.button("🇸🇦  AR", key="lang_ar",
                     disabled=(st.session_state.lang == "ar"),
                     use_container_width=True,
                     help="التبديل إلى العربية"):
            st.session_state.lang = "ar"
            st.rerun()

    # ── Service Status
    def dot(alive, label):
        color  = "var(--teal)" if alive else "var(--amber)"
        status = L["online"] if alive else L["offline"]
        return (f'<div style="display:flex;align-items:center;justify-content:space-between;'
                f'font-size:.76rem;padding:5px 0;">'
                f'<span style="color:var(--text2);display:flex;align-items:center;gap:7px;">'
                f'<span style="width:7px;height:7px;border-radius:50%;background:{color};'
                f'box-shadow:0 0 6px {color};display:inline-block;flex-shrink:0;"></span>{label}</span>'
                f'<span style="color:{color};font-size:.68rem;font-family:var(--mono);">{status}</span>'
                f'</div>')

    def ping(url):
        try:
            requests.get(url, timeout=1.2)
            return True
        except Exception:
            return False

    st.sidebar.markdown("""
    <div style='height:8px'></div>
    <div style='height:1px;background:var(--border);margin:0 16px'></div>""",
    unsafe_allow_html=True)
    st.sidebar.markdown(f"""
    <div style="padding:14px 18px 18px;">
        <div style="font-size:.65rem;color:var(--faint);text-transform:uppercase;
                    letter-spacing:.1em;margin-bottom:10px;">{L['services']}</div>
        {dot(ping(CHATBOT_URL), "Chatbot")}
        {dot(ping(VISION_URL),  "Vision AI")}
        {dot(ping(IMAGING_URL), "Imaging")}
    </div>""", unsafe_allow_html=True)


# ── Pages ─────────────────────────────────────────────────────────────────────

def page_home():
    dir_attr = 'rtl' if RTL else 'ltr'
    st.markdown(f"""
    <div style="padding:40px 0 28px;{_rtl()};" class="fade-up">
        <div style="font-size:.7rem;font-weight:700;letter-spacing:.18em;
                    text-transform:uppercase;color:var(--teal);margin-bottom:16px;
                    display:flex;align-items:center;gap:8px;">
            <span style="display:inline-block;width:22px;height:1px;
                         background:var(--teal);opacity:.6;"></span>
            Healthcare AI Platform
            <span style="display:inline-block;width:22px;height:1px;
                         background:var(--teal);opacity:.6;"></span>
        </div>
        <h1 style="font-family:var(--font);font-size:clamp(2rem,4.5vw,3rem);
                   font-weight:800;line-height:1.12;color:var(--text);
                   margin:0 0 20px;white-space:pre-line;letter-spacing:-.02em;">{L['hero']}</h1>
        <p style="font-size:.97rem;color:var(--muted);max-width:560px;
                  line-height:1.82;margin:0 0 38px;">{L['hero_sub']}</p>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        card("🔬", L["c1_title"], L["c1_desc"], "teal")
        if st.button(L["open_tool"] + "  " + L["nav_xray"], key="h_xray", use_container_width=True):
            st.session_state.prev_page = "home"
            st.session_state.page = "xray"; st.rerun()
    with c2:
        card("👁", L["c2_title"], L["c2_desc"], "blue")
        if st.button(L["open_tool"] + "  " + L["nav_vision"], key="h_vis", use_container_width=True):
            st.session_state.prev_page = "home"
            st.session_state.page = "vision"; st.rerun()
    with c3:
        card("💬", L["c3_title"], L["c3_desc"], "amber")
        if st.button(L["open_tool"] + "  " + L["nav_chat"], key="h_chat", use_container_width=True):
            st.session_state.prev_page = "home"
            st.session_state.page = "chat"; st.rerun()

    st.markdown(f"""
    <div style="margin-top:36px;padding:20px 28px;
                background:var(--surface);border:1px solid var(--border);
                border-radius:var(--r-lg);display:flex;gap:40px;
                align-items:center;flex-wrap:wrap;box-shadow:var(--shadow);{_rtl()}">
        <div><div style="font-size:1.5rem;font-weight:800;color:var(--teal);
                         font-family:var(--mono);">3</div>
             <div style="font-size:.72rem;color:var(--muted);margin-top:2px;">{L['stats_svc']}</div></div>
        <div style="width:1px;height:34px;background:var(--border);"></div>
        <div><div style="font-size:1.5rem;font-weight:800;color:var(--blue);
                         font-family:var(--mono);">14</div>
             <div style="font-size:.72rem;color:var(--muted);margin-top:2px;">{L['stats_cond']}</div></div>
        <div style="width:1px;height:34px;background:var(--border);"></div>
        <div><div style="font-size:1.5rem;font-weight:800;color:var(--amber);
                         font-family:var(--mono);">2</div>
             <div style="font-size:.72rem;color:var(--muted);margin-top:2px;">{L['stats_lang']}</div></div>
        <div style="width:1px;height:34px;background:var(--border);"></div>
        <div><div style="font-size:1.5rem;font-weight:800;color:var(--teal);
                         font-family:var(--mono);">✓</div>
             <div style="font-size:.72rem;color:var(--muted);margin-top:2px;">{L['stats_plain']}</div></div>
    </div>""", unsafe_allow_html=True)


# ── X-Ray page ─────────────────────────────────────────────────────────────────

def page_xray():
    back_button()
    section_header(L["xray_title"], L["xray_sub"])
    col_up, col_res = st.columns([1, 1], gap="large")

    with col_up:
        st.markdown(f"<div style='color:var(--muted);font-size:.8rem;margin-bottom:6px;{_rtl()}'>{L['xray_upload']}</div>",
                    unsafe_allow_html=True)
        img_file = st.file_uploader("", type=["jpg", "jpeg", "png"],
                                     key="xray_file", label_visibility="collapsed")
        if img_file:
            st.image(img_file, use_container_width=True)

        thresh = st.slider(L["xray_thresh"], 0.1, 0.9, 0.5, 0.05, key="xray_thresh")
        run_btn = st.button(L["xray_btn"], key="xray_run", use_container_width=True)

    with col_res:
        if run_btn:
            if not img_file:
                st.error(L["no_file"])
                return
            with st.spinner(L["loading"]):
                try:
                    files  = {"file": (img_file.name, img_file.getvalue(), img_file.type)}
                    params = {"confidence_threshold": thresh}
                    r = requests.post(f"{IMAGING_URL}/analyze/xray",
                                      files=files, params=params, timeout=40)
                    if r.status_code == 200:
                        _render_xray_result(r.json())
                    else:
                        st.error(f"Service error {r.status_code}: {r.text[:200]}")
                except requests.exceptions.ConnectionError:
                    st.warning(f"⚠️ {L['svc_offline']} — showing demo result.")
                    _render_xray_demo()
                except Exception as e:
                    st.error(str(e))


def _render_xray_result(data: dict):
    risk = data.get("overall_risk_level", "low")
    risk_badge(risk)
    result_panel(L["xray_patient"],  data.get("patient_summary", ""), "teal", "💡")

    df = data.get("detailed_findings", {})
    lines = []
    for sev, emoji in [("high_severity", "🚨"), ("medium_severity", "⚠️"), ("low_severity", "ℹ️")]:
        for f in df.get(sev, []):
            lines.append(f"{emoji} {f['condition']} — {f['confidence_percent']}")
            if "plain_language" in f:
                lines.append(f"   ↳ {f['plain_language']}")
    if lines:
        result_panel(L["xray_findings"], "\n".join(lines), "blue", "🔬")

    recs = data.get("clinical_recommendations", [])
    if recs:
        result_panel(L["xray_recs"], "\n".join(f"• {r}" for r in recs), "amber", "📋")

    st.markdown(f"""
    <div style="margin-top:14px;font-size:.72rem;color:var(--faint);
                padding:10px 14px;border:1px solid var(--border);
                border-radius:8px;">{data.get('disclaimer','')}</div>""",
                unsafe_allow_html=True)


def _render_xray_demo():
    fake = {
        "overall_risk_level": "low",
        "patient_summary": "✅ No significant findings detected. Your X-ray looks normal based on this AI scan. Always confirm results with your doctor.",
        "detailed_findings": {"high_severity": [], "medium_severity": [], "low_severity": []},
        "clinical_recommendations": [
            "Routine follow-up as recommended by your healthcare provider.",
            "Continue with regular health monitoring.",
            "No immediate intervention needed based on this analysis.",
        ],
        "disclaimer": "This AI analysis is for preliminary screening only and is NOT a medical diagnosis.",
    }
    _render_xray_result(fake)


# ── Vision AI page ─────────────────────────────────────────────────────────────

def page_vision():
    back_button()
    section_header(L["vision_title"], L["vision_sub"])
    col_up, col_res = st.columns([1, 1], gap="large")

    with col_up:
        st.markdown(f"<div style='color:var(--muted);font-size:.8rem;margin-bottom:6px;{_rtl()}'>{L['vision_upload']}</div>",
                    unsafe_allow_html=True)
        img_file = st.file_uploader("", type=["jpg", "jpeg", "png"],
                                     key="vis_file", label_visibility="collapsed")
        if img_file:
            st.image(img_file, use_container_width=True)

        question = st.text_area(L["vision_q"], placeholder=L["vision_q_ph"],
                                 key="vis_q", height=90)
        ask_btn = st.button(L["vision_btn"], key="vis_run", use_container_width=True)

    with col_res:
        if ask_btn:
            if not img_file:
                st.error(L["no_file"])
                return
            prompt = question.strip() or (
                "صف ما تراه في هذه الصورة الطبية بلغة بسيطة." if RTL
                else "Please describe what you see in this medical image in simple language."
            )
            with st.spinner(L["loading"]):
                try:
                    files = {"image": (img_file.name, img_file.getvalue(), img_file.type)}
                    data  = {"human_prompt": prompt}
                    r = requests.post(f"{VISION_URL}/analyze_image/",
                                      files=files, data=data, timeout=50)
                    if r.status_code == 200:
                        reply = r.json().get("response", {})
                        text  = reply.get("content", reply) if isinstance(reply, dict) else str(reply)
                        result_panel("Vision AI Response", text, "blue", "👁")
                    else:
                        st.error(f"Service error {r.status_code}: {r.text[:200]}")
                except requests.exceptions.ConnectionError:
                    st.warning(f"⚠️ {L['svc_offline']}")


# ── Chat page ──────────────────────────────────────────────────────────────────

def page_chat():
    back_button()
    section_header(L["chat_title"], L["chat_sub"])

    # PDF upload expander
    with st.expander(L["chat_pdf"], expanded=False):
        pdf = st.file_uploader("", type=["pdf"], key="chat_pdf_file",
                                label_visibility="collapsed")
        if st.button(L["chat_load"], key="load_pdf_btn") and pdf:
            with st.spinner("Loading..."):
                try:
                    files = {"file": (pdf.name, pdf.getvalue(), "application/pdf")}
                    data  = {"session_id": st.session_state.session_id}
                    r = requests.post(f"{CHATBOT_URL}/load_pdf/",
                                      files=files, data=data, timeout=40)
                    if r.status_code == 200:
                        st.success("✅ " + r.json().get("message", "Loaded!"))
                    else:
                        st.error("Failed to load document.")
                except Exception:
                    st.error(f"⚠️ {L['svc_offline']}")

    # Chat history
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            chat_bubble("assistant", L["chat_welcome"])
        else:
            for msg in st.session_state.chat_history:
                chat_bubble(msg["role"], msg["content"])

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # Input row
    col_in, col_send = st.columns([6, 1])
    with col_in:
        st.text_input(
            "", placeholder=L["chat_ph"],
            key="chat_input_field",
            on_change=handle_chat_logic,
            label_visibility="collapsed",
        )
    with col_send:
        st.button(
            L["chat_send"], key="chat_send_btn",
            on_click=handle_chat_logic,
            use_container_width=True,
        )

    # Clear button — subtle, below the input
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    _, col_clr = st.columns([5, 1])
    with col_clr:
        if st.button("🗑 " + L["chat_clear"], key="chat_clear_btn", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()


# ── Top bar ───────────────────────────────────────────────────────────────────

def top_lang_bar():
    en_active = st.session_state.lang == "en"
    ar_active  = st.session_state.lang == "ar"

    st.markdown(f"""
    <style>
    .top-lang-bar {{
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding: 9px 8px 9px 16px;
        border-bottom: 1px solid var(--border);
        background: rgba(7,17,31,0.92);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        gap: 6px;
        margin-bottom: 4px;
    }}
    .tlb-label {{
        font-size: .7rem;
        color: var(--faint);
        letter-spacing: .1em;
        text-transform: uppercase;
        margin-right: 8px;
        font-family: var(--font);
    }}
    .tlb-pill {{
        display: inline-flex;
        border-radius: 50px;
        border: 1.5px solid var(--border2);
        overflow: hidden;
        background: var(--surface2);
    }}
    .tlb-opt {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 15px;
        font-family: var(--font);
        font-size: .79rem;
        font-weight: 600;
        color: var(--muted);
        transition: all .16s;
    }}
    .tlb-opt.on {{
        background: linear-gradient(135deg, var(--teal) 0%, #00b385 100%);
        color: #041020;
    }}
    </style>
    <div class="top-lang-bar">
        <span class="tlb-label">🌐</span>
        <div class="tlb-pill">
            <span class="tlb-opt {'on' if en_active else ''}">🇬🇧 English</span>
            <span class="tlb-opt {'on' if ar_active else ''}">🇸🇦 العربية</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_gap, col_en, col_ar = st.columns([7.2, 0.9, 0.9])
    with col_en:
        if st.button("EN", key="topbar_lang_en", disabled=en_active,
                     use_container_width=True, help="Switch to English"):
            st.session_state.lang = "en"
            st.rerun()
    with col_ar:
        if st.button("AR", key="topbar_lang_ar", disabled=ar_active,
                     use_container_width=True, help="التبديل إلى العربية"):
            st.session_state.lang = "ar"
            st.rerun()

    st.markdown("""
    <style>
    /* Overlap real buttons behind the visual bar */
    [data-testid="stMainBlockContainer"] > div:nth-child(2) {
        margin-top: -52px !important;
        position: relative;
        z-index: 5;
    }
    [data-testid="stMainBlockContainer"] > div:nth-child(2) .stButton > button {
        opacity: 0 !important;
        height: 40px !important;
        border: none !important;
        box-shadow: none !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ── Layout ────────────────────────────────────────────────────────────────────

sidebar()
top_lang_bar()

st.markdown("<div style='padding:1rem 2.5rem 5rem;'>", unsafe_allow_html=True)
{
    "home":   page_home,
    "xray":   page_xray,
    "vision": page_vision,
    "chat":   page_chat,
}[st.session_state.page]()
st.markdown("</div>", unsafe_allow_html=True)