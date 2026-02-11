
import streamlit as st
import pandas as pd
import polars as pl
import os
import time
from datetime import datetime
import uuid
import json

# Local Modules (Refactored Phase 0.2)
from src import ui
from src import ingress
from src import compliance_engine
# Phase 0.2 does NOT use database yet
from src.utils import sample_generator

# 1. Setup & Config
ui.setup_page()

# 2. Session State Initialization
if 'data_source' not in st.session_state:
    st.session_state.data_source = None
if 'processed_df' not in st.session_state:
    st.session_state.processed_df = None
if 'mapping_confirmed' not in st.session_state:
    st.session_state.mapping_confirmed = False
if 'revoked' not in st.session_state:
    st.session_state.revoked = False
if 'detected_format' not in st.session_state:
    st.session_state.detected_format = None
if 'governance_logs' not in st.session_state:
    st.session_state.governance_logs = []

# 3. Sidebar & Governance
if st.session_state.revoked:
    ui.render_governance_sidebar(st.session_state.governance_logs)
else:
    # Standard Sidebar
    ui.render_governance_sidebar(st.session_state.governance_logs)

st.sidebar.markdown("### 🛡️ System Status")

# Sandbox Toggle
is_sandbox = st.sidebar.toggle("🛠️ Sandbox Mode", value=(st.session_state.data_source == "DUMMY"))
if is_sandbox and st.session_state.data_source != "DUMMY":
    st.session_state.data_source = "DUMMY"
    with st.spinner("Building test environment..."):
        sample_generator.main()
        st.session_state.processed_df = ingress.run_ingress("raw_data.csv")
        st.session_state.mapping_confirmed = True
        st.session_state.detected_format = ingress.detect_format("raw_data.csv")
    st.rerun()
elif not is_sandbox and st.session_state.data_source == "DUMMY":
    st.session_state.data_source = None
    st.session_state.processed_df = None
    st.rerun()

if st.sidebar.button("Reset Session"):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()


# 4. Main Layout
ui.render_header()

if st.session_state.revoked:
    ui.render_revoked_warning()
    # Double-tap safety
    if st.session_state.processed_df is not None:
         st.session_state.processed_df = compliance_engine.mask_pii_for_preview(st.session_state.processed_df, is_revoked=True)

# Input Section
col1, _ = st.columns([3, 1])
with col1:
    tab1, tab2 = st.tabs(["📂 File Upload (PDF/CSV)", "✍️ Manual Entry"])
    
    uploaded_file = None
    with tab1:
        uploaded_file = st.file_uploader("", type=['csv', 'json', 'xml', 'xlsx', 'pdf', 'txt'])
    
    with tab2:
        st.info("Manual Entry: Coming in future updates.")

# File Processing Logic
if uploaded_file is not None:
    temp_path = os.path.join(os.getcwd(), uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.markdown(f"<div style='background-color: #161b22; padding: 10px; border-radius: 8px; border-left: 4px solid #10a37f;'>📄 <b>Detected:</b> {uploaded_file.name}</div>", unsafe_allow_html=True)
    st.session_state.data_source = "REAL"
    
    # Auto-Ingest
    if not st.session_state.mapping_confirmed:
        with st.spinner("🕵️ OmniIngest Smart-Scan..."):
            # Using the new ingress that handles PDF
            st.session_state.processed_df = ingress.run_ingress(temp_path, autofill=True)
            st.session_state.detected_format = ingress.detect_format(temp_path)
            st.session_state.mapping_confirmed = True
        st.rerun()

# Dashboard & Analytics
if st.session_state.processed_df is not None:
    st.markdown("---")
    df = st.session_state.processed_df
    
    # Audit Run
    results = ingress.run_audit(df, "Session", return_results=True)
    
    st.subheader(f"📊 Analytics Dashboard - {st.session_state.detected_format or 'N/A'}")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total", results['total'])
    m2.metric("Success", results['processed'])
    m3.metric("Purged", results['purged'])
    m4.metric("Quarantined", results['quarantined'])

    # Charts
    chart_data = pd.DataFrame({
        "Status": ["Success", "Purged", "Quarantined"],
        "Count": [results["processed"], results["purged"], results["quarantined"]],
        "Color": ["#10a37f", "#dc3545", "#fd7e14"] 
    })
    st.altair_chart(ui.get_chart(chart_data), use_container_width=True)
    
    st.markdown("---")
    
    # Preview
    st.subheader("📄 Privacy-Safe Preview")
    preview_df = compliance_engine.mask_pii_for_preview(df, is_revoked=st.session_state.revoked)
    st.dataframe(preview_df, use_container_width=True)
    
    # Kill Switch (Rule 8.3)
    if not st.session_state.revoked:
        if st.button("🔴 Purge Data (DPDP Rule 8)"):
             # Execute Kill Switch
             vault = compliance_engine.PIIVault()
             log = vault.shred_keys()
             
             st.session_state.governance_logs.append(f"{datetime.now().strftime('%H:%M:%S')} {log}")
             st.session_state.revoked = True
             # Explicit PII erasure in dataframe since we don't have DB
             st.session_state.processed_df = ingress.erase_pii_for_revocation(df)
             st.rerun()

    # Exports
    st.markdown("---")
    st.subheader("📥 Export Hub")
    if not st.session_state.revoked:
        e1, e2 = st.columns(2)
        with e1:
             st.download_button("✅ FHIR Bundle (R5)", compliance_engine.get_fhir_bundle(df), "bundle.json", "application/json")
        with e2:
             st.download_button("📜 Master CSV", df.write_csv(), "master.csv", "text/csv")
    else:
        st.error("Exports Disabled: Data Purged.")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #444654;'>🛡️ <b>OmniIngest Phase 0.2:</b> The Hardening | Modular Architecture</div>", unsafe_allow_html=True)
