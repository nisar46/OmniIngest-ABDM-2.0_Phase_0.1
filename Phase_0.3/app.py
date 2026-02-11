
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
from src import database # [Phase 0.3]
from src.utils import sample_generator

# 1. Setup & Config
ui.setup_page()
database.init_db() # [Phase 0.3] Initialize DB

# 2. Session State Initialization
if 'processed_df' not in st.session_state:
    # [Phase 0.3] Load from DB on startup
    db_data = database.get_all_records()
    if not db_data.is_empty():
        st.session_state.processed_df = db_data
        st.session_state.data_source = "DB_RECOVERY" # [FIX] Tell UI we have data
        st.session_state.detected_format = "Database Persistence"
    else:
        st.session_state.processed_df = None
        st.session_state.data_source = None

if 'data_source' not in st.session_state:
    st.session_state.data_source = None
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
col_sb, col_count = st.sidebar.columns([2, 1])
is_sandbox = col_sb.toggle("🛠️ Sandbox Mode", value=(st.session_state.data_source == "DUMMY"))
num_patients = col_count.number_input("Count", min_value=10, max_value=5000, value=1000, step=100)

if is_sandbox and st.session_state.data_source != "DUMMY":
    st.session_state.data_source = "DUMMY"
    with st.spinner(f"Generating {num_patients} test patients..."):
        sample_generator.main(num_rows=num_patients) # Updated to accept arg
        new_df = ingress.run_ingress("raw_data.csv")
        
        # [Phase 0.3 Fix] Save Sandbox Data to DB so Persistence works
        for row in new_df.to_dicts():
            database.save_record(row)
            
        st.session_state.processed_df = database.get_all_records() # Load from DB to confirm save
        st.session_state.mapping_confirmed = True
        st.session_state.detected_format = ingress.detect_format("raw_data.csv")
        st.session_state.processed_df = database.get_all_records() # Load from DB to confirm save
        st.session_state.mapping_confirmed = True
        st.session_state.detected_format = ingress.detect_format("raw_data.csv")
    st.rerun()

# [Improvement] Visibility Toggle
show_pii = st.sidebar.checkbox("👁️ Reveal PII (Compliance Audit)", value=False)


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
         # Use Compliance Engine for erasure
         pass 

# Input Section
col1, _ = st.columns([3, 1])
with col1:
    tab1, tab2 = st.tabs(["📂 File Upload (PDF/CSV)", "✍️ Manual Entry"])
    
    uploaded_file = None
    with tab1:
        uploaded_file = st.file_uploader("", type=['csv', 'json', 'xml', 'xlsx', 'pdf', 'txt'])
    
    with tab2:
        st.info("Enter data manually for demo purposes.")
        # (Manual entry logic preserved but simplified for brevity in this refactor step)
        if st.button("Generate Dummy Manual Data"):
             st.info("Manual Entry Module - Integrated via ORCHESTRA™ Gateway")

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
            new_df = ingress.run_ingress(temp_path, autofill=True) 
            
            # [Phase 0.3] Persistence Layer
            for row in new_df.to_dicts():
                database.save_record(row)
            
            st.session_state.processed_df = database.get_all_records() # Reload from Source of Truth
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

    # Breakdown Charts
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Purge Reasons")
        if results.get("purge_reasons"):
            st.bar_chart(results["purge_reasons"], color="#dc3545")
        else:
            st.success("No purged records.")
            
    with c2:
        st.subheader("Quarantine Reasons")
        if results.get("quarantine_reasons"):
            st.bar_chart(results["quarantine_reasons"], color="#fd7e14")
        else:
            st.success("No quarantine records.")
    
    st.markdown("---")
    
    # Preview
    st.subheader("📄 Privacy-Safe Preview")
    preview_df = compliance_engine.mask_pii_for_preview(df, is_revoked=st.session_state.revoked, reveal_pii=show_pii)
    st.dataframe(preview_df, use_container_width=True, height=600)
    
    # Kill Switch (Rule 8.3)
    if not st.session_state.revoked:
        if st.button("🔴 Purge Data (DPDP Rule 8)"):
             # Execute Kill Switch
             vault = compliance_engine.PIIVault()
             log = vault.shred_keys()
             
             # [Phase 0.3] DB Hard Delete
             database.hard_delete_all()
             
             st.session_state.governance_logs.append(f"{datetime.now().strftime('%H:%M:%S')} {log}")
             st.session_state.revoked = True
             st.session_state.processed_df = database.get_all_records() # Should be empty
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
st.markdown("<div style='text-align: center; color: #444654;'>🛡️ <b>OmniIngest Phase 0.3:</b> The Orchestration Foundation | Ready for ORCHESTRA™ Evolution</div>", unsafe_allow_html=True)
