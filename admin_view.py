"""
admin_view.py — Dedicated State Emergency Operations Command (SEOC) & Admin Dashboard
Provides full administrative authority:
1. Incident Triage & Live SDRF/NDRF Dispatch
2. Hospital Bed & ICU Matrix Control
3. Relief Shelter Capacity Slider
4. Logistics & Supply Warehouse Logger
5. Emergency Public Broadcast Siren
6. Citizen Suggestions Moderation
7. Misinformation & Fake News Enforcement Cell (Section 54 DM Act 2005)
8. Daily SitRep Generator & CSV Exporters
9. Database Management & Live Reseeding Engine
"""

import streamlit as st
import pandas as pd
import os
import urllib.parse
from datetime import datetime

from database import (
    get_all_disasters, get_shelters_by_district, get_hospitals_by_district, get_resources_by_district,
    get_all_alerts, update_disaster_status, update_hospital_beds,
    update_shelter_occupancy, get_dashboard_summary, add_suggestion,
    get_all_suggestions, upvote_suggestion, update_suggestion_status,
    edit_disaster, delete_disaster, dispatch_rescue_team,
    add_hospital, edit_hospital, delete_hospital,
    add_shelter, edit_shelter, delete_shelter,
    add_resource, edit_resource, delete_resource,
    delete_alert, delete_suggestion,
    report_fake_info, get_all_fake_reports, resolve_fake_report,
    blacklist_contact, is_contact_blacklisted, get_blacklisted_contacts, unblacklist_contact,
    submit_shelter_runtime_checkin, get_shelter_runtime_history,
    DISTRICT_NAMES_MAP, ALL_DISTRICTS, DISTRICT_COORDINATES,
    add_disaster, add_custom_alert
)

from translations import (t, DISASTER_TYPE_TRANSLATIONS, SEVERITY_TRANSLATIONS, STATUS_TRANSLATIONS)
import sample_data

def render_admin_dashboard(lang="en", is_hi=False):
    st.markdown(f'<div class="portal-title">{"⚙️ राज्य आपदा नियंत्रण कक्ष एवं अधिकारी कमान (SEOC)" if is_hi else "⚙️ State Emergency Operations Command & Admin Center"}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="portal-subtitle">{"जिलाधिकारियों, एसडीआरएफ कमान और राहत आयुक्त के लिए एकीकृत नियंत्रण, संपादन एवं प्रवर्तन प्रणाली।" if is_hi else "Dedicated Command, Control, Incident Triage, Legal Enforcement & Resource Management Portal for State Incident Commanders."}</div>', unsafe_allow_html=True)

    # ── Admin Authentication Gate ──
    if "admin_authenticated" not in st.session_state:
        st.session_state["admin_authenticated"] = False

    if not st.session_state["admin_authenticated"]:
        st.markdown(f"""
        <div style="background:rgba(15,23,42,0.85);border:1px solid rgba(59,130,246,0.3);border-radius:14px;padding:24px;max-width:550px;margin:20px auto 40px;">
            <div style="font-size:1.1rem;font-weight:800;color:#F8FAFC;margin-bottom:8px;display:flex;align-items:center;gap:8px;">
                🔒 {'कंट्रोल रूम सुरक्षा सत्यापन' if is_hi else 'Officer Security Access Gate'}
            </div>
            <div style="font-size:0.85rem;color:#94A3B8;margin-bottom:16px;">
                {'कृपया राज्य आपदा कंट्रोल रूम का मास्टर पिन दर्ज करें (मूल्यांकन पिन: admin123)' if is_hi else 'Please enter authorized State Operations PIN (Evaluator Passcode: admin123)'}
            </div>
        </div>
        """, unsafe_allow_html=True)

        c_pin1, c_pin2, c_pin3 = st.columns([1, 2, 1])
        with c_pin2:
            with st.form("admin_login_form"):
                entered_pin = st.text_input("🔑 " + ("एडमिन पिन कोड" if is_hi else "Master Admin Passcode"), type="password", placeholder="admin123")
                login_btn = st.form_submit_button("🔓 " + ("कंट्रोल रूम में प्रवेश करें" if is_hi else "Authenticate & Access Command Center"), type="primary", use_container_width=True)
                if login_btn:
                    if entered_pin.strip() in ["admin123", "sdrf2026", "ukdisaster"]:
                        st.session_state["admin_authenticated"] = True
                        st.success("✅ " + ("सत्यापन सफल! कंट्रोल रूम सक्रिय है।" if is_hi else "Authenticated successfully! Welcome, Incident Commander."))
                        st.rerun()
                    else:
                        st.error("❌ " + ("गलत पिन कोड! कृपया पुनः प्रयास करें।" if is_hi else "Invalid Passcode. Please enter 'admin123'."))

    else:
        # Officer Status & Logout Bar
        c_auth_info, c_auth_logout = st.columns([4, 1])
        with c_auth_info:
            st.markdown(f"""
            <div style="background:linear-gradient(90deg, rgba(30,58,138,0.3) 0%, rgba(15,23,42,0.6) 100%);border:1px solid rgba(59,130,246,0.4);border-radius:10px;padding:8px 16px;display:flex;align-items:center;gap:10px;">
                <span style="font-size:1.1rem;">👮</span>
                <div>
                    <span style="font-size:0.88rem;font-weight:800;color:#38BDF8;">{'राज्य राहत आयुक्त एवं एसडीआरएफ कमान (SEOC उत्तराखंड)' if is_hi else 'State Relief Commissioner & SDRF Incident Commander (SEOC)'}</span>
                    <span style="font-size:0.75rem;color:#94A3B8;display:block;">{'सक्रिय सत्र · 24x7 इमरजेंसी नियंत्रण सक्षम' if is_hi else 'Active Session · Full Read/Write/Dispatch Privileges Granted'}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with c_auth_logout:
            if st.button("🔒 " + ("लॉगआउट" if is_hi else "Lock / Logout"), use_container_width=True):
                st.session_state["admin_authenticated"] = False
                st.rerun()

        st.markdown("<br/>", unsafe_allow_html=True)

        # ── Executive Quick Stats ──
        stats = get_dashboard_summary()
        c_s1, c_s2, c_s3, c_s4 = st.columns(4)
        c_s1.metric("🔥 " + ("सक्रिय आपदाएं" if is_hi else "Active Incidents"), f"{stats['active_disasters']} / {stats['total_disasters']}")
        c_s2.metric("🚨 " + ("अति-गंभीर मामले" if is_hi else "Critical Cases"), f"{stats['critical_count']}")
        c_s3.metric("🛏️ " + ("उपलब्ध अस्पताल बेड" if is_hi else "Hospital Beds"), f"{stats['beds_available']} / {stats['beds_total']}")
        c_s4.metric("🏠 " + ("राहत शिविर क्षमता" if is_hi else "Shelter Space"), f"{stats['shelter_occupied']} / {stats['shelter_capacity']}")

        st.markdown("<hr style='border-color:rgba(255,255,255,0.08);margin:16px 0;'>", unsafe_allow_html=True)

        # ── Comprehensive Admin Command Tabs ──
        ad_tab1, ad_tab2, ad_tab3, ad_tab4, ad_tab5, ad_tab6, ad_tab7, ad_tab8, ad_tab9 = st.tabs([
            "🚨 " + ("घटना नियंत्रण व रेस्क्यू" if is_hi else "Incidents & Rescue"),
            "🏥 " + ("अस्पताल व बेड" if is_hi else "Hospitals & Beds"),
            "🏠 " + ("राहत शिविर" if is_hi else "Relief Shelters"),
            "📦 " + ("राशन व आपूर्ति भंडार" if is_hi else "Supplies & Stockpiles"),
            "📢 " + ("आपातकालीन ब्रॉडकास्ट" if is_hi else "Emergency Broadcast"),
            "💡 " + ("सुझाव व नवाचार" if is_hi else "Suggestions Review"),
            "⚖️ " + ("फर्जी सूचना निस्तारण व साइबर सेल" if is_hi else "Fake News Grievance Cell"),
            "📊 " + ("दैनिक SitRep व रिपोर्ट" if is_hi else "SitRep & Reports"),
            "⚙️ " + ("डेटाबेस ऑपरेशन्स" if is_hi else "Database Tools")
        ])

        # ─────────────────────────────────────────────────────────────────────
        # TAB 1: INCIDENTS CONTROL & SDRF RESCUE DISPATCH
        # ─────────────────────────────────────────────────────────────────────
        with ad_tab1:
            st.subheader("🚨 " + ("आपदा घटना नियंत्रण एवं रेस्क्यू दस्ता प्रेषण" if is_hi else "Incident Command, Editing & Rescue Dispatch"))
            df_all = get_all_disasters()

            if not df_all.empty:
                # Filter & Search row
                f_c1, f_c2 = st.columns(2)
                with f_c1:
                    filter_dist = st.selectbox("📍 " + ("जिले अनुसार देखें" if is_hi else "Filter by District"), ["All"] + ALL_DISTRICTS, key="adm_dist_f")
                with f_c2:
                    filter_sev = st.selectbox("⚠️ " + ("गंभीरता अनुसार देखें" if is_hi else "Filter by Severity"), ["All", "Critical", "High", "Medium", "Low"], key="adm_sev_f")

                df_filtered = df_all.copy()
                if filter_dist != "All":
                    df_filtered = df_filtered[df_filtered['location'] == filter_dist]
                if filter_sev != "All":
                    df_filtered = df_filtered[df_filtered['severity'] == filter_sev]

                st.dataframe(
                    df_filtered[['id', 'type', 'location', 'severity', 'status', 'reporter_contact', 'date_reported', 'description']],
                    use_container_width=True, hide_index=True
                )

                st.markdown("---")

                # Action Sub-Sections: Edit / Dispatch / Delete / Add
                inc_act_edit, inc_act_dispatch, inc_act_add, inc_act_del = st.tabs([
                    "✏️ " + ("घटना विवरण संपादित करें" if is_hi else "Edit Incident Details"),
                    "🚀 " + ("SDRF / NDRF दस्ता रवाना करें" if is_hi else "Dispatch Rescue Team"),
                    "➕ " + ("नई घटना दर्ज करें" if is_hi else "Log New Incident"),
                    "🗑️ " + ("फर्जी/डुप्लीकेट रिपोर्ट हटाएं" if is_hi else "Delete False Report")
                ])

                # EDIT INCIDENT
                with inc_act_edit:
                    st.markdown("##### ✏️ " + ("घटना विवरण एवं स्थिति अपडेट करें" if is_hi else "Modify Existing Incident Record"))
                    options_edit = {row['id']: f"#{row['id']} — {row['type']} in {row['location']} ({row['severity']})" for _, row in df_all.iterrows()}
                    selected_e_id = st.selectbox("Select Incident to Edit:", options_edit.keys(), format_func=lambda x: options_edit[x], key="adm_edit_sel")

                    e_row = df_all.loc[df_all['id'] == selected_e_id].iloc[0]
                    with st.form("edit_incident_form"):
                        ec1, ec2, ec3 = st.columns(3)
                        with ec1:
                            e_type = st.selectbox("Disaster Type:", list(DISASTER_TYPE_TRANSLATIONS.keys()), index=list(DISASTER_TYPE_TRANSLATIONS.keys()).index(e_row['type']) if e_row['type'] in DISASTER_TYPE_TRANSLATIONS else 0)
                        with ec2:
                            e_loc = st.selectbox("District / Location:", ALL_DISTRICTS, index=ALL_DISTRICTS.index(e_row['location']) if e_row['location'] in ALL_DISTRICTS else 0)
                        with ec3:
                            e_sev = st.selectbox("Severity Level:", ["Critical", "High", "Medium", "Low"], index=["Critical", "High", "Medium", "Low"].index(e_row['severity']) if e_row['severity'] in ["Critical", "High", "Medium", "Low"] else 0)

                        ec4, ec5 = st.columns(2)
                        with ec4:
                            e_stat = st.selectbox("Live Operational Status:", ["Active", "Under Control", "Resolved"], index=["Active", "Under Control", "Resolved"].index(e_row['status']) if e_row['status'] in ["Active", "Under Control", "Resolved"] else 0)
                        with ec5:
                            e_contact = st.text_input("Reporter / Local Contact:", value=str(e_row['reporter_contact']))

                        e_desc = st.text_area("Detailed Description / Situation Notes:", value=str(e_row['description']))

                        e_save = st.form_submit_button("💾 " + ("परिवर्तन सुरक्षित करें" if is_hi else "Save Incident Changes"), type="primary")
                        if e_save:
                            edit_disaster(selected_e_id, e_type, e_loc, e_sev, e_desc, e_stat, e_contact)
                            st.success(f"Incident #{selected_e_id} updated successfully!")
                            st.rerun()

                # DISPATCH RESCUE TEAM
                with inc_act_dispatch:
                    st.markdown("##### 🚀 " + ("आपदा स्थल पर त्वरित राहत एवं बचाव दस्ता तैनात करें" if is_hi else "Deploy Emergency Rescue Teams"))
                    active_incidents = df_all[df_all['status'] != 'Resolved']
                    if not active_incidents.empty:
                        opt_disp = {row['id']: f"#{row['id']} — {row['type']} in {row['location']} [{row['severity']}]" for _, row in active_incidents.iterrows()}
                        sel_disp_id = st.selectbox("Select Target Incident:", opt_disp.keys(), format_func=lambda x: opt_disp[x], key="adm_disp_sel")

                        with st.form("dispatch_rescue_form"):
                            dc1, dc2 = st.columns(2)
                            with dc1:
                                team_name = st.selectbox("Rescue Unit / Battalion:", [
                                    "SDRF 1st Battalion (Jolly Grant, Dehradun)",
                                    "SDRF High Altitude Team (Joshimath / Chamoli)",
                                    "SDRF Quick Response Unit (Uttarkashi)",
                                    "SDRF River Rescue Team (Rishikesh / Rudraprayag)",
                                    "NDRF 15th Battalion (Regional Response Center)",
                                    "ITBP Mountain Rescue Wing (Pithoragarh)",
                                    "Uttarakhand Police Disaster Task Force (QRT)"
                                ])
                                team_lead = st.text_input("Incident / Unit Commander Name:", placeholder="e.g. Inspector R. S. Negi")
                            with dc2:
                                team_count = st.number_input("Deployed Personnel Strength (जवानों की संख्या):", min_value=2, max_value=200, value=15)
                                team_phone = st.text_input("Wireless / Satellite Phone:", value="0135-2710334")

                            disp_notes = st.text_area("Operational Directives / Equipment Orders:", placeholder="Deploy with motorized rescue boats, cutting equipment, trauma kits, satellite phones.")
                            disp_btn = st.form_submit_button("🚀 " + ("आधिकारिक तैनाती आदेश जारी करें" if is_hi else "Issue Official Deployment Order"), type="primary")

                            if disp_btn:
                                did_ret = dispatch_rescue_team(sel_disp_id, team_name, team_lead.strip() or "SDRF Officer In-charge", team_phone, team_count, disp_notes)
                                st.success(f"Rescue Unit '{team_name}' dispatched successfully to Incident #{sel_disp_id}!")
                                st.rerun()
                    else:
                        st.info("No active pending incidents requiring rescue deployment.")

                # ADD INCIDENT
                with inc_act_add:
                    st.markdown("##### ➕ " + ("कंट्रोल रूम से नई आपदा घटना दर्ज करें" if is_hi else "Directly Log Incident from Command Center"))
                    with st.form("admin_add_disaster_form"):
                        ac1, ac2, ac3 = st.columns(3)
                        with ac1:
                            new_dtype = st.selectbox("Disaster Type:", list(DISASTER_TYPE_TRANSLATIONS.keys()), key="adm_add_dt")
                        with ac2:
                            new_dist = st.selectbox("Affected District:", ALL_DISTRICTS, key="adm_add_dist")
                        with ac3:
                            new_sev = st.selectbox("Initial Severity:", ["Critical", "High", "Medium", "Low"], key="adm_add_sev")

                        new_desc = st.text_area("Initial SitRep / Officer Notes:", placeholder="Official verified report from District Emergency Operations Centre (DEOC)...")
                        new_rep = st.text_input("Reporting Authority / Source:", value="DEOC Officer / 112 Control Room")

                        if st.form_submit_button("➕ " + ("घटना दर्ज करें एवं पोर्टल पर प्रसारित करें" if is_hi else "Log Incident & Publish Alert"), type="primary"):
                            new_id = add_disaster(new_dtype, new_dist, new_sev, new_desc.strip() or f"{new_dtype} reported in {new_dist}", reporter_contact=new_rep)
                            st.success(f"Incident #{new_id} registered and published!")
                            st.rerun()

                # DELETE INCIDENT
                with inc_act_del:
                    st.markdown("##### 🗑️ " + ("गलत या निरस्त घटना हटाएं" if is_hi else "Purge Duplicate or False Incident Record"))
                    sel_del_id = st.selectbox("Select Incident to Delete:", options_edit.keys(), format_func=lambda x: options_edit[x], key="adm_del_sel")
                    st.warning(f"Warning: Deleting incident #{sel_del_id} will permanently remove it and its associated alerts.")
                    if st.button("🗑️ " + ("घटना हमेशा के लिए हटाएं (Confirm Delete)" if is_hi else "Permanently Delete Incident"), type="secondary"):
                        delete_disaster(sel_del_id)
                        st.success(f"Incident #{sel_del_id} deleted successfully.")
                        st.rerun()

        # ─────────────────────────────────────────────────────────────────────
        # TAB 2: HOSPITALS & MEDICAL CAPACITY
        # ─────────────────────────────────────────────────────────────────────
        with ad_tab2:
            st.subheader("🏥 " + ("अस्पताल एवं आईसीयू बेड प्रबंधन" if is_hi else "Hospital & ICU Bed Matrix Management"))
            hosp_df = get_hospitals_by_district()

            if not hosp_df.empty:
                st.dataframe(hosp_df[['id', 'name', 'district', 'beds_available', 'beds_total', 'contact']], use_container_width=True, hide_index=True)

                h_act_tab1, h_act_tab2, h_act_tab3 = st.tabs([
                    "⚡ " + ("उपलब्ध बेड अपडेट करें" if is_hi else "Quick Bed Updater"),
                    "➕ " + ("नया अस्पताल / फील्ड क्लिनिक जोड़ें" if is_hi else "Add New Hospital"),
                    "🗑️ " + ("अस्पताल हटाएं" if is_hi else "Remove Hospital")
                ])

                with h_act_tab1:
                    h_opt = {row['id']: f"#{row['id']} — {row['name']} ({row['district']}) | Beds: {row['beds_available']}/{row['beds_total']}" for _, row in hosp_df.iterrows()}
                    sel_hid = st.selectbox("Select Hospital:", h_opt.keys(), format_func=lambda x: h_opt[x], key="adm_h_sel")
                    curr_h = hosp_df.loc[hosp_df['id'] == sel_hid].iloc[0]

                    with st.form("quick_bed_form"):
                        c_b1, c_b2 = st.columns(2)
                        with c_b1:
                            new_avail_b = st.number_input("Available Free Beds (उपलब्ध रिक्त बेड):", min_value=0, max_value=10000, value=int(curr_h['beds_available']))
                        with c_b2:
                            new_tot_b = st.number_input("Total Beds Capacity (कुल क्षमता):", min_value=1, max_value=10000, value=int(curr_h['beds_total']))

                        if st.form_submit_button("💾 " + ("बेड संख्या सुरक्षित करें" if is_hi else "Save Bed Count"), type="primary"):
                            update_hospital_beds(sel_hid, new_avail_b, new_tot_b)
                            st.success("Hospital bed capacity updated!")
                            st.rerun()

                with h_act_tab2:
                    with st.form("add_new_hosp_form"):
                        ahc1, ahc2 = st.columns(2)
                        with ahc1:
                            new_h_name = st.text_input("Hospital Name (English):", placeholder="e.g. AIIMS Rishikesh Emergency Wing")
                            new_h_dist = st.selectbox("District:", ALL_DISTRICTS, key="adm_add_h_dist")
                        with ahc2:
                            new_h_name_hi = st.text_input("Hospital Name (Hindi):", placeholder="उदा: एम्स ऋषिकेश इमरजेंसी विंग")
                            new_h_phone = st.text_input("Emergency Doctor / Helpdesk Phone:", value="0135-2462000")

                        ahc3, ahc4 = st.columns(2)
                        with ahc3:
                            add_h_tot = st.number_input("Total Bed Capacity:", min_value=1, max_value=10000, value=250)
                        with ahc4:
                            add_h_avail = st.number_input("Currently Free Beds:", min_value=0, max_value=10000, value=120)

                        if st.form_submit_button("➕ " + ("अस्पताल जोड़ें" if is_hi else "Add Hospital Facility"), type="primary"):
                            if new_h_name.strip():
                                add_hospital(new_h_name.strip(), new_h_name_hi.strip() or new_h_name.strip(), new_h_dist, new_h_dist, add_h_tot, add_h_avail, new_h_phone)
                                st.success("New hospital registered!")
                                st.rerun()

                with h_act_tab3:
                    sel_del_h = st.selectbox("Select Hospital to Remove:", h_opt.keys(), format_func=lambda x: h_opt[x], key="adm_h_del_sel")
                    if st.button("🗑️ " + ("अस्पताल हटाएं (Confirm Delete)" if is_hi else "Delete Hospital Facility"), type="secondary"):
                        delete_hospital(sel_del_h)
                        st.success("Hospital removed.")
                        st.rerun()

        # ─────────────────────────────────────────────────────────────────────
        # TAB 3: RELIEF SHELTERS & CAMPS
        # ─────────────────────────────────────────────────────────────────────
        with ad_tab3:
            st.subheader("🏠 " + ("राहत शिविर एवं आश्रय स्थल प्रबंधन" if is_hi else "Relief Shelters & Evacuation Camps"))
            sh_df = get_shelters_by_district()

            if not sh_df.empty:
                st.dataframe(sh_df[['id', 'name', 'district', 'occupied', 'capacity', 'contact']], use_container_width=True, hide_index=True)

                s_act_tab1, s_act_tab2, s_act_tab3 = st.tabs([
                    "⚡ " + ("उपस्थिति संख्या अपडेट करें" if is_hi else "Occupancy Slider"),
                    "➕ " + ("नया राहत शिविर जोड़ें" if is_hi else "Add New Shelter Camp"),
                    "🗑️ " + ("शिविर हटाएं" if is_hi else "Remove Shelter")
                ])

                with s_act_tab1:
                    s_opt = {row['id']: f"#{row['id']} — {row['name']} ({row['district']}) | Occupied: {row['occupied']}/{row['capacity']}" for _, row in sh_df.iterrows()}
                    sel_sid = st.selectbox("Select Shelter:", s_opt.keys(), format_func=lambda x: s_opt[x], key="adm_s_sel")
                    curr_s = sh_df.loc[sh_df['id'] == sel_sid].iloc[0]

                    with st.form("quick_occ_form"):
                        new_occ = st.number_input("Current Occupants (उपस्थित लोग):", min_value=0, max_value=int(curr_s['capacity'])*2, value=int(curr_s['occupied']))
                        if st.form_submit_button("💾 " + ("उपस्थिति सुरक्षित करें" if is_hi else "Save Occupancy"), type="primary"):
                            update_shelter_occupancy(sel_sid, new_occ)
                            st.success("Shelter occupancy updated!")
                            st.rerun()

                with s_act_tab2:
                    with st.form("add_new_shelter_form"):
                        asc1, asc2 = st.columns(2)
                        with asc1:
                            new_s_name = st.text_input("Shelter Camp Name (English):", placeholder="e.g. Joshimath Relief Camp")
                            new_s_dist = st.selectbox("District:", ALL_DISTRICTS, key="adm_add_s_dist")
                        with asc2:
                            new_s_name_hi = st.text_input("Shelter Camp Name (Hindi):", placeholder="उदा: जोशीमठ राहत शिविर")
                            new_s_phone = st.text_input("Camp Incharge Contact:", value="9876543210")

                        new_s_cap = st.number_input("Maximum Shelter Capacity (Person count):", min_value=10, max_value=5000, value=300)

                        if st.form_submit_button("➕ " + ("राहत शिविर जोड़ें" if is_hi else "Register Relief Shelter"), type="primary"):
                            if new_s_name.strip():
                                add_shelter(new_s_name.strip(), new_s_name_hi.strip() or new_s_name.strip(), new_s_dist, new_s_dist, new_s_cap, 0, new_s_phone)
                                st.success("New relief shelter registered!")
                                st.rerun()

                with s_act_tab3:
                    sel_del_s = st.selectbox("Select Shelter to Remove:", s_opt.keys(), format_func=lambda x: s_opt[x], key="adm_s_del_sel")
                    if st.button("🗑️ " + ("शिविर हटाएं (Confirm Delete)" if is_hi else "Delete Shelter Camp"), type="secondary"):
                        delete_shelter(sel_del_s)
                        st.success("Shelter camp removed.")
                        st.rerun()

        # ─────────────────────────────────────────────────────────────────────
        # TAB 4: LOGISTICS & SUPPLIES
        # ─────────────────────────────────────────────────────────────────────
        with ad_tab4:
            st.subheader("📦 " + ("राशन, जल व आपदा राहत सामग्री भंडार" if is_hi else "Warehouse Logistics & Emergency Supplies Stockpile"))
            res_df = get_resources_by_district()

            if not res_df.empty:
                st.dataframe(res_df[['id', 'type', 'name', 'district', 'quantity', 'unit', 'available']], use_container_width=True, hide_index=True)

                r_act_tab1, r_act_tab2, r_act_tab3 = st.tabs([
                    "⚡ " + ("भंडार मात्रा अपडेट करें" if is_hi else "Modify Stock Quantity"),
                    "➕ " + ("नई सामग्री जोड़ें" if is_hi else "Add New Stockpile Item"),
                    "🗑️ " + ("सामग्री हटाएं" if is_hi else "Remove Stockpile Item")
                ])

                with r_act_tab1:
                    r_opt = {row['id']: f"#{row['id']} — {row['name']} ({row['district']}) | Qty: {row['quantity']} {row['unit']}" for _, row in res_df.iterrows()}
                    sel_rid = st.selectbox("Select Supply Item:", r_opt.keys(), format_func=lambda x: r_opt[x], key="adm_r_sel")
                    curr_r = res_df.loc[res_df['id'] == sel_rid].iloc[0]

                    with st.form("quick_r_stock_form"):
                        new_r_qty = st.number_input("Available Stock Quantity (उपलब्ध मात्रा):", min_value=0, max_value=1000000, value=int(curr_r['quantity']))
                        if st.form_submit_button("💾 " + ("मात्रा सुरक्षित करें" if is_hi else "Save Stock Quantity"), type="primary"):
                            edit_resource(sel_rid, curr_r['name'], new_r_qty, 1)
                            st.success("Stock quantity updated!")
                            st.rerun()

                with r_act_tab2:
                    with st.form("add_new_resource_form"):
                        arc1, arc2 = st.columns(2)
                        with arc1:
                            new_r_type = st.selectbox("Supply Category:", ["Food", "Water", "Medical", "Shelter", "Rescue Equipment", "Fuel & Energy"])
                            new_r_name = st.text_input("Supply Item Name (English):", placeholder="e.g. 5kg Family Ration Pack")
                        with arc2:
                            new_r_dist = st.selectbox("District Warehouse:", ALL_DISTRICTS, key="adm_add_r_dist")
                            new_r_name_hi = st.text_input("Supply Item Name (Hindi):", placeholder="उदा: 5 किग्रा सूखा पारिवारिक राशन किट")

                        arc3, arc4 = st.columns(2)
                        with arc3:
                            add_r_qty = st.number_input("Initial Quantity:", min_value=1, max_value=1000000, value=500)
                        with arc4:
                            add_r_unit = st.text_input("Unit of Measure:", value="Kits / Canisters")

                        if st.form_submit_button("➕ " + ("सामग्री भंडार में जोड़ें" if is_hi else "Add to Warehouse"), type="primary"):
                            if new_r_name.strip():
                                add_resource(new_r_type, new_r_type, new_r_name.strip(), new_r_name_hi.strip() or new_r_name.strip(), new_r_dist, new_r_dist, add_r_qty, add_r_unit)
                                st.success("New stockpile item added!")
                                st.rerun()

                with r_act_tab3:
                    sel_del_r = st.selectbox("Select Supply Item to Remove:", r_opt.keys(), format_func=lambda x: r_opt[x], key="adm_r_del_sel")
                    if st.button("🗑️ " + ("सामग्री हटाएं (Confirm Delete)" if is_hi else "Delete Supply Item"), type="secondary"):
                        delete_resource(sel_del_r)
                        st.success("Supply item removed.")
                        st.rerun()

        # ─────────────────────────────────────────────────────────────────────
        # TAB 5: EMERGENCY BROADCAST & CELL SIREN
        # ─────────────────────────────────────────────────────────────────────
        with ad_tab5:
            st.subheader("📢 " + ("आपातकालीन ब्रॉडकास्ट एवं मोबाइल सायरन अलर्ट" if is_hi else "Emergency Public Broadcast Transmitter"))

            # Quick Preset Templates
            st.markdown("##### ⚡ " + ("त्वरित अलर्ट टेम्पलेट चुनें" if is_hi else "Quick Alert Presets"))
            b_preset1, b_preset2, b_preset3 = st.columns(3)
            p_msg_hi, p_msg_en, p_sev = "", "", "High"
            if b_preset1.button("🌧️ " + ("भारी बारिश / फ्लैश फ्लड अलर्ट" if is_hi else "Flash Flood Warning")):
                p_msg_hi = "🚨 अति-गंभीर: निचले इलाकों व नदी तटों पर जलस्तर खतरे के निशान से ऊपर। सभी नागरिक तुरंत ऊंचे स्थानों पर जाएं।"
                p_msg_en = "CRITICAL ALERT: River water level crossed danger mark in low-lying areas. Move to high ground immediately."
                p_sev = "Critical"
            if b_preset2.button("⛰️ " + ("भूस्खलन मार्ग अवरुद्ध अलर्ट" if is_hi else "Highway Landslide Block")):
                p_msg_hi = "⚠️ उच्च चेतावनी: राष्ट्रीय राजमार्ग पर भारी मलबा आने से यातायात पूरी तरह बंद है। नजदीकी विश्राम स्थल पर रुकें।"
                p_msg_en = "HIGH WARNING: Major landslide debris blocked National Highway. Traffic halted. Stay at nearest transit camps."
                p_sev = "High"
            if b_preset3.button("🟢 " + ("मार्ग सुरक्षित / स्थिति सामान्य" if is_hi else "All Clear / Road Reopened")):
                p_msg_hi = "🟢 सुरक्षा अपडेट: मार्ग से मलबा हटा दिया गया है एवं यातायात सुचारू रूप से बहाल कर दिया गया है।"
                p_msg_en = "SAFETY UPDATE: Highway debris cleared and road reopened for vehicular movement."
                p_sev = "Low"

            with st.form("broadcast_alert_form_pro"):
                bc1, bc2 = st.columns(2)
                with bc1:
                    b_sev = st.selectbox(t("filter_severity", lang), ["Critical", "High", "Medium", "Low"], index=["Critical", "High", "Medium", "Low"].index(p_sev))
                with bc2:
                    b_target = st.selectbox("Target District / Audience", ["All Uttarakhand Districts", "Emergency Rescue Units Only"] + ALL_DISTRICTS)

                b_msg_hi = st.text_area("चेतावनी संदेश (हिंदी)", value=p_msg_hi, placeholder="उदा: भारी बारिश के चलते बद्रीनाथ राष्ट्रीय राजमार्ग अवरुद्ध है।")
                b_msg_en = st.text_area("Alert Message (English)", value=p_msg_en, placeholder="e.g. Heavy rainfall has disrupted Badrinath National Highway.")

                send_btn = st.form_submit_button("📡 " + ("आपातकालीन अलर्ट प्रसारित करें" if is_hi else "Transmit Live Broadcast Alert"), type="primary")
                if send_btn:
                    if b_msg_hi.strip() or b_msg_en.strip():
                        primary_en = b_msg_en.strip() if b_msg_en.strip() else b_msg_hi.strip()
                        primary_hi = b_msg_hi.strip() if b_msg_hi.strip() else b_msg_en.strip()
                        aid = add_custom_alert(None, primary_en, primary_hi, b_sev, b_target)
                        st.success(f"Broadcast Alert #{aid} transmitted successfully to live portal feed!")
                        st.rerun()
                    else:
                        st.error("Please enter a message before broadcasting.")

            st.markdown("---")
            st.markdown("##### 📜 " + ("सक्रिय अलर्ट सूची एवं प्रबंधन" if is_hi else "Active Broadcasts & Withdrawal"))
            df_active_alerts = get_all_alerts(limit=20)
            if not df_active_alerts.empty:
                for _, al in df_active_alerts.iterrows():
                    with st.container(border=True):
                        ac1, ac2 = st.columns([5, 1])
                        with ac1:
                            st.markdown(f"**#{al['id']} [{al['severity']}]** 🕐 `{al['timestamp']}` — Target: `{al['target']}`")
                            st.markdown(al['message'])
                        with ac2:
                            if st.button("🗑️ " + ("हटाएं" if is_hi else "Withdraw"), key=f"del_al_{al['id']}"):
                                delete_alert(al['id'])
                                st.success(f"Alert #{al['id']} withdrawn.")
                                st.rerun()

        # ─────────────────────────────────────────────────────────────────────
        # TAB 6: SUGGESTIONS & COMMUNITY INNOVATIONS REVIEW
        # ─────────────────────────────────────────────────────────────────────
        with ad_tab6:
            st.subheader("💡 " + ("नागरिक सुझाव एवं नवाचार समीक्षा" if is_hi else "Citizen Suggestions & Innovation Review"))
            df_sugg = get_all_suggestions()

            if not df_sugg.empty:
                st.markdown(f"Total community suggestions submitted: **{len(df_sugg)}**")
                for _, sg in df_sugg.iterrows():
                    with st.container(border=True):
                        sg_c1, sg_c2 = st.columns([4, 2])
                        with sg_c1:
                            st.markdown(f"### {sg['title']}")
                            st.markdown(sg['description'])
                            st.caption(f"👤 {sg['contributor']} | 📍 {sg['district']} | 👍 Upvotes: **{sg['upvotes']}** | 🕐 {sg['created_at']}")
                        with sg_c2:
                            st.markdown(f"**Current Status:** `{sg['status']}`")
                            new_s_stat = st.selectbox(
                                "Update Status:",
                                ["Under Review", "Approved / In Progress", "Implemented", "Closed"],
                                index=["Under Review", "Approved / In Progress", "Implemented", "Closed"].index(sg['status']) if sg['status'] in ["Under Review", "Approved / In Progress", "Implemented", "Closed"] else 0,
                                key=f"sg_stat_sel_{sg['id']}"
                            )
                            c_btn1, c_btn2 = st.columns(2)
                            with c_btn1:
                                if st.button("💾 " + ("सेव करें" if is_hi else "Save"), key=f"sg_save_{sg['id']}"):
                                    update_suggestion_status(sg['id'], new_s_stat)
                                    st.success("Status updated!")
                                    st.rerun()
                            with c_btn2:
                                if st.button("🗑️ " + ("हटाएं" if is_hi else "Delete"), key=f"sg_del_{sg['id']}"):
                                    delete_suggestion(sg['id'])
                                    st.success("Suggestion removed.")
                                    st.rerun()

        # ─────────────────────────────────────────────────────────────────────
        # TAB 7: FAKE NEWS & MISINFORMATION GRIEVANCE CELL
        # ─────────────────────────────────────────────────────────────────────
        with ad_tab7:
            st.subheader("⚖️ " + ("फर्जी सूचना निस्तारण एवं कानूनी प्रवर्तन सेल" if is_hi else "Misinformation & Fake News Enforcement Cell"))
            st.markdown(f"""
            <div style="background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.3);border-radius:10px;padding:12px 16px;margin-bottom:14px;">
                <div style="font-size:0.88rem;font-weight:800;color:#F87171;display:flex;align-items:center;gap:6px;">
                    ⚖️ {'आपदा प्रबंधन अधिनियम, 2005 (धारा 54) — वैधानिक प्रवर्तन' if is_hi else 'Disaster Management Act, 2005 (Section 54) — Statutory Enforcement'}
                </div>
                <div style="font-size:0.78rem;color:#CBD5E1;margin-top:4px;">
                    {'आपदा के दौरान झूठी चेतावनी, अफवाह या फर्जी सूचना प्रसारित करना 1 वर्ष तक के कारावास और जुर्माने से दंडनीय अपराध है।' if is_hi else 'Circulating false alarms or misleading disaster claims is a punishable offense with imprisonment up to 1 year or fine.'}
                </div>
            </div>
            """, unsafe_allow_html=True)

            fn_subtab1, fn_subtab2 = st.tabs([
                "🚩 " + ("नागरिक शिकायतों की समीक्षा" if is_hi else "Flagged Public Grievances"),
                "🚫 " + ("ब्लैकलिस्टेड नंबर सूची" if is_hi else "Blacklisted Callers Registry")
            ])

            with fn_subtab1:
                df_fake = get_all_fake_reports()
                if not df_fake.empty:
                    st.markdown(f"Total flagged misinformation claims: **{len(df_fake)}**")
                    for _, fr in df_fake.iterrows():
                        with st.container(border=True):
                            fc_c1, fc_c2 = st.columns([4, 2])
                            with fc_c1:
                                st.markdown(f"**Grievance #{fr['id']}** | Target: `{fr['item_type'].upper()} #{fr['item_id']}` | Status: `{fr['status']}`")
                                st.markdown(f"🚩 **Reason:** `{fr['reason']}`")
                                st.markdown(f"📝 **Details:** {fr['details']}")
                                st.caption(f"👤 Flagged by: {fr['flagged_by']} | 🕐 {fr['flagged_at']}")
                                if fr.get('action_notes'):
                                    st.info(f"👮 Action Taken: {fr['action_notes']}")

                            with fc_c2:
                                st.markdown("##### 👮 " + ("प्रशासनिक कार्रवाई" if is_hi else "Enforcement Action"))
                                act_choice = st.selectbox(
                                    "Select Action:",
                                    ["Action Taken / Blacklisted", "Fact-Check Alert Issued", "Dismissed (Genuine Info)", "Forwarded to Cyber Police"],
                                    key=f"act_sel_{fr['id']}"
                                )
                                admin_act_note = st.text_input("Officer Action Note:", placeholder="e.g. Number blacklisted & fact check posted", key=f"act_note_{fr['id']}")
                                
                                act_btn1, act_btn2 = st.columns(2)
                                with act_btn1:
                                    if st.button("⚖️ " + ("कार्रवाई लागू करें" if is_hi else "Apply Action"), key=f"apply_act_{fr['id']}"):
                                        resolve_fake_report(fr['id'], act_choice, admin_act_note.strip() or act_choice)
                                        st.success("Action recorded!")
                                        st.rerun()
                                with act_btn2:
                                    if fr['item_type'] == 'incident':
                                        if st.button("🗑️ " + ("आपदा हटाएं" if is_hi else "Purge Incident"), key=f"del_fake_inc_{fr['id']}"):
                                            delete_disaster(fr['item_id'])
                                            add_custom_alert(None, f"FACT CHECK: Incident #{fr['item_id']} was verified as a false alarm. Area is completely safe.", f"📢 फैक्ट चेक: घटना #{fr['item_id']} फर्जी सूचना पाई गई है। क्षेत्र पूर्णतः सुरक्षित है।", "Low")
                                            resolve_fake_report(fr['id'], "Action Taken / Blacklisted", "Incident deleted and fact-check retraction broadcasted")
                                            st.success("Fake incident purged & retraction alert issued!")
                                            st.rerun()

                else:
                    st.success("✅ " + ("वर्तमान में कोई फर्जी सूचना शिकायत लंबित नहीं है।" if is_hi else "No pending misinformation complaints. The system feed is verified and clean."))

            with fn_subtab2:
                st.markdown("##### 🚫 " + ("अवरुद्ध / ब्लैकलिस्टेड फोन नंबर" if is_hi else "Blacklisted Phone Registry"))
                with st.form("manual_blacklist_form"):
                    st.markdown("##### ➕ " + ("नया नंबर ब्लॉक करें" if is_hi else "Manually Blacklist Phone Number"))
                    bl_c1, bl_c2 = st.columns(2)
                    with bl_c1:
                        new_bl_phone = st.text_input("Phone Number to Block (उदा: 9876543210):")
                    with bl_c2:
                        new_bl_reason = st.text_input("Reason for Blocking:", value="Circulating false disaster rumors")
                    if st.form_submit_button("🚫 " + ("नंबर ब्लैकलिस्ट करें" if is_hi else "Blacklist Contact"), type="primary"):
                        if new_bl_phone.strip():
                            blacklist_contact(new_bl_phone.strip(), new_bl_reason.strip())
                            st.success(f"Phone {new_bl_phone} blacklisted successfully!")
                            st.rerun()

                df_banned = get_blacklisted_contacts()
                if not df_banned.empty:
                    st.dataframe(df_banned, use_container_width=True, hide_index=True)
                    unban_sel = st.selectbox("Select Phone to Restore:", df_banned['contact_phone'].tolist(), key="unban_sel")
                    if st.button("🟢 " + ("प्रतिबंध हटाएं (Unblock Number)" if is_hi else "Unban / Restore Number")):
                        unblacklist_contact(unban_sel)
                        st.success(f"Phone {unban_sel} unblocked.")
                        st.rerun()
                else:
                    st.info("No blacklisted phone numbers currently.")

        # ─────────────────────────────────────────────────────────────────────
        # TAB 8: SITUATION REPORT (SITREP) & DATA EXPORT CENTER
        # ─────────────────────────────────────────────────────────────────────
        with ad_tab8:
            st.subheader("📊 " + ("दैनिक स्थिति रिपोर्ट (SitRep) एवं डेटा एक्सपोर्ट" if is_hi else "Daily Situation Report (SitRep) & Data Exports"))

            st.markdown(f"""
            <div style="background:rgba(15,23,42,0.8);border:1px solid rgba(59,130,246,0.3);border-radius:12px;padding:16px;margin-bottom:16px;">
                <div style="font-size:1.1rem;font-weight:800;color:#38BDF8;">🏛️ STATE EMERGENCY OPERATIONS SITUATION REPORT (SitRep)</div>
                <div style="font-size:0.8rem;color:#94A3B8;">Govt of Uttarakhand · Disaster Mitigation & Management Centre (DMMC)</div>
                <div style="margin-top:10px;font-size:0.85rem;color:#CBD5E1;line-height:1.6;">
                    • <b>Generated On:</b> {datetime.now().strftime('%d %B %Y at %I:%M:%S %p IST')}<br/>
                    • <b>Total Incidents Tracked:</b> {stats['total_disasters']} (Active: {stats['active_disasters']}, Critical: {stats['critical_count']})<br/>
                    • <b>Medical Readiness:</b> {stats['beds_available']} Free Beds out of {stats['beds_total']} Statewide Capacity<br/>
                    • <b>Shelter Occupancy:</b> {stats['shelter_occupied']} / {stats['shelter_capacity']} Persons Housed
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("##### 📥 " + ("आधिकारिक डेटा CSV डाउनलोड" if is_hi else "Download Official Datasets (CSV)"))
            exp_c1, exp_c2, exp_c3, exp_c4 = st.columns(4)

            with exp_c1:
                df_d_exp = get_all_disasters()
                if not df_d_exp.empty:
                    st.download_button(
                        "📄 Incidents Data (CSV)",
                        data=df_d_exp.to_csv(index=False).encode('utf-8'),
                        file_name=f"uttarakhand_disasters_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            with exp_c2:
                df_h_exp = get_hospitals_by_district()
                if not df_h_exp.empty:
                    st.download_button(
                        "🏥 Hospitals Data (CSV)",
                        data=df_h_exp.to_csv(index=False).encode('utf-8'),
                        file_name=f"uttarakhand_hospitals_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            with exp_c3:
                df_s_exp = get_shelters_by_district()
                if not df_s_exp.empty:
                    st.download_button(
                        "🏠 Shelters Data (CSV)",
                        data=df_s_exp.to_csv(index=False).encode('utf-8'),
                        file_name=f"uttarakhand_shelters_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            with exp_c4:
                df_r_exp = get_resources_by_district()
                if not df_r_exp.empty:
                    st.download_button(
                        "📦 Supplies Data (CSV)",
                        data=df_r_exp.to_csv(index=False).encode('utf-8'),
                        file_name=f"uttarakhand_supplies_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

        # ─────────────────────────────────────────────────────────────────────
        # TAB 9: DATABASE TOOLS & RESEED
        # ─────────────────────────────────────────────────────────────────────
        with ad_tab9:
            st.subheader("⚙️ " + ("डेटाबेस ऑपरेशन्स एवं रीसीड टूल्स" if is_hi else "Database Tools & Reseeding Engine"))
            st.markdown("Reset database and reseed complete official Uttarakhand mock data with dynamic live timestamps across all 13 districts.")

            if st.button("🔄 " + ("संपूर्ण 13-जिला डेटाबेस रीसीड करें" if is_hi else "Reseed Full 13-District Database"), type="secondary"):
                sample_data.insert_sample_data(reset_existing=True)
                st.success("Database successfully reset and reseeded with live timestamps!")
                st.rerun()
