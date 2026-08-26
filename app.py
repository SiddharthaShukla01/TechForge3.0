import streamlit as st
import pandas as pd
import os
import urllib.parse
import altair as alt
from datetime import datetime
import weather as wx

os.makedirs("uploads", exist_ok=True)


from database import (
    create_tables, add_disaster, add_custom_alert, get_all_disasters,
    get_shelters_by_district, get_hospitals_by_district, get_resources_by_district,
    get_all_alerts, update_disaster_status, update_hospital_beds,
    update_shelter_occupancy, get_dashboard_summary, add_suggestion,
    get_all_suggestions, upvote_suggestion, DISTRICT_NAMES_MAP, ALL_DISTRICTS
)
from translations import (t, DISASTER_TYPE_TRANSLATIONS, SEVERITY_TRANSLATIONS, STATUS_TRANSLATIONS)
import sample_data

create_tables()

st.set_page_config(
    page_title="उत्तराखंड आपदा राहत | Uttarakhand Disaster Relief",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────────────
# COMPREHENSIVE CSS OVERHAUL
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── 1. GLOBAL DARK THEME ───────────────────────────────────────────────── */
.stApp {
    background: #070C18 !important;
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
}
.main .block-container {
    padding: 1.4rem 2.2rem 2rem;
    max-width: 1440px;
}

/* ── 2. SIDEBAR ─────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] > div:first-child {
    background: linear-gradient(180deg, #0A0F1D 0%, #0E1626 50%, #080D18 100%) !important;
    border-right: 1px solid rgba(59,130,246,0.15) !important;
    box-shadow: 4px 0 24px rgba(0,0,0,0.4) !important;
}
section[data-testid="stSidebar"] * { color: #CBD5E1 !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #F8FAFC !important; }
section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.07) !important; }

/* ── 2A. SIDEBAR NAVIGATION TILES ─────────────────────────────────────────── */
section[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] {
    gap: 0.45rem !important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] > label > div:first-child {
    display: none !important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] > label {
    background: rgba(30, 41, 59, 0.4) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 12px !important;
    padding: 0.75rem 1rem !important;
    cursor: pointer !important;
    transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
    display: flex !important;
    align-items: center !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2) !important;
    margin-bottom: 2px !important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] > label:hover {
    background: rgba(59, 130, 246, 0.12) !important;
    border-color: rgba(59, 130, 246, 0.35) !important;
    transform: translateX(4px) !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3) !important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] > label:hover p {
    color: #F8FAFC !important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] > label:has(input:checked) {
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.3) 0%, rgba(30, 58, 138, 0.22) 100%) !important;
    border: 1px solid rgba(59, 130, 246, 0.6) !important;
    border-left: 5px solid #3B82F6 !important;
    box-shadow: 0 4px 16px rgba(37, 99, 235, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.12) !important;
    transform: translateX(3px) !important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] > label:has(input:checked) p {
    color: #93C5FD !important;
    font-weight: 800 !important;
    letter-spacing: 0.01em !important;
}

/* ── 2B. LANGUAGE TOGGLE SWITCH ─────────────────────────────────────────── */
section[data-testid="stSidebar"] [data-testid="stRadio"]:first-of-type [role="radiogroup"] {
    display: flex !important;
    flex-direction: row !important;
    background: rgba(15, 23, 42, 0.8) !important;
    padding: 4px !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    gap: 4px !important;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.3) !important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"]:first-of-type [role="radiogroup"] > label {
    flex: 1 !important;
    justify-content: center !important;
    padding: 6px 10px !important;
    margin-bottom: 0 !important;
    border-radius: 8px !important;
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    transform: none !important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"]:first-of-type [role="radiogroup"] > label:hover {
    background: rgba(255, 255, 255, 0.06) !important;
    transform: none !important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"]:first-of-type [role="radiogroup"] > label:has(input:checked) {
    background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
    border-left: none !important;
    box-shadow: 0 2px 10px rgba(37, 99, 235, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
    transform: none !important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"]:first-of-type [role="radiogroup"] > label:has(input:checked) p {
    color: #FFFFFF !important;
    font-weight: 800 !important;
}

/* ── 3. HEADINGS & TEXT ─────────────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6, p, label, span, div { color: #E2E8F0; }
[data-testid="stMarkdownContainer"] p { color: #CBD5E1; }

/* ── 4. METRICS ─────────────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1A2744 0%, #0F1C38 100%) !important;
    border: 1px solid rgba(59,130,246,0.15) !important;
    border-radius: 14px !important;
    padding: 1rem 1.2rem !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.4) !important;
}
[data-testid="stMetricValue"] { color: #F1F5F9 !important; font-weight: 800 !important; font-size: 1.8rem !important; }
[data-testid="stMetricLabel"] { color: #94A3B8 !important; font-size: 0.82rem !important; font-weight: 600 !important; letter-spacing: 0.03em !important; text-transform: uppercase; }
[data-testid="stMetricDelta"] { font-size: 0.82rem !important; font-weight: 600 !important; }

/* ── 5. BUTTONS ─────────────────────────────────────────────────────────── */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.03em !important;
    transition: all 0.2s ease !important;
    border: none !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%) !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(220,38,38,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(220,38,38,0.5) !important;
    background: linear-gradient(135deg, #EF4444 0%, #B91C1C 100%) !important;
}
.stButton > button[kind="secondary"] {
    background: rgba(30,41,59,0.9) !important;
    color: #CBD5E1 !important;
    border: 1px solid #334155 !important;
}
.stButton > button[kind="secondary"]:hover {
    background: rgba(51,65,85,0.9) !important;
    border-color: #475569 !important;
}

/* ── 6. FORM INPUTS ─────────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
    background: #1A2035 !important;
    border: 1px solid #2D3D55 !important;
    border-radius: 8px !important;
    color: #F1F5F9 !important;
    font-size: 0.92rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 2px rgba(59,130,246,0.2) !important;
}
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: #1A2035 !important;
    border: 1px solid #2D3D55 !important;
    border-radius: 8px !important;
    color: #F1F5F9 !important;
}
.stSelectbox > div > div:focus-within { border-color: #3B82F6 !important; }
[data-baseweb="select"] > div { background: #1A2035 !important; border-color: #2D3D55 !important; }
[data-baseweb="popover"] { background: #1A2035 !important; border: 1px solid #334155 !important; }
[data-baseweb="menu"] { background: #1A2035 !important; }
[data-baseweb="option"]:hover { background: #243352 !important; }

/* ── 7. GENERAL RADIO BUTTONS ───────────────────────────────────────────── */
[data-testid="stRadio"] > div { gap: 0.4rem; }
[data-testid="stRadio"] label {
    background: rgba(30,41,59,0.7) !important;
    border: 1px solid #2D3D55 !important;
    border-radius: 8px !important;
    padding: 0.5rem 1rem !important;
    cursor: pointer !important;
    transition: all 0.15s !important;
}
[data-testid="stRadio"] label:has(input:checked) {
    background: rgba(59,130,246,0.15) !important;
    border-color: #3B82F6 !important;
    color: #93C5FD !important;
}

/* ── 8. MODERN PAGE SELECTION TABS ───────────────────────────────────────── */
[data-testid="stTabs"] {
    margin-top: 8px !important;
}
[data-testid="stTabs"] [role="tablist"] {
    background: rgba(15, 23, 42, 0.85) !important;
    border-radius: 16px !important;
    padding: 6px 8px !important;
    border: 1px solid rgba(59, 130, 246, 0.18) !important;
    gap: 6px !important;
    backdrop-filter: blur(12px) !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35) !important;
    margin-bottom: 22px !important;
    display: flex !important;
    flex-wrap: wrap !important;
}
[data-testid="stTabs"] [role="tab"] {
    border-radius: 10px !important;
    color: #94A3B8 !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    padding: 8px 18px !important;
    border: 1px solid transparent !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    background: transparent !important;
}
[data-testid="stTabs"] [role="tab"]:hover {
    color: #F8FAFC !important;
    background: rgba(255, 255, 255, 0.05) !important;
    border-color: rgba(255, 255, 255, 0.08) !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
    color: #FFFFFF !important;
    font-weight: 800 !important;
    border: 1px solid rgba(147, 197, 253, 0.35) !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.25) !important;
    transform: translateY(-1px) !important;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"],
[data-testid="stTabs"] [data-baseweb="tab-border"] {
    display: none !important;
}


/* ── 9. PROGRESS BARS ───────────────────────────────────────────────────── */
[data-testid="stProgress"] > div {
    background: #1E293B !important;
    border-radius: 999px !important;
    height: 10px !important;
}
[data-testid="stProgress"] > div > div {
    border-radius: 999px !important;
    background: linear-gradient(90deg, #3B82F6, #6366F1) !important;
    transition: width 0.4s ease !important;
}

/* ── 10. DATAFRAME ──────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] { border-radius: 12px !important; overflow: hidden; }
[data-testid="stDataFrame"] th {
    background: #1E293B !important;
    color: #94A3B8 !important;
    font-weight: 700 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    border-bottom: 1px solid #334155 !important;
}
[data-testid="stDataFrame"] td {
    background: #0F172A !important;
    color: #E2E8F0 !important;
    border-bottom: 1px solid #1E293B !important;
    font-size: 0.88rem !important;
}
[data-testid="stDataFrame"] tr:hover td { background: #1A2744 !important; }

/* ── 11. EXPANDER ───────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: #0F172A !important;
    border: 1px solid #1E293B !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary { color: #94A3B8 !important; font-weight: 600 !important; }

/* ── 12. ALERTS (st.error / warning / info / success) ───────────────────── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    border-left-width: 4px !important;
    padding: 0.8rem 1rem !important;
}
.stAlert[data-baseweb="notification"][kind="error"] {
    background: rgba(127,29,29,0.2) !important;
    border-color: #EF4444 !important;
}
.stAlert[data-baseweb="notification"][kind="warning"] {
    background: rgba(120,53,15,0.2) !important;
    border-color: #F59E0B !important;
}
.stAlert[data-baseweb="notification"][kind="info"] {
    background: rgba(30,58,138,0.2) !important;
    border-color: #3B82F6 !important;
}
.stAlert[data-baseweb="notification"][kind="success"] {
    background: rgba(6,78,59,0.2) !important;
    border-color: #10B981 !important;
}

/* ── 13. SPINNER & CAPTION ──────────────────────────────────────────────── */
[data-testid="stSpinner"] > div { color: #3B82F6 !important; }
.stCaption { color: #475569 !important; font-size: 0.78rem !important; }

/* ── 14. FILE UPLOADER ──────────────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: #1A2035 !important;
    border: 2px dashed #2D3D55 !important;
    border-radius: 12px !important;
    transition: border-color 0.2s !important;
}
[data-testid="stFileUploader"]:hover { border-color: #3B82F6 !important; }

/* ── 15. SCROLLBAR ──────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0F172A; }
::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #475569; }

/* ─────────────────────────────────────────────────────────────────────────
   CUSTOM COMPONENTS
   ─────────────────────────────────────────────────────────────────────── */

/* SOS BANNER */
@keyframes sos-pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(239,68,68,0.5), 0 4px 20px rgba(0,0,0,0.4); }
    50%       { box-shadow: 0 0 0 8px rgba(239,68,68,0), 0 4px 20px rgba(0,0,0,0.4); }
}
@keyframes blink-dot {
    0%, 100% { opacity: 1; }
    50%      { opacity: 0.3; }
}
.sos-banner {
    background: linear-gradient(135deg, #7F1D1D 0%, #991B1B 50%, #7F1D1D 100%);
    border: 1px solid rgba(239,68,68,0.45);
    color: #FEF2F2;
    padding: 12px 20px;
    border-radius: 12px;
    margin-bottom: 22px;
    font-size: 0.95rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 6px;
    animation: sos-pulse 2s ease-in-out infinite;
    letter-spacing: 0.01em;
}
.sos-live-dot {
    width: 9px; height: 9px;
    background: #EF4444;
    border-radius: 50%;
    display: inline-block;
    margin-right: 6px;
    animation: blink-dot 1.2s ease-in-out infinite;
}
.sos-pipe { color: rgba(255,255,255,0.3); margin: 0 8px; }
.sos-num { color: #FCA5A5; font-weight: 800; }

/* PORTAL TITLE */
.portal-title {
    font-size: 2rem; font-weight: 900; letter-spacing: -0.03em;
    background: linear-gradient(135deg, #F1F5F9 0%, #CBD5E1 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.2rem; line-height: 1.2;
}
.portal-subtitle {
    font-size: 0.97rem; color: #64748B;
    margin-bottom: 1.6rem; font-weight: 400;
}

/* SECTION DIVIDER */
.section-divider {
    border: none; border-top: 1px solid #1E293B;
    margin: 1.4rem 0;
}

/* STAT CARDS (custom metric replacements) */
.stat-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; margin-bottom: 1.6rem; }
.stat-card {
    background: linear-gradient(135deg, #1A2744 0%, #0F1C38 100%);
    border: 1px solid rgba(59,130,246,0.12);
    border-radius: 14px; padding: 1.1rem 1.2rem;
    position: relative; overflow: hidden;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.stat-card:hover { transform: translateY(-3px); box-shadow: 0 12px 30px rgba(0,0,0,0.5); }
.stat-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0;
    height: 3px; border-radius: 14px 14px 0 0;
}
.stat-danger::before  { background: linear-gradient(90deg, #EF4444, #B91C1C); }
.stat-warning::before { background: linear-gradient(90deg, #F59E0B, #D97706); }
.stat-blue::before    { background: linear-gradient(90deg, #3B82F6, #1D4ED8); }
.stat-green::before   { background: linear-gradient(90deg, #10B981, #059669); }
.stat-purple::before  { background: linear-gradient(90deg, #8B5CF6, #6D28D9); }
.stat-icon { font-size: 1.6rem; margin-bottom: 0.5rem; display: block; }
.stat-value { font-size: 2.2rem; font-weight: 900; color: #F1F5F9; line-height: 1; }
.stat-label { font-size: 0.75rem; color: #64748B; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; margin: 4px 0; }
.stat-sub { font-size: 0.8rem; font-weight: 600; margin-top: 4px; }
.stat-danger  .stat-sub { color: #FCA5A5; }
.stat-warning .stat-sub { color: #FCD34D; }
.stat-blue    .stat-sub { color: #93C5FD; }
.stat-green   .stat-sub { color: #6EE7B7; }
.stat-purple  .stat-sub { color: #C4B5FD; }

/* ALERT CARDS */
.alert-card {
    border-radius: 12px; padding: 14px 18px; margin-bottom: 12px;
    border-left: 5px solid; position: relative;
    transition: transform 0.15s ease;
}
.alert-card:hover { transform: translateX(3px); }
.alert-critical {
    background: linear-gradient(135deg, rgba(127,29,29,0.35) 0%, rgba(69,10,10,0.35) 100%);
    border-left-color: #EF4444;
}
.alert-high {
    background: linear-gradient(135deg, rgba(120,53,15,0.35) 0%, rgba(69,26,3,0.35) 100%);
    border-left-color: #F59E0B;
}
.alert-medium {
    background: linear-gradient(135deg, rgba(30,58,138,0.35) 0%, rgba(23,37,84,0.35) 100%);
    border-left-color: #3B82F6;
}
.alert-low {
    background: linear-gradient(135deg, rgba(6,78,59,0.35) 0%, rgba(2,44,34,0.35) 100%);
    border-left-color: #10B981;
}
.alert-header {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 8px; flex-wrap: wrap; gap: 6px;
}
.alert-badge {
    font-size: 0.75rem; font-weight: 800; padding: 3px 10px;
    border-radius: 999px; letter-spacing: 0.07em; text-transform: uppercase;
}
.badge-critical { background: rgba(239,68,68,0.2); color: #FCA5A5; border: 1px solid rgba(239,68,68,0.4); }
.badge-high     { background: rgba(245,158,11,0.2); color: #FCD34D; border: 1px solid rgba(245,158,11,0.4); }
.badge-medium   { background: rgba(59,130,246,0.2); color: #93C5FD; border: 1px solid rgba(59,130,246,0.4); }
.badge-low      { background: rgba(16,185,129,0.2); color: #6EE7B7; border: 1px solid rgba(16,185,129,0.4); }
.alert-time { font-size: 0.77rem; color: #475569; font-family: monospace; }
.alert-body { font-size: 0.92rem; color: #E2E8F0; line-height: 1.55; margin-bottom: 6px; }
.alert-target { font-size: 0.78rem; color: #64748B; }

/* RESOURCE CARDS (Shelters & Hospitals) */
.resource-card {
    background: linear-gradient(135deg, #111827 0%, #0F172A 100%);
    border: 1px solid #1E293B;
    border-radius: 14px; padding: 1.1rem 1.3rem;
    margin-bottom: 14px;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
    position: relative; overflow: hidden;
}
.resource-card:hover {
    border-color: #334155;
    box-shadow: 0 8px 24px rgba(0,0,0,0.35);
}
.resource-card-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 10px; flex-wrap: wrap; gap: 8px;
}
.resource-name { font-size: 1.02rem; font-weight: 700; color: #F1F5F9; }
.resource-district { font-size: 0.8rem; color: #64748B; margin-top: 1px; }
.resource-contact { font-size: 0.82rem; color: #475569; margin-top: 4px; }
.resource-contact span { color: #94A3B8; font-family: monospace; }
.avail-badge {
    font-size: 0.78rem; font-weight: 800; padding: 4px 12px;
    border-radius: 999px; white-space: nowrap;
}
.avail-open   { background: rgba(16,185,129,0.15); color: #6EE7B7; border: 1px solid rgba(16,185,129,0.35); }
.avail-medium { background: rgba(245,158,11,0.15); color: #FCD34D; border: 1px solid rgba(245,158,11,0.35); }
.avail-full   { background: rgba(239,68,68,0.15);  color: #FCA5A5; border: 1px solid rgba(239,68,68,0.35); }
.res-progress-wrap { background: #1E293B; border-radius: 999px; height: 8px; overflow: hidden; margin: 8px 0; }
.res-progress-bar  { height: 100%; border-radius: 999px; transition: width 0.4s ease; }
.prog-green  { background: linear-gradient(90deg, #10B981, #059669); }
.prog-yellow { background: linear-gradient(90deg, #F59E0B, #D97706); }
.prog-red    { background: linear-gradient(90deg, #EF4444, #B91C1C); }
.res-stats-row {
    display: flex; justify-content: space-between; align-items: center;
    font-size: 0.82rem; color: #94A3B8; margin-top: 6px; flex-wrap: wrap; gap: 4px;
}
.res-stats-row b { color: #CBD5E1; }

/* SUPPLY TABLE */
.supply-table { width: 100%; border-collapse: collapse; border-radius: 12px; overflow: hidden; }
.supply-table th {
    background: #1E293B; color: #64748B; font-size: 0.75rem;
    text-transform: uppercase; letter-spacing: 0.07em;
    padding: 10px 14px; text-align: left; font-weight: 700;
}
.supply-table td {
    background: #0F1726; color: #CBD5E1; font-size: 0.88rem;
    padding: 10px 14px; border-top: 1px solid #1E293B;
}
.supply-table tr:hover td { background: #141E30; }
.supply-type-badge {
    font-size: 0.75rem; font-weight: 700; padding: 2px 8px;
    border-radius: 6px; background: rgba(59,130,246,0.15);
    color: #93C5FD; border: 1px solid rgba(59,130,246,0.25);
}

/* SUGGESTION CARD */
.sugg-card {
    background: linear-gradient(135deg, #111827 0%, #0F172A 100%);
    border: 1px solid #1E293B; border-radius: 14px;
    padding: 1.1rem 1.3rem; margin-bottom: 12px;
    transition: border-color 0.2s;
}
.sugg-card:hover { border-color: #2D3D55; }
.sugg-title { font-size: 1rem; font-weight: 700; color: #F1F5F9; margin-bottom: 4px; }
.sugg-meta { font-size: 0.78rem; color: #475569; margin-bottom: 8px; }
.sugg-desc { font-size: 0.88rem; color: #94A3B8; line-height: 1.5; }
.sugg-footer {
    display: flex; justify-content: space-between; align-items: center;
    margin-top: 10px; flex-wrap: wrap; gap: 6px;
}
.sugg-votes { font-size: 0.82rem; color: #6EE7B7; font-weight: 700; }
.sugg-status {
    font-size: 0.72rem; font-weight: 700; padding: 2px 8px;
    border-radius: 6px; background: rgba(99,102,241,0.15);
    color: #C4B5FD; border: 1px solid rgba(99,102,241,0.25);
}
.cat-tag {
    font-size: 0.72rem; font-weight: 700; padding: 2px 8px;
    border-radius: 6px; background: rgba(30,41,59,0.8);
    color: #64748B; border: 1px solid #2D3D55;
}

/* WEATHER CARD */
.wx-main-card {
    background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
    border: 1px solid #2D3D55; border-radius: 16px;
    padding: 20px 24px; margin: 12px 0;
}
.wx-temp { font-size: 3.5rem; font-weight: 900; color: #F1F5F9; line-height: 1; }
.wx-cond { font-size: 1.1rem; color: #94A3B8; margin: 4px 0; }
.wx-meta { font-size: 0.82rem; color: #475569; margin-top: 6px; }
.wx-icon { font-size: 3.5rem; }
.wx-forecast-card {
    background: #1E293B; border: 1px solid #2D3D55;
    border-radius: 14px; padding: 16px; text-align: center;
    transition: border-color 0.2s ease;
}
.wx-forecast-card:hover { border-color: #3B82F6; }
.wx-alert-critical {
    background: linear-gradient(135deg, rgba(127,29,29,0.4), rgba(69,10,10,0.4));
    color: #FEF2F2; border-radius: 10px; padding: 14px 18px;
    margin-bottom: 10px; border-left: 5px solid #EF4444; font-size: 0.9rem;
}
.wx-alert-high {
    background: linear-gradient(135deg, rgba(120,53,15,0.4), rgba(69,26,3,0.4));
    color: #FFFBEB; border-radius: 10px; padding: 14px 18px;
    margin-bottom: 10px; border-left: 5px solid #F59E0B; font-size: 0.9rem;
}
.wx-alert-medium {
    background: linear-gradient(135deg, rgba(30,58,138,0.4), rgba(23,37,84,0.4));
    color: #EFF6FF; border-radius: 10px; padding: 14px 18px;
    margin-bottom: 10px; border-left: 5px solid #3B82F6; font-size: 0.9rem;
}

/* STATUS BADGE */
.status-badge-open {
    background: rgba(16,185,129,0.15); color: #6EE7B7;
    border: 1px solid rgba(16,185,129,0.35);
    padding: 4px 12px; border-radius: 999px;
    font-weight: 800; font-size: 0.78rem; white-space: nowrap;
}
.status-badge-full {
    background: rgba(239,68,68,0.15); color: #FCA5A5;
    border: 1px solid rgba(239,68,68,0.35);
    padding: 4px 12px; border-radius: 999px;
    font-weight: 800; font-size: 0.78rem; white-space: nowrap;
}

/* STEP FORM LABELS */
.step-label {
    display: inline-flex; align-items: center; gap: 8px;
    font-size: 1rem; font-weight: 800; color: #F1F5F9;
    margin: 18px 0 10px;
}
.step-num {
    width: 28px; height: 28px; background: linear-gradient(135deg, #DC2626, #991B1B);
    border-radius: 50%; display: inline-flex; align-items: center; justify-content: center;
    font-size: 0.82rem; font-weight: 900; color: white; flex-shrink: 0;
}

/* SIDEBAR HELPLINE BOX */
.sidebar-helpline {
    background: rgba(127,29,29,0.25); border: 1px solid rgba(239,68,68,0.25);
    border-radius: 10px; padding: 12px 14px; margin-top: 8px;
}
.sidebar-helpline div { font-size: 0.85rem; color: #FCA5A5 !important; margin: 3px 0; }
.sidebar-helpline span { color: #FEF2F2 !important; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ─── Language Initialization ──────────────────────────────────────────────────
if "lang" not in st.session_state:
    st.session_state["lang"] = "hi"

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 14px; padding: 14px 16px; margin-bottom: 14px; box-shadow: 0 4px 16px rgba(0,0,0,0.3);">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
            <span style="font-size:1.8rem;filter:drop-shadow(0 2px 8px rgba(220,38,38,0.6));">🚨</span>
            <span style="background:rgba(16,185,129,0.15);color:#34D399;border:1px solid rgba(16,185,129,0.35);font-size:0.68rem;font-weight:800;padding:2px 8px;border-radius:999px;display:inline-flex;align-items:center;gap:5px;">
                <span style="width:6px;height:6px;border-radius:50%;background:#10B981;box-shadow:0 0 6px #10B981;"></span> 24x7 LIVE
            </span>
        </div>
        <div style="font-size:1.05rem;font-weight:900;color:#F8FAFC;line-height:1.2;">उत्तराखंड आपदा राहत</div>
        <div style="font-size:0.72rem;color:#60A5FA;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;margin-top:2px;">Disaster Management Portal</div>
    </div>
    """, unsafe_allow_html=True)

    lang_choice = st.radio(
        t("lang_switch_label", st.session_state["lang"]),
        options=["hi", "en"],
        format_func=lambda x: "🇮🇳 हिंदी" if x == "hi" else "🇬🇧 English",
        index=0 if st.session_state["lang"] == "hi" else 1,
        horizontal=True,
        key="lang_radio"
    )
    if lang_choice != st.session_state["lang"]:
        st.session_state["lang"] = lang_choice
        st.rerun()

    lang = st.session_state["lang"]
    is_hi = (lang == "hi")

    st.markdown("<hr style='border-color:rgba(255,255,255,0.06);margin:14px 0 10px;'>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.75rem;font-weight:800;color:#64748B;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;padding-left:4px;'>{t('nav_title', lang)}</div>", unsafe_allow_html=True)

    nav_options = [
        t("nav_dashboard", lang), t("nav_report", lang), t("nav_find_help", lang),
        t("nav_alerts", lang), t("nav_weather", lang), t("nav_suggestions", lang), t("nav_admin", lang)
    ]
    nav_icons = ["📊", "📝", "📍", "🔔", "🌤️", "💡", "⚙️"]

    selected_nav = st.radio(
        t("nav_title", lang),
        nav_options,
        format_func=lambda x: f"{nav_icons[nav_options.index(x)]}  {x}",
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("<hr style='border-color:rgba(255,255,255,0.06);margin:14px 0 10px;'>", unsafe_allow_html=True)

    # Helplines in sidebar
    st.markdown(f"""
    <div class="sidebar-helpline" style="background: linear-gradient(135deg, rgba(127,29,29,0.22) 0%, rgba(30,41,59,0.5) 100%); border: 1px solid rgba(239,68,68,0.3); border-radius: 12px; padding: 12px 14px; box-shadow: 0 4px 14px rgba(0,0,0,0.25);">
        <div style="font-size:0.78rem;font-weight:800;color:#F87171;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:8px;display:flex;align-items:center;gap:6px;">
            🚨 {t('helpline_title', lang)}
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin:5px 0;font-size:0.82rem;"><span style="color:#CBD5E1;">📞 राज्य कंट्रोल</span><b style="color:#FEF2F2;background:rgba(239,68,68,0.3);padding:2px 7px;border-radius:6px;">1070</b></div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin:5px 0;font-size:0.82rem;"><span style="color:#CBD5E1;">🚔 Emergency</span><b style="color:#FEF2F2;background:rgba(239,68,68,0.3);padding:2px 7px;border-radius:6px;">112</b></div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin:5px 0;font-size:0.82rem;"><span style="color:#CBD5E1;">🪖 SDRF Helpline</span><b style="color:#FEF2F2;background:rgba(239,68,68,0.3);padding:2px 7px;border-radius:6px;font-size:0.75rem;">0135-2710334</b></div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin:5px 0;font-size:0.82rem;"><span style="color:#CBD5E1;">🚑 Ambulance</span><b style="color:#FEF2F2;background:rgba(239,68,68,0.3);padding:2px 7px;border-radius:6px;">108</b></div>
    </div>
    """, unsafe_allow_html=True)


lang = st.session_state["lang"]
is_hi = (lang == "hi")

# ─── SOS Banner ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="sos-banner">
    <span class="sos-live-dot"></span>
    <b>{t('helpline_title', lang)}:</b>
    <span class="sos-num">1070</span><span style="color:rgba(255,255,255,0.3)"> राज्य कंट्रोल</span>
    <span class="sos-pipe">|</span>
    <span class="sos-num">112</span><span style="color:rgba(255,255,255,0.3)"> Emergency</span>
    <span class="sos-pipe">|</span>
    <span class="sos-num">0135-2710334</span><span style="color:rgba(255,255,255,0.3)"> SDRF</span>
    <span class="sos-pipe">|</span>
    <span class="sos-num">108</span><span style="color:rgba(255,255,255,0.3)"> Ambulance</span>
</div>
""", unsafe_allow_html=True)

# ─── District Helpers ─────────────────────────────────────────────────────────
def get_district_display(district_key):
    return DISTRICT_NAMES_MAP.get(district_key, {}).get(lang, district_key)

district_display_list = [get_district_display(d) for d in ALL_DISTRICTS]
district_lookup = {get_district_display(d): d for d in ALL_DISTRICTS}


# ─────────────────────────────────────────────────────────────────────────────
# 1. DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
if selected_nav == t("nav_dashboard", lang):
    st.markdown(f'<div class="portal-title">{t("dash_title", lang)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="portal-subtitle">{t("dash_subtitle", lang)}</div>', unsafe_allow_html=True)

    stats = get_dashboard_summary()
    df_disasters = get_all_disasters()

    bed_pct = (stats['beds_available'] / stats['beds_total'] * 100) if stats['beds_total'] > 0 else 0
    shelter_pct = (stats['shelter_occupied'] / stats['shelter_capacity'] * 100) if stats['shelter_capacity'] > 0 else 0
    shelter_free = max(0, stats['shelter_capacity'] - stats['shelter_occupied'])

    # Custom stat cards
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"""
        <div class="stat-card stat-danger">
            <span class="stat-icon">🔥</span>
            <div class="stat-value">{stats['active_disasters']}</div>
            <div class="stat-label">{t('kpi_active_disasters', lang)}</div>
            <div class="stat-sub">{stats['critical_count']} {'अति-गंभीर' if is_hi else 'Critical'}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="stat-card stat-warning">
            <span class="stat-icon">📋</span>
            <div class="stat-value">{stats['total_disasters']}</div>
            <div class="stat-label">{t('kpi_total_incidents', lang)}</div>
            <div class="stat-sub">{stats['high_count']} {'गंभीर' if is_hi else 'High'}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        urgent = stats['critical_count'] + stats['high_count']
        st.markdown(f"""
        <div class="stat-card stat-danger">
            <span class="stat-icon">🚨</span>
            <div class="stat-value">{urgent}</div>
            <div class="stat-label">{t('kpi_urgent_cases', lang)}</div>
            <div class="stat-sub">{stats['critical_count']} {'अति-गंभीर' if is_hi else 'Critical'}</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        bed_color = "stat-green" if bed_pct > 40 else ("stat-warning" if bed_pct > 15 else "stat-danger")
        st.markdown(f"""
        <div class="stat-card {bed_color}">
            <span class="stat-icon">🏥</span>
            <div class="stat-value">{stats['beds_available']}</div>
            <div class="stat-label">{t('kpi_hospital_beds', lang)}</div>
            <div class="stat-sub">/ {stats['beds_total']} &nbsp; ({bed_pct:.0f}% {'खाली' if is_hi else 'Free'})</div>
        </div>""", unsafe_allow_html=True)
    with c5:
        sh_color = "stat-green" if shelter_pct < 60 else ("stat-warning" if shelter_pct < 85 else "stat-danger")
        st.markdown(f"""
        <div class="stat-card {sh_color}">
            <span class="stat-icon">🏕️</span>
            <div class="stat-value">{shelter_free}</div>
            <div class="stat-label">{t('kpi_shelter_capacity', lang)}</div>
            <div class="stat-sub">{stats['shelter_occupied']}/{stats['shelter_capacity']} {'भरे' if is_hi else 'Occ'} ({shelter_pct:.0f}%)</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # Map & Charts Row
    c_map, c_chart = st.columns([3, 2])

    with c_map:
        st.subheader(t("map_title", lang))
        active_disasters_df = df_disasters[df_disasters['status'] == 'Active'] if not df_disasters.empty else pd.DataFrame()
        map_points = []
        if not active_disasters_df.empty:
            for _, row in active_disasters_df.iterrows():
                if pd.notnull(row.get('latitude')) and pd.notnull(row.get('longitude')):
                    map_points.append({"lat": float(row['latitude']), "lon": float(row['longitude'])})
        if map_points:
            map_df = pd.DataFrame(map_points)
            st.map(map_df, zoom=7, use_container_width=True)
            st.caption(t("map_caption", lang))
        else:
            st.info(t("map_no_points", lang))

    with c_chart:
        st.subheader(t("chart_title", lang))
        if not df_disasters.empty:
            tab_type, tab_sev = st.tabs([t("tab_by_type", lang), t("tab_by_severity", lang)])
            with tab_type:
                type_col = 'type_hi' if is_hi and 'type_hi' in df_disasters.columns else 'type'
                type_counts = df_disasters[type_col].value_counts().reset_index()
                type_counts.columns = ['Disaster_Type', 'Count']
                total_cases = type_counts['Count'].sum()
                type_counts['Percentage'] = (type_counts['Count'] / total_cases * 100).round(1).astype(str) + "%"

                chart_type = alt.Chart(type_counts).mark_arc(innerRadius=55, stroke='#0A0F1D', strokeWidth=2).encode(
                    theta=alt.Theta(field="Count", type="quantitative"),
                    color=alt.Color(field="Disaster_Type", type="nominal", scale=alt.Scale(scheme='category10'),
                                    legend=alt.Legend(title=("आपदा प्रकार" if is_hi else "Disaster Type"), orient="bottom", labelColor="#CBD5E1", titleColor="#94A3B8")),
                    tooltip=[
                        alt.Tooltip(field="Disaster_Type", type="nominal", title=("आपदा" if is_hi else "Type")),
                        alt.Tooltip(field="Count", type="quantitative", title=("मामले" if is_hi else "Incidents")),
                        alt.Tooltip(field="Percentage", type="nominal", title=("प्रतिशत" if is_hi else "Share"))
                    ]
                ).properties(height=250).configure_view(strokeOpacity=0)
                
                st.altair_chart(chart_type, use_container_width=True)

                # Detailed Breakdown
                for _, r in type_counts.iterrows():
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 12px;margin-bottom:4px;background:rgba(30,41,59,0.45);border-radius:8px;border:1px solid rgba(255,255,255,0.06);">
                        <span style="font-size:0.85rem;color:#F1F5F9;font-weight:600;">{r['Disaster_Type']}</span>
                        <span style="font-size:0.82rem;"><b style="color:#60A5FA;">{r['Count']}</b> <span style="color:#64748B;">({r['Percentage']})</span></span>
                    </div>
                    """, unsafe_allow_html=True)

            with tab_sev:
                sev_col = 'severity_hi' if is_hi and 'severity_hi' in df_disasters.columns else 'severity'
                sev_counts = df_disasters[sev_col].value_counts().reset_index()
                sev_counts.columns = ['Severity', 'Count']
                total_sev = sev_counts['Count'].sum()
                sev_counts['Percentage'] = (sev_counts['Count'] / total_sev * 100).round(1).astype(str) + "%"

                sev_color_range = ['#EF4444', '#F59E0B', '#3B82F6', '#10B981']
                chart_sev = alt.Chart(sev_counts).mark_arc(innerRadius=55, stroke='#0A0F1D', strokeWidth=2).encode(
                    theta=alt.Theta(field="Count", type="quantitative"),
                    color=alt.Color(field="Severity", type="nominal",
                                    scale=alt.Scale(domain=sev_counts['Severity'].tolist(), range=sev_color_range[:len(sev_counts)]),
                                    legend=alt.Legend(title=("गंभीरता स्तर" if is_hi else "Urgency Level"), orient="bottom", labelColor="#CBD5E1", titleColor="#94A3B8")),
                    tooltip=[
                        alt.Tooltip(field="Severity", type="nominal", title=("स्तर" if is_hi else "Severity")),
                        alt.Tooltip(field="Count", type="quantitative", title=("मामले" if is_hi else "Cases")),
                        alt.Tooltip(field="Percentage", type="nominal", title=("प्रतिशत" if is_hi else "Share"))
                    ]
                ).properties(height=250).configure_view(strokeOpacity=0)

                st.altair_chart(chart_sev, use_container_width=True)

                # Detailed Urgency Cards
                for _, r in sev_counts.iterrows():
                    s_name = str(r['Severity'])
                    pill_color = "#EF4444" if ("Critical" in s_name or "अति-गंभीर" in s_name) else ("#F59E0B" if ("High" in s_name or "गंभीर" in s_name) else ("#3B82F6" if ("Medium" in s_name or "मध्यम" in s_name) else "#10B981"))
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 12px;margin-bottom:5px;background:rgba(30,41,59,0.45);border-radius:8px;border-left:4px solid {pill_color};border-top:1px solid rgba(255,255,255,0.06);border-right:1px solid rgba(255,255,255,0.06);border-bottom:1px solid rgba(255,255,255,0.06);">
                        <span style="font-size:0.85rem;color:#F1F5F9;font-weight:700;">{s_name}</span>
                        <span style="font-size:0.82rem;"><b style="color:{pill_color};">{r['Count']}</b> <span style="color:#64748B;">({r['Percentage']})</span></span>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No data available to chart.")


    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    st.subheader(t("table_title", lang))
    f1, f2, f3 = st.columns(3)
    with f1:
        f_status_options = [t("filter_all", lang),
            "सक्रिय (Active)" if is_hi else "Active",
            "नियंत्रण में (Under Control)" if is_hi else "Under Control",
            "समाधान हो गया (Resolved)" if is_hi else "Resolved"]
        f_status = st.selectbox(t("filter_status", lang), f_status_options, index=1)
        if f_status == t("filter_all", lang): status_val = None
        elif "Active" in f_status or "सक्रिय" in f_status: status_val = "Active"
        elif "Control" in f_status or "नियंत्रण" in f_status: status_val = "Under Control"
        else: status_val = "Resolved"
    with f2:
        f_sev_options = [t("filter_all", lang),
            "अति-गंभीर (Critical)" if is_hi else "Critical",
            "गंभीर (High)" if is_hi else "High",
            "मध्यम (Medium)" if is_hi else "Medium",
            "सामान्य (Low)" if is_hi else "Low"]
        f_sev = st.selectbox(t("filter_severity", lang), f_sev_options)
        if f_sev == t("filter_all", lang): sev_val = None
        elif "Critical" in f_sev or "अति-गंभीर" in f_sev: sev_val = "Critical"
        elif "High" in f_sev or "गंभीर" in f_sev: sev_val = "High"
        elif "Medium" in f_sev or "मध्यम" in f_sev: sev_val = "Medium"
        else: sev_val = "Low"
    with f3:
        f_dist_display = st.selectbox(t("filter_district", lang), [t("filter_all", lang)] + district_display_list)
        dist_val = None if f_dist_display == t("filter_all", lang) else district_lookup[f_dist_display]

    filtered_df = get_all_disasters(status_filter=status_val, severity_filter=sev_val, district_filter=dist_val)

    if not filtered_df.empty:
        def get_media_badge(val):
            if pd.notnull(val) and str(val).strip() and str(val) != "None":
                cnt = len(str(val).split(";"))
                return f"📸 {cnt} फाइलें" if is_hi else f"📸 {cnt} Files"
            return "—"

        evidence_badge_series = filtered_df['evidence_media'].apply(get_media_badge) if 'evidence_media' in filtered_df.columns else "—"

        if is_hi:
            display_df = pd.DataFrame({
                t("col_id", lang): filtered_df['id'],
                t("col_type", lang): filtered_df['type_hi'].fillna(filtered_df['type']),
                t("col_location", lang): filtered_df['location_hi'].fillna(filtered_df['location']),
                t("col_severity", lang): filtered_df['severity_hi'].fillna(filtered_df['severity']),
                t("col_description", lang): filtered_df['description_hi'].fillna(filtered_df['description']),
                t("col_evidence", lang): evidence_badge_series,
                t("col_contact", lang): filtered_df['reporter_contact'],
                t("col_time", lang): filtered_df['date_reported'],
                t("col_status", lang): filtered_df['status_hi'].fillna(filtered_df['status'])
            })
        else:
            display_df = pd.DataFrame({
                t("col_id", lang): filtered_df['id'],
                t("col_type", lang): filtered_df['type'],
                t("col_location", lang): filtered_df['location'],
                t("col_severity", lang): filtered_df['severity'],
                t("col_description", lang): filtered_df['description'],
                t("col_evidence", lang): evidence_badge_series,
                t("col_contact", lang): filtered_df['reporter_contact'],
                t("col_time", lang): filtered_df['date_reported'],
                t("col_status", lang): filtered_df['status']
            })

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        with st.expander(t("view_evidence_btn", lang)):
            evidence_rows = filtered_df[filtered_df['evidence_media'].astype(str).str.strip().str.len() > 3] if ('evidence_media' in filtered_df.columns and not filtered_df.empty) else pd.DataFrame()
            if not evidence_rows.empty:
                for _, r in evidence_rows.iterrows():
                    r_type = r['type_hi'] if is_hi else r['type']
                    r_loc = r['location_hi'] if is_hi else r['location']
                    st.markdown(f"##### 📍 Incident #{r['id']} — {r_type} ({r_loc}) | `{r['date_reported']}`")
                    files = str(r['evidence_media']).split(";")
                    ev_cols = st.columns(min(len(files), 3))
                    for idx, fpath in enumerate(files):
                        if os.path.exists(fpath):
                            with ev_cols[idx % len(ev_cols)]:
                                if fpath.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                                    st.image(fpath, caption=os.path.basename(fpath), use_container_width=True)
                                elif fpath.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                                    st.video(fpath)
                    st.markdown("---")
            else:
                st.info(t("no_evidence", lang))

        csv_data = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=t("download_csv", lang), data=csv_data,
            file_name=f"uttarakhand_emergency_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info(t("no_records_match", lang))


# ─────────────────────────────────────────────────────────────────────────────
# 2. REPORT DISASTER
# ─────────────────────────────────────────────────────────────────────────────
elif selected_nav == t("nav_report", lang):
    st.markdown(f'<div class="portal-title">{t("report_title", lang)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="portal-subtitle">{t("report_subtitle", lang)}</div>', unsafe_allow_html=True)

    with st.form("simple_report_form", clear_on_submit=True):
        st.markdown(f'<div class="step-label"><span class="step-num">1</span> {t("step1_title", lang)}</div>', unsafe_allow_html=True)
        dtype_keys = list(DISASTER_TYPE_TRANSLATIONS.keys())
        dtype_labels = [DISASTER_TYPE_TRANSLATIONS[k][lang] for k in dtype_keys]
        dtype_choice = st.selectbox(t("field_disaster_type", lang), dtype_labels)
        chosen_dtype_key = dtype_keys[dtype_labels.index(dtype_choice)]

        st.markdown(f'<div class="step-label"><span class="step-num">2</span> {t("step2_title", lang)}</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            selected_dist_display = st.selectbox(t("field_district", lang), district_display_list)
            clean_location = district_lookup[selected_dist_display]
        with c2:
            landmark = st.text_input(t("field_landmark", lang), placeholder=t("field_landmark_placeholder", lang))

        st.markdown(f'<div class="step-label"><span class="step-num">3</span> {t("step3_title", lang)}</div>', unsafe_allow_html=True)
        sev_options = [t("sev_critical_desc", lang), t("sev_high_desc", lang), t("sev_medium_desc", lang), t("sev_low_desc", lang)]
        sev_choice = st.radio(t("field_severity", lang), sev_options, index=1)
        if "Critical" in sev_choice or "अति-गंभीर" in sev_choice: clean_sev = "Critical"
        elif "High" in sev_choice or "गंभीर" in sev_choice: clean_sev = "High"
        elif "Medium" in sev_choice or "मध्यम" in sev_choice: clean_sev = "Medium"
        else: clean_sev = "Low"

        description = st.text_area(t("field_description", lang), placeholder=t("field_desc_placeholder", lang))
        phone = st.text_input(t("field_contact", lang), placeholder="e.g. 9876543210")

        step4_label = "चरण 4: फोटो या वीडियो प्रमाण जोड़ें (वैकल्पिक)" if is_hi else "Step 4: Attach Photos & Video Evidence (Optional)"
        st.markdown(f'<div class="step-label"><span class="step-num">4</span> {step4_label}</div>', unsafe_allow_html=True)
        upload_label = "आपदा स्थल के फोटो या वीडियो अपलोड करें" if is_hi else "Upload Disaster Photos & Videos (Evidence)"
        uploaded_files = st.file_uploader(
            upload_label, type=["jpg", "jpeg", "png", "webp", "mp4", "mov", "avi", "mkv"],
            accept_multiple_files=True,
            help="JPG, PNG, MP4, MOV supported. Helps rescue teams assess conditions."
        )

        submitted = st.form_submit_button(t("btn_submit_report", lang), type="primary", use_container_width=True)

        if submitted:
            full_desc = f"{landmark} — {description}" if landmark else description
            if not full_desc.strip():
                full_desc = f"{chosen_dtype_key} incident in {clean_location} requiring verification."
            contact_str = phone.strip() if phone.strip() else "N/A"
            saved_paths = []
            if uploaded_files:
                for ufile in uploaded_files:
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    safe_name = f"{ts}_{ufile.name.replace(' ', '_')}"
                    dest_path = os.path.join("uploads", safe_name)
                    with open(dest_path, "wb") as f:
                        f.write(ufile.getbuffer())
                    saved_paths.append(dest_path)
            media_str = ";".join(saved_paths) if saved_paths else ""
            did = add_disaster(dtype=chosen_dtype_key, location=clean_location, severity=clean_sev,
                description=full_desc, reporter_contact=contact_str, evidence_media=media_str)
            st.success(t("report_success_title", lang))
            st.info(t("report_success_msg", lang).replace("{did}", str(did)))
            if saved_paths:
                st.markdown("##### 📸 " + ("संलग्न प्रमाण पूर्वावलोकन" if is_hi else "Attached Evidence Preview"))
                p_cols = st.columns(min(len(saved_paths), 3))
                for idx, fpath in enumerate(saved_paths):
                    with p_cols[idx % len(p_cols)]:
                        if fpath.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                            st.image(fpath, caption=os.path.basename(fpath), use_container_width=True)
                        elif fpath.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                            st.video(fpath)
            st.balloons()


# ─────────────────────────────────────────────────────────────────────────────
# 3. FIND NEAREST HELP
# ─────────────────────────────────────────────────────────────────────────────
elif selected_nav == t("nav_find_help", lang):
    st.markdown(f'<div class="portal-title">{t("find_help_title", lang)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="portal-subtitle">{t("find_help_subtitle", lang)}</div>', unsafe_allow_html=True)

    c_dist, _ = st.columns([2, 2])
    with c_dist:
        chosen_dist_display = st.selectbox(t("select_your_district", lang), district_display_list, index=0)
        chosen_district = district_lookup[chosen_dist_display]

    st.markdown(f"### {t('resources_in', lang)}: **{chosen_dist_display}**")

    tab_s, tab_h, tab_r = st.tabs([t("tab_shelters", lang), t("tab_hospitals", lang), t("tab_supplies", lang)])

    with tab_s:
        df_s = get_shelters_by_district(chosen_district)
        if not df_s.empty:
            for _, s in df_s.iterrows():
                cap = int(s['capacity']); occ = int(s['occupied'])
                avail = max(0, cap - occ)
                occ_ratio = min(1.0, occ / cap) if cap > 0 else 0.0
                s_name = s['name_hi'] if (is_hi and pd.notnull(s.get('name_hi'))) else s['name']
                dist_label = s['district_hi'] if (is_hi and pd.notnull(s.get('district_hi'))) else s['district']

                # Google Maps Link
                if pd.notnull(s.get('latitude')) and pd.notnull(s.get('longitude')):
                    gmaps_url = f"https://www.google.com/maps/search/?api=1&query={s['latitude']},{s['longitude']}"
                else:
                    gmaps_url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(str(s['name']) + ' ' + str(s['district']) + ' Uttarakhand')}"

                if avail == 0:
                    badge_cls, badge_txt = "avail-full", ("पूर्ण भर गया" if is_hi else "Full")
                elif occ_ratio > 0.75:
                    badge_cls, badge_txt = "avail-medium", (f"सीमित ({avail})" if is_hi else f"Limited ({avail})")
                else:
                    badge_cls, badge_txt = "avail-open", (f"उपलब्ध ({avail})" if is_hi else f"Available ({avail})")

                prog_cls = "prog-red" if occ_ratio > 0.85 else ("prog-yellow" if occ_ratio > 0.6 else "prog-green")
                st.markdown(f"""
                <div class="resource-card">
                    <div class="resource-card-header">
                        <div>
                            <div class="resource-name">
                                <a href="{gmaps_url}" target="_blank" style="color:#F1F5F9;text-decoration:none;display:inline-flex;align-items:center;gap:6px;">
                                    🏠 {s_name} <span style="font-size:0.75rem;color:#60A5FA;">↗️</span>
                                </a>
                            </div>
                            <div class="resource-district">📍 {dist_label}</div>
                        </div>
                        <span class="avail-badge {badge_cls}">{badge_txt}</span>
                    </div>
                    <div class="res-progress-wrap">
                        <div class="res-progress-bar {prog_cls}" style="width:{occ_ratio*100:.0f}%;"></div>
                    </div>
                    <div class="res-stats-row">
                        <span>{'भरे हुए' if is_hi else 'Occupied'}: <b>{occ}/{cap}</b></span>
                        <span>📞 <span style="color:#93C5FD;font-family:monospace;">{s['contact']}</span></span>
                    </div>
                    <div style="margin-top:10px;display:flex;justify-content:space-between;align-items:center;">
                        <a href="{gmaps_url}" target="_blank" style="display:inline-flex;align-items:center;gap:6px;background:rgba(59,130,246,0.18);border:1px solid rgba(59,130,246,0.4);color:#93C5FD;padding:6px 14px;border-radius:8px;font-size:0.8rem;font-weight:700;text-decoration:none;">
                            🗺️ {'गूगल मैप्स पर लोकेशन व दिशा-निर्देश देखें' if is_hi else 'View Shelter on Google Maps'} ↗️
                        </a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning(t("no_shelters", lang))

    with tab_h:
        df_h = get_hospitals_by_district(chosen_district)
        if not df_h.empty:
            for _, h in df_h.iterrows():
                total_beds = int(h['beds_total']); avail_beds = int(h['beds_available'])
                avail_ratio = min(1.0, avail_beds / total_beds) if total_beds > 0 else 0.0

                h_name = h['name_hi'] if (is_hi and pd.notnull(h.get('name_hi'))) else h['name']
                dist_label = h['district_hi'] if (is_hi and pd.notnull(h.get('district_hi'))) else h['district']

                # Google Maps Link
                if pd.notnull(h.get('latitude')) and pd.notnull(h.get('longitude')):
                    gmaps_url_h = f"https://www.google.com/maps/search/?api=1&query={h['latitude']},{h['longitude']}"
                else:
                    gmaps_url_h = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(str(h['name']) + ' ' + str(h['district']) + ' Uttarakhand')}"

                if avail_beds == 0:
                    badge_cls, badge_txt = "avail-full", ("बेड उपलब्ध नहीं" if is_hi else "No Beds")
                elif avail_beds < 10:
                    badge_cls, badge_txt = "avail-medium", (f"{avail_beds} बेड बचे" if is_hi else f"{avail_beds} Beds Left")
                else:
                    badge_cls, badge_txt = "avail-open", (f"{avail_beds} बेड खाली" if is_hi else f"{avail_beds} Beds Free")

                bed_fill = 1.0 - avail_ratio
                prog_cls = "prog-red" if bed_fill > 0.85 else ("prog-yellow" if bed_fill > 0.6 else "prog-green")
                st.markdown(f"""
                <div class="resource-card">
                    <div class="resource-card-header">
                        <div>
                            <div class="resource-name">
                                <a href="{gmaps_url_h}" target="_blank" style="color:#F1F5F9;text-decoration:none;display:inline-flex;align-items:center;gap:6px;">
                                    🏥 {h_name} <span style="font-size:0.75rem;color:#60A5FA;">↗️</span>
                                </a>
                            </div>
                            <div class="resource-district">📍 {dist_label}</div>
                        </div>
                        <span class="avail-badge {badge_cls}">{badge_txt}</span>
                    </div>
                    <div class="res-progress-wrap">
                        <div class="res-progress-bar {prog_cls}" style="width:{bed_fill*100:.0f}%;"></div>
                    </div>
                    <div class="res-stats-row">
                        <span>{'खाली बेड' if is_hi else 'Free Beds'}: <b>{avail_beds}/{total_beds}</b></span>
                        <span>📞 <span style="color:#93C5FD;font-family:monospace;">{h['contact']}</span></span>
                    </div>
                    <div style="margin-top:10px;display:flex;justify-content:space-between;align-items:center;">
                        <a href="{gmaps_url_h}" target="_blank" style="display:inline-flex;align-items:center;gap:6px;background:rgba(59,130,246,0.18);border:1px solid rgba(59,130,246,0.4);color:#93C5FD;padding:6px 14px;border-radius:8px;font-size:0.8rem;font-weight:700;text-decoration:none;">
                            🗺️ {'गूगल मैप्स पर अस्पताल व मार्ग देखें' if is_hi else 'Navigate to Hospital on Google Maps'} ↗️
                        </a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning(t("no_hospitals", lang))

    with tab_r:
        df_r = get_resources_by_district(chosen_district)
        if not df_r.empty:
            # Stockpile Summary Cards
            food_items = df_r[df_r['type'].str.contains('Food', case=False, na=False)]
            water_items = df_r[df_r['type'].str.contains('Water', case=False, na=False)]
            med_items = df_r[df_r['type'].str.contains('Medicine', case=False, na=False)]
            eq_items = df_r[df_r['type'].str.contains('Equipment|Shelter', case=False, na=False)]

            st.markdown(f"#### 🍞 {'खाद्य सामग्री व आपातकालीन राहत भंडार' if is_hi else 'Food & Emergency Relief Stockpile Overview'}")
            
            sc1, sc2, sc3, sc4 = st.columns(4)
            with sc1:
                food_qty = food_items['quantity'].sum() if not food_items.empty else 0
                st.metric("🍞 " + ("राशन व भोजन किट" if is_hi else "Food & Ration Packs"), f"{food_qty:,}")
            with sc2:
                water_qty = water_items['quantity'].sum() if not water_items.empty else 0
                st.metric("💧 " + ("पेयजल / वाटर सप्लाई" if is_hi else "Drinking Water Supply"), f"{water_qty:,}")
            with sc3:
                med_qty = med_items['quantity'].sum() if not med_items.empty else 0
                st.metric("💊 " + ("चिकित्सा व फर्स्ट-एड" if is_hi else "Medical & Trauma Kits"), f"{med_qty:,}")
            with sc4:
                eq_qty = eq_items['quantity'].sum() if not eq_items.empty else 0
                st.metric("🏕️ " + ("टेंट, कंबल व उपकरण" if is_hi else "Tents & Rescue Gear"), f"{eq_qty:,}")

            st.markdown("---")

            # Supply Filter Tabs
            cat_list = [t("filter_all", lang), "🍞 " + ("खाद्य सामग्री (Food)" if is_hi else "Food & Rations"), "💧 " + ("पेयजल (Water)" if is_hi else "Drinking Water"), "💊 " + ("दवाइयां (Medical)" if is_hi else "Medical Supplies"), "🏕️ " + ("आश्रय व टेंट (Shelter)" if is_hi else "Shelter & Tents"), "🚤 " + ("बचाव उपकरण (Rescue Gear)" if is_hi else "Rescue Gear")]
            sel_cat = st.selectbox("📦 " + ("सामग्री श्रेणी चुनें (Filter Stockpile Category):" if is_hi else "Filter Stockpile Category:"), cat_list)

            filtered_r = df_r.copy()
            if "Food" in sel_cat or "खाद्य" in sel_cat:
                filtered_r = filtered_r[filtered_r['type'].str.contains('Food', case=False, na=False)]
            elif "Water" in sel_cat or "पेयजल" in sel_cat:
                filtered_r = filtered_r[filtered_r['type'].str.contains('Water', case=False, na=False)]
            elif "Medical" in sel_cat or "दवाइयां" in sel_cat:
                filtered_r = filtered_r[filtered_r['type'].str.contains('Medicine', case=False, na=False)]
            elif "Shelter" in sel_cat or "आश्रय" in sel_cat:
                filtered_r = filtered_r[filtered_r['type'].str.contains('Shelter', case=False, na=False)]
            elif "Rescue" in sel_cat or "बचाव" in sel_cat:
                filtered_r = filtered_r[filtered_r['type'].str.contains('Equipment', case=False, na=False)]

            # Render Cards for each resource
            depot_maps_url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(str(chosen_district) + ' District Disaster Food Warehouse Uttarakhand')}"

            for _, row in filtered_r.iterrows():
                rtype = row['type_hi'] if is_hi and pd.notnull(row.get('type_hi')) else row['type']
                rname = row['name_hi'] if is_hi and pd.notnull(row.get('name_hi')) else row['name']
                runit = row['unit_hi'] if is_hi and pd.notnull(row.get('unit_hi')) else row['unit']
                rdist = row['district_hi'] if is_hi and pd.notnull(row.get('district_hi')) else row['district']
                rqty = row['quantity']

                # Status Badge
                if rqty > 1000:
                    status_badge = '<span style="background:rgba(16,185,129,0.2);color:#34D399;padding:3px 10px;border-radius:6px;font-size:0.75rem;font-weight:700;">🟢 ' + ('पर्याप्त भंडार (Ample Reserve)' if is_hi else 'Ample Reserve') + '</span>'
                elif rqty > 200:
                    status_badge = '<span style="background:rgba(59,130,246,0.2);color:#93C5FD;padding:3px 10px;border-radius:6px;font-size:0.75rem;font-weight:700;">🟡 ' + ('संतोषजनक भंडार (Adequate)' if is_hi else 'Adequate Stock') + '</span>'
                else:
                    status_badge = '<span style="background:rgba(245,158,11,0.2);color:#FCD34D;padding:3px 10px;border-radius:6px;font-size:0.75rem;font-weight:700;">🟠 ' + ('सीमित भंडार (Active Dispatch)' if is_hi else 'Active Dispatch') + '</span>'

                with st.container(border=True):
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
                        <div>
                            <span style="font-size:0.75rem;font-weight:800;color:#94A3B8;text-transform:uppercase;letter-spacing:0.04em;">🏷️ {rtype}</span>
                            <div style="font-size:1.05rem;font-weight:800;color:#F8FAFC;margin-top:2px;">{rname}</div>
                            <div style="font-size:0.8rem;color:#64748B;margin-top:2px;">📍 {rdist} &nbsp;|&nbsp; 🏢 {'जिला आपदा रसद गोदाम' if is_hi else 'District Food & Relief Depot'}</div>
                        </div>
                        <div>
                            {status_badge}
                            <div style="font-size:1.3rem;font-weight:900;color:#38BDF8;text-align:right;margin-top:4px;">{rqty:,} <span style="font-size:0.85rem;color:#94A3B8;">{runit}</span></div>
                        </div>
                    </div>
                    <div style="margin-top:8px;padding-top:8px;border-top:1px solid rgba(255,255,255,0.06);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;">
                        <span style="font-size:0.78rem;color:#94A3B8;">📦 {'15 से 30 दिन का आपातकालीन आरक्षित स्टॉक' if is_hi else '15-30 days emergency buffer stock'}</span>
                        <a href="{depot_maps_url}" target="_blank" style="font-size:0.78rem;color:#60A5FA;text-decoration:none;font-weight:700;">🗺️ {'गोदाम लोकेशन (Google Maps)' if is_hi else 'View Depot on Google Maps'} ↗️</a>
                    </div>
                    """, unsafe_allow_html=True)

            # Table view
            with st.expander("📑 " + ("विस्तृत रसद व स्टॉक सूची देखें (Complete Stockpile Manifest)" if is_hi else "View Complete Stockpile Manifest")):
                display_stock = pd.DataFrame({
                    t("col_res_type", lang): filtered_r['type_hi'].fillna(filtered_r['type']) if is_hi else filtered_r['type'],
                    t("col_res_name", lang): filtered_r['name_hi'].fillna(filtered_r['name']) if is_hi else filtered_r['name'],
                    t("col_res_qty", lang): filtered_r['quantity'],
                    t("col_res_unit", lang): filtered_r['unit_hi'].fillna(filtered_r['unit']) if is_hi else filtered_r['unit'],
                    t("col_res_district", lang): filtered_r['district_hi'].fillna(filtered_r['district']) if is_hi else filtered_r['district']
                })
                st.dataframe(display_stock, use_container_width=True, hide_index=True)
        else:
            st.warning(t("no_supplies", lang))



# ─────────────────────────────────────────────────────────────────────────────
# 4. LIVE ALERTS FEED
# ─────────────────────────────────────────────────────────────────────────────
elif selected_nav == t("nav_alerts", lang):
    st.markdown(f'<div class="portal-title">{t("alerts_title", lang)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="portal-subtitle">{t("alerts_subtitle", lang)}</div>', unsafe_allow_html=True)

    filter_sev_options = [t("filter_all", lang),
        "अति-गंभीर (Critical)" if is_hi else "Critical",
        "गंभीर (High)" if is_hi else "High",
        "मध्यम (Medium)" if is_hi else "Medium",
        "सामान्य (Low)" if is_hi else "Low"]
    filter_sev = st.radio(t("filter_alerts_sev", lang), filter_sev_options, horizontal=True)

    if filter_sev == t("filter_all", lang): sev_query = None
    elif "Critical" in filter_sev or "अति-गंभीर" in filter_sev: sev_query = "Critical"
    elif "High" in filter_sev or "गंभीर" in filter_sev: sev_query = "High"
    elif "Medium" in filter_sev or "मध्यम" in filter_sev: sev_query = "Medium"
    else: sev_query = "Low"

    df_alerts = get_all_alerts(limit=50)

    if not df_alerts.empty:
        if sev_query:
            df_alerts = df_alerts[df_alerts['severity'] == sev_query]

        if not df_alerts.empty:
            st.markdown(f"<div style='color:#64748B;font-size:0.85rem;margin-bottom:12px;'>{'कुल' if is_hi else 'Showing'} <b style='color:#94A3B8;'>{len(df_alerts)}</b> {'चेतावनियां' if is_hi else 'alerts'}</div>", unsafe_allow_html=True)
            for _, alert in df_alerts.iterrows():
                sev = alert['severity']
                timestamp = alert['timestamp']
                msg_en = alert['message']
                msg_hi = alert.get('message_hi')
                display_msg = msg_hi if (is_hi and msg_hi and str(msg_hi).strip()) else msg_en
                target = alert.get('target', 'All')

                card_cls = {"Critical": "alert-critical", "High": "alert-high", "Medium": "alert-medium"}.get(sev, "alert-low")
                badge_cls = {"Critical": "badge-critical", "High": "badge-high", "Medium": "badge-medium"}.get(sev, "badge-low")
                badge_txt = {"Critical": t("alert_critical_badge", lang), "High": t("alert_high_badge", lang),
                             "Medium": t("alert_medium_badge", lang)}.get(sev, t("alert_low_badge", lang))

                st.markdown(f"""
                <div class="alert-card {card_cls}">
                    <div class="alert-header">
                        <span class="alert-badge {badge_cls}">{badge_txt}</span>
                        <span class="alert-time">🕐 {timestamp}</span>
                    </div>
                    <div class="alert-body">{display_msg}</div>
                    <div class="alert-target">📍 {'प्रभावित क्षेत्र' if is_hi else 'Target'}: {target}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(t("no_alerts", lang))
    else:
        st.info(t("no_alerts", lang))


# ─────────────────────────────────────────────────────────────────────────────
# 5. SUGGESTIONS
# ─────────────────────────────────────────────────────────────────────────────
elif selected_nav == t("nav_suggestions", lang):
    st.markdown(f'<div class="portal-title">{t("sugg_page_title", lang)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="portal-subtitle">{t("sugg_page_subtitle", lang)}</div>', unsafe_allow_html=True)

    sugg_tab_submit, sugg_tab_browse = st.tabs([t("tab_sugg_submit", lang), t("tab_sugg_browse", lang)])

    sugg_cat_options_en = ["Early Warning & Tech","Rescue Operations","Relief Shelters","Community Support","Web Portal Improvement","Other"]
    sugg_cat_options_hi = ["पूर्व चेतावनी व तकनीक (Technology)","राहत एवं बचाव कार्य (Rescue)","राहत शिविर सुविधाएं (Shelters)","जन सहयोग व स्वयंसेवक (Volunteers)","वेब पोर्टल सुधार (Web Portal)","अन्य (Other)"]

    with sugg_tab_submit:
        with st.form("suggestion_form", clear_on_submit=True):
            sugg_title = st.text_input(t("field_sugg_title", lang), placeholder=t("field_sugg_title_placeholder", lang))
            cat_options = sugg_cat_options_hi if is_hi else sugg_cat_options_en
            sugg_cat = st.selectbox(t("field_sugg_category", lang), cat_options)
            cat_idx = cat_options.index(sugg_cat)
            sugg_cat_en = sugg_cat_options_en[cat_idx]
            sugg_cat_hi = sugg_cat_options_hi[cat_idx]
            sugg_desc = st.text_area(t("field_sugg_desc", lang), placeholder=t("field_sugg_desc_placeholder", lang), height=150)
            s_c1, s_c2 = st.columns(2)
            with s_c1:
                sugg_name = st.text_input(t("field_sugg_contributor", lang), placeholder="Rahul Sharma / उत्तराखंड नागरिक")
            with s_c2:
                sugg_dist_display = st.selectbox(t("field_sugg_district", lang), [("समस्त उत्तराखंड (All)" if is_hi else "All Uttarakhand")] + district_display_list)
            sugg_submitted = st.form_submit_button(t("btn_submit_sugg", lang), type="primary", use_container_width=True)
            if sugg_submitted:
                if not sugg_title.strip() or not sugg_desc.strip():
                    st.error("⚠️ " + ("शीर्षक और विवरण भरना आवश्यक है।" if is_hi else "Title and description are required."))
                else:
                    contributor = sugg_name.strip() if sugg_name.strip() else "Anonymous / नागरिक"
                    if sugg_dist_display in district_lookup:
                        dist_en = district_lookup[sugg_dist_display]
                        dist_hi = DISTRICT_NAMES_MAP.get(dist_en, {}).get("hi", dist_en)
                    else:
                        dist_en = "All Uttarakhand"; dist_hi = "समस्त उत्तराखंड"
                    add_suggestion(title=sugg_title.strip(), category=sugg_cat_en, description=sugg_desc.strip(),
                        contributor=contributor, district=dist_en, category_hi=sugg_cat_hi, district_hi=dist_hi)
                    st.success(t("sugg_success_msg", lang))
                    st.balloons()

    with sugg_tab_browse:
        fb1, fb2 = st.columns([1, 2])
        with fb1:
            browse_cat_options = [t("filter_all", lang)] + (sugg_cat_options_hi if is_hi else sugg_cat_options_en)
            browse_cat = st.selectbox(t("filter_sugg_cat", lang), browse_cat_options, key="browse_cat")
        with fb2:
            search_q = st.text_input("🔍", placeholder=t("search_sugg_placeholder", lang), label_visibility="collapsed", key="search_sugg")

        cat_filter = None
        if browse_cat != t("filter_all", lang):
            if is_hi:
                cat_idx = sugg_cat_options_hi.index(browse_cat)
                cat_filter = sugg_cat_options_en[cat_idx]
            else:
                cat_filter = browse_cat

        df_sugg = get_all_suggestions(category_filter=cat_filter, search_term=search_q if search_q else None)

        if not df_sugg.empty:
            st.markdown(f"<div style='color:#64748B;font-size:0.85rem;margin:8px 0 14px;'>{'कुल' if is_hi else 'Total'} <b style='color:#94A3B8;'>{len(df_sugg)}</b> {'सुझाव मिले' if is_hi else 'suggestions found'}</div>", unsafe_allow_html=True)

            for _, s in df_sugg.iterrows():
                s_title = s['title_hi'] if (is_hi and s.get('title_hi')) else s['title']
                s_cat   = s['category_hi'] if (is_hi and s.get('category_hi')) else s['category']
                s_desc  = s['description_hi'] if (is_hi and s.get('description_hi')) else s['description']
                s_dist  = s['district_hi'] if (is_hi and s.get('district_hi')) else s['district']
                s_status = s['status_hi'] if (is_hi and s.get('status_hi')) else s['status']
                s_contributor = s.get('contributor', 'Anonymous')
                s_votes = int(s.get('upvotes', 0))
                s_date  = str(s.get('submitted_at', ''))[:10]

                col_card, col_vote = st.columns([5, 1])
                with col_card:
                    st.markdown(f"""
                    <div class="sugg-card">
                        <div class="sugg-title">{s_title}</div>
                        <div class="sugg-meta">
                            <span class="cat-tag">{s_cat}</span> &nbsp;
                            👤 {s_contributor} &nbsp;|&nbsp; 📍 {s_dist} &nbsp;|&nbsp; 🗓 {s_date}
                        </div>
                        <div class="sugg-desc">{s_desc}</div>
                        <div class="sugg-footer">
                            <span class="sugg-votes">👍 {s_votes} {'वोट' if is_hi else 'votes'}</span>
                            <span class="sugg-status">{s_status}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_vote:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("👍", key=f"upvote_{s['id']}", help="Upvote this suggestion"):
                        upvote_suggestion(s['id'])
                        st.rerun()
        else:
            st.info(t("no_alerts", lang) if is_hi else "No suggestions found.")


# ─────────────────────────────────────────────────────────────────────────────
# 6. WEATHER
# ─────────────────────────────────────────────────────────────────────────────
elif selected_nav == t("nav_weather", lang):
    st.markdown(f'<div class="portal-title">{t("weather_page_title", lang)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="portal-subtitle">{t("weather_page_subtitle", lang)}</div>', unsafe_allow_html=True)

    wx_tab1, wx_tab2, wx_tab3 = st.tabs([
        t("weather_current_conditions", lang),
        t("weather_3day_forecast", lang) + " & " + t("weather_alerts_tab", lang),
        t("weather_all_districts", lang),
    ])

    with wx_tab1:
        c_sel, _ = st.columns([2, 2])
        with c_sel:
            wx_dist_display = st.selectbox(t("weather_select_district", lang), district_display_list, key="wx_district_select")
        wx_district = district_lookup[wx_dist_display]

        with st.spinner(t("weather_loading", lang)):
            wx_data = wx.fetch_current_weather(wx_district)

        if wx_data.get("error"):
            st.error(f"{t('weather_error', lang)} — {wx_data['error']}")
        else:
            cur = wx_data["current"]
            today = wx_data["today"]
            alerts = wx_data["alerts"]

            if alerts:
                for a in alerts:
                    msg = a["message_hi"] if is_hi else a["message_en"]
                    sev = a["severity"]
                    icon = {"Critical": "🚨", "High": "⚠️"}.get(sev, "🟡")
                    badge = {"Critical": t("weather_critical_badge", lang), "High": t("weather_high_badge", lang)}.get(sev, t("weather_medium_badge", lang))
                    alert_text = f"{icon} **{badge}**\n\n{msg}"
                    if sev == "Critical":
                        st.error(alert_text)
                    elif sev == "High":
                        st.warning(alert_text)
                    else:
                        st.info(alert_text)
            else:
                st.success(t("weather_no_alerts", lang))

            st.markdown("---")


            cond = cur["condition_hi"] if is_hi else cur["condition_en"]
            wind_dir = wx.wind_direction_label(cur["winddirection"] or 0, lang)
            uv_lbl = wx.uv_label(cur["uv_index"], lang)

            with st.container(border=True):
                st.markdown(f"## {cur['icon']} {cur['temperature']:.1f}°C")
                st.markdown(f"**{cond}**")
                st.caption(f"📍 {wx_dist_display} &nbsp;|&nbsp; 🕐 {t('weather_updated', lang)}: {cur['updated_at']}")


            wc1, wc2, wc3, wc4, wc5, wc6 = st.columns(6)
            wc1.metric(t("weather_feels_like", lang), f"{cur['feels_like']:.1f}°C")
            wc2.metric(t("weather_humidity", lang), f"{cur['humidity']}%")
            wc3.metric(t("weather_wind", lang), f"{cur['windspeed']:.1f} km/h")
            wc4.metric(t("weather_wind_dir", lang), wind_dir)
            wc5.metric(t("weather_precip", lang), f"{cur['precipitation']:.1f} mm")
            wc6.metric(t("weather_uv", lang), uv_lbl)

            st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
            st.subheader("📅 " + t("weather_today", lang))
            tc1, tc2, tc3, tc4 = st.columns(4)
            tc1.metric(f"🌡️ {t('weather_max', lang)}", f"{today.get('temperature_max', 'N/A')}°C")
            tc2.metric(f"🌡️ {t('weather_min', lang)}", f"{today.get('temperature_min', 'N/A')}°C")
            tc3.metric(f"🌧️ {t('weather_rain', lang)}", f"{today.get('precipitation_sum', 0):.1f} mm")
            tc4.metric(f"❄️ {t('weather_snow', lang)}", f"{today.get('snowfall_sum', 0):.1f} cm")
            st.caption(f"ℹ️ {t('weather_source', lang)}")

    with wx_tab2:
        c_sel2, _ = st.columns([2, 2])
        with c_sel2:
            wx_dist2_display = st.selectbox(t("weather_select_district", lang), district_display_list, key="wx_district_select2")
        wx_district2 = district_lookup[wx_dist2_display]
        with st.spinner(t("weather_loading", lang)):
            wx_data2 = wx.fetch_current_weather(wx_district2)
        if wx_data2.get("error"):
            st.error(t("weather_error", lang))
        else:
            forecast = wx_data2["forecast"]
            alerts2 = wx_data2["alerts"]
            st.subheader(f"📅 {t('weather_3day_forecast', lang)} — {wx_dist2_display}")
            if forecast:
                fc_cols = st.columns(len(forecast))
                for i, day in enumerate(forecast):
                    cond_d = day["condition_hi"] if is_hi else day["condition_en"]
                    with fc_cols[i]:
                        with st.container(border=True):
                            st.caption(day['date'])
                            st.markdown(f"### {day['icon']}")
                            st.markdown(f"**{cond_d}**")
                            st.markdown(f"🔴 **▲ {day['temperature_max']:.0f}°C** &nbsp;&nbsp; 🔵 **▼ {day['temperature_min']:.0f}°C**")
                            st.caption(f"🌧 {day['precipitation_sum']:.1f} mm &nbsp; ❄ {day['snowfall_sum']:.1f} cm")
                            st.caption(f"💨 {day['wind_speed_max']:.0f} km/h")
            else:
                st.info("Forecast data not available.")
            st.markdown("---")

            st.subheader(f"⚠️ {t('weather_alert_header', lang)} — {wx_dist2_display}")
            if alerts2:
                for a in alerts2:
                    msg = a["message_hi"] if is_hi else a["message_en"]
                    sev = a["severity"]
                    icon = {"Critical": "🚨", "High": "⚠️"}.get(sev, "🟡")
                    badge = {"Critical": t("weather_critical_badge", lang), "High": t("weather_high_badge", lang)}.get(sev, t("weather_medium_badge", lang))
                    alert_text = f"{icon} **{badge}**\n\n{msg}"
                    if sev == "Critical":
                        st.error(alert_text)
                    elif sev == "High":
                        st.warning(alert_text)
                    else:
                        st.info(alert_text)
            else:
                st.success(t("weather_no_alerts", lang))
            st.caption(f"ℹ️ {t('weather_source', lang)}")


    with wx_tab3:
        st.subheader(t("weather_overview_title", lang))
        st.info("🔄 " + ("सभी 13 जिलों का लाइव डेटा लोड हो रहा है..." if is_hi else "Loading live data for all 13 districts..."))
        with st.spinner(t("weather_loading", lang)):
            all_wx = wx.fetch_all_districts_summary()
        if all_wx:
            all_wx_sorted = sorted(all_wx, key=lambda x: (0 if x.get("has_alert") else 1))
            n = len(all_wx_sorted)
            rows = [all_wx_sorted[i:i+3] for i in range(0, n, 3)]
            for row in rows:
                cols = st.columns(3)
                for ci, d in enumerate(row):
                    with cols[ci]:
                        if d.get("error"):
                            st.warning(f"**{d['district']}** — Data unavailable")
                            continue
                        dist_name = DISTRICT_NAMES_MAP.get(d["district"], {}).get(lang, d["district"])
                        cond = d["condition_hi"] if is_hi else d["condition_en"]
                        has_alert = d.get("has_alert", False)
                        sev = d.get("alert_severity", "High")

                        with st.container(border=True):
                            # Alert badge
                            if has_alert:
                                if sev == "Critical":
                                    st.error(f"🚨 {'अलर्ट' if is_hi else 'ALERT'}")
                                else:
                                    st.warning(f"⚠️ {'अलर्ट' if is_hi else 'ALERT'}")

                            st.markdown(f"**{dist_name}**")
                            st.markdown(f"### {d['icon']} {d['temperature']:.0f}°C")
                            st.caption(cond)
                            st.caption(f"🌧 {d.get('precipitation', 0):.1f} mm &nbsp; 💨 {d.get('windspeed', 0):.0f} km/h")

            st.caption(f"ℹ️ {t('weather_source', lang)}")
        else:
            st.error(t("weather_error", lang))



# ─────────────────────────────────────────────────────────────────────────────
# 7. ADMIN
# ─────────────────────────────────────────────────────────────────────────────
elif selected_nav == t("nav_admin", lang):
    st.markdown(f'<div class="portal-title">{t("admin_title", lang)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="portal-subtitle">{t("admin_subtitle", lang)}</div>', unsafe_allow_html=True)

    ad_tab1, ad_tab2, ad_tab3, ad_tab4 = st.tabs([
        t("admin_tab_status", lang), t("admin_tab_capacity", lang),
        t("admin_tab_broadcast", lang), t("admin_tab_db", lang)
    ])

    with ad_tab1:
        st.subheader(t("admin_tab_status", lang))
        df_all = get_all_disasters()
        if not df_all.empty:
            options = {}
            for _, row in df_all.iterrows():
                row_type = row['type_hi'] if is_hi else row['type']
                row_loc = row['location_hi'] if is_hi else row['location']
                row_sev = row['severity_hi'] if is_hi else row['severity']
                row_stat = row['status_hi'] if is_hi else row['status']
                options[row['id']] = f"#{row['id']} — {row_type} in {row_loc} [{row_sev}] ({row_stat})"

            selected_id = st.selectbox(t("admin_select_incident", lang), options.keys(), format_func=lambda x: options[x])
            curr_status = df_all.loc[df_all['id'] == selected_id, 'status'].values[0]
            status_map = {"Active": t("status_active", lang), "Under Control": t("status_under_control", lang), "Resolved": t("status_resolved", lang)}
            new_status_key = st.selectbox(t("admin_set_status", lang), ["Active", "Under Control", "Resolved"],
                format_func=lambda x: status_map[x],
                index=["Active", "Under Control", "Resolved"].index(curr_status) if curr_status in ["Active", "Under Control", "Resolved"] else 0)

            if st.button(t("btn_save_status", lang), type="primary"):
                update_disaster_status(selected_id, new_status_key)
                st.success(f"Incident #{selected_id} updated successfully!")
                st.rerun()

            st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
            if is_hi:
                st.dataframe(df_all[['id','type_hi','location_hi','severity_hi','status_hi','reporter_contact','date_reported']].rename(columns={
                    'id': t('col_id', lang), 'type_hi': t('col_type', lang), 'location_hi': t('col_location', lang),
                    'severity_hi': t('col_severity', lang), 'status_hi': t('col_status', lang),
                    'reporter_contact': t('col_contact', lang), 'date_reported': t('col_time', lang)
                }), use_container_width=True, hide_index=True)
            else:
                st.dataframe(df_all[['id','type','location','severity','status','reporter_contact','date_reported']], use_container_width=True, hide_index=True)
        else:
            st.info("No recorded incidents.")

    with ad_tab2:
        st.subheader(t("admin_tab_capacity", lang))
        h_col, s_col = st.columns(2)

        with h_col:
            st.markdown("##### 🏥 " + ("अस्पताल बेड संख्या अपडेट करें" if is_hi else "Update Hospital Beds Available"))
            hospitals_df = get_hospitals_by_district()
            if not hospitals_df.empty:
                h_options = {}
                for _, row in hospitals_df.iterrows():
                    h_name = row['name_hi'] if is_hi else row['name']
                    h_dist = row['district_hi'] if is_hi else row['district']
                    h_options[row['id']] = f"{h_name} ({h_dist}) — Total: {row['beds_total']}"
                sel_h = st.selectbox("Select Hospital:", h_options.keys(), format_func=lambda x: h_options[x])
                curr_h_avail = int(hospitals_df.loc[hospitals_df['id'] == sel_h, 'beds_available'].values[0])
                total_h = int(hospitals_df.loc[hospitals_df['id'] == sel_h, 'beds_total'].values[0])
                new_h_avail = st.number_input("Available Beds / उपलब्ध बेड", min_value=0, max_value=total_h, value=curr_h_avail)
                if st.button("💾 " + ("बेड संख्या सुरक्षित करें" if is_hi else "Save Hospital Beds")):
                    update_hospital_beds(sel_h, new_h_avail)
                    st.success(f"Hospital beds updated to {new_h_avail}!")
                    st.rerun()

        with s_col:
            st.markdown("##### 🏠 " + ("राहत शिविर ऑक्यूपेंसी अपडेट करें" if is_hi else "Update Shelter Occupancy"))
            shelters_df = get_shelters_by_district()
            if not shelters_df.empty:
                s_options = {}
                for _, row in shelters_df.iterrows():
                    s_name = row['name_hi'] if is_hi else row['name']
                    s_dist = row['district_hi'] if is_hi else row['district']
                    s_options[row['id']] = f"{s_name} ({s_dist}) — Total: {row['capacity']}"
                sel_s = st.selectbox("Select Shelter:", s_options.keys(), format_func=lambda x: s_options[x])
                curr_s_occ = int(shelters_df.loc[shelters_df['id'] == sel_s, 'occupied'].values[0])
                total_s = int(shelters_df.loc[shelters_df['id'] == sel_s, 'capacity'].values[0])
                new_s_occ = st.number_input("Occupied Count / भरे हुए स्थान", min_value=0, max_value=total_s, value=curr_s_occ)
                if st.button("💾 " + ("शिविर ऑक्यूपेंसी सुरक्षित करें" if is_hi else "Save Shelter Occupancy")):
                    update_shelter_occupancy(sel_s, new_s_occ)
                    st.success(f"Shelter occupancy updated to {new_s_occ}!")
                    st.rerun()

    with ad_tab3:
        st.subheader(t("admin_broadcast_title", lang))
        with st.form("broadcast_alert_form"):
            b_sev = st.selectbox(t("filter_severity", lang), ["Critical", "High", "Medium", "Low"])
            b_target = st.selectbox("Target District / Audience", ["All Uttarakhand Districts", "Emergency Teams Only"] + ALL_DISTRICTS)
            b_msg_hi = st.text_area("चेतावनी संदेश (हिंदी)", placeholder="उदा: भारी बारिश के चलते बद्रीनाथ राष्ट्रीय राजमार्ग अवरुद्ध है।")
            b_msg_en = st.text_area("Alert Message (English)", placeholder="e.g. Heavy rainfall has disrupted Badrinath National Highway.")
            send_btn = st.form_submit_button(t("btn_send_broadcast", lang), type="primary")
            if send_btn:
                if b_msg_hi.strip() or b_msg_en.strip():
                    primary_en = b_msg_en.strip() if b_msg_en.strip() else b_msg_hi.strip()
                    primary_hi = b_msg_hi.strip() if b_msg_hi.strip() else b_msg_en.strip()
                    aid = add_custom_alert(None, primary_en, primary_hi, b_sev, b_target)
                    st.success(f"Broadcast Alert #{aid} transmitted successfully!")
                else:
                    st.error("Please enter a message before broadcasting.")

    with ad_tab4:
        st.subheader(t("admin_tab_db", lang))
        st.markdown("<div style='color:#94A3B8;font-size:0.9rem;margin-bottom:16px;'>Reset database and reseed complete official Uttarakhand mock data across all 13 districts.</div>", unsafe_allow_html=True)
        if st.button("🔄 " + t("admin_reset_db", lang), type="secondary"):
            sample_data.insert_sample_data(reset_existing=True)
            st.success("Database successfully reset and reseeded with full 13-district Uttarakhand data!")
            st.rerun()
