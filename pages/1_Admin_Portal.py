"""
Admin_Portal.py — Dedicated URL Page for State Emergency Operations Command (SEOC)
Accessible directly at: /Admin_Portal or /1_Admin_Portal
"""

import streamlit as st
from translations import t
from admin_view import render_admin_dashboard
import sample_data

st.set_page_config(
    page_title="उत्तराखंड SEOC नियंत्रण कक्ष | State Emergency Operations Command",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "lang" not in st.session_state:
    st.session_state["lang"] = "en"

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:12px 0 10px;">
        <div style="display:inline-flex;align-items:center;justify-content:center;width:44px;height:44px;background:linear-gradient(135deg, #1E3A8A 0%, #1E40AF 100%);border-radius:12px;margin-bottom:8px;box-shadow:0 0 16px rgba(59,130,246,0.5);">
            <span style="font-size:1.4rem;">🏛️</span>
        </div>
        <div style="font-size:1.0rem;font-weight:900;color:#F8FAFC;line-height:1.2;">SEOC उत्तराखंड</div>
        <div style="font-size:0.72rem;color:#38BDF8;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;margin-top:2px;">Disaster Incident Command</div>
    </div>
    """, unsafe_allow_html=True)

    lang_choice = st.radio(
        "🌐 भाषा / Language",
        options=["hi", "en"],
        format_func=lambda x: "🇮🇳 हिंदी" if x == "hi" else "🇬🇧 English",
        index=0 if st.session_state["lang"] == "hi" else 1,
        horizontal=True,
        key="admin_page_lang_radio"
    )
    st.session_state["lang"] = lang_choice
    is_hi = (lang_choice == "hi")

    if st.button("🔄 " + ("लाइव डेटा रीफ्रेश करें" if is_hi else "Refresh Emergency Feeds"), use_container_width=True):
        st.rerun()

    st.markdown("<hr style='border-color:rgba(255,255,255,0.06);margin:14px 0 10px;'>", unsafe_allow_html=True)
    st.markdown("🔗 [← " + ("नागरिक पब्लिक पोर्टल पर जाएं" if is_hi else "Back to Citizen Public Portal") + "](/?page=home)")

render_admin_dashboard(st.session_state["lang"], is_hi)
