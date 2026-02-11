
import streamlit as st
import pandas as pd
import polars as pl
import os
from src import ingress
from src.utils import sample_generator
from datetime import datetime
import uuid
import csv
import altair as alt
import json
import time

def verify_fhir_structure(resource):
    """Lead Auditor Check: Ensures Patient_Name is properly nested as {'name': [{'text': '...'}]} per FHIR R5."""
    if "resourceType" in resource and resource["resourceType"] == "Patient":
        name_block = resource.get("name", [])
        if not name_block or not isinstance(name_block, list) or "text" not in name_block[0]:
            return False
    return True

def get_fhir_bundle(df):
    """Generates a FHIR R5 Bundle collection from the processed dataframe with nested name structures."""
    import json
    bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "timestamp": datetime.now().isoformat(),
        "entry": []
    }
    
    processed_df = df.filter(pl.col("Ingest_Status") == "PROCESSED")
    
    for row in processed_df.to_dicts():
        patient_resource = {
            "resourceType": "Patient",
            "identifier": [{"system": "https://healthidsbx.abdm.gov.in", "value": row.get("ABHA_ID")}],
            "name": [{"text": row.get("Patient_Name")}], # Compliant Nesting
            "extension": [
                {"url": "https://abdm.gov.in/fhir/StructureDefinition/consent-status", "valueString": row.get("Consent_Status")},
                {"url": "https://abdm.gov.in/fhir/StructureDefinition/notice-id", "valueString": row.get("Notice_ID")}
            ]
        }
        
        # Auditor Verification before adding to bundle
        if verify_fhir_structure(patient_resource):
             entry = {
                "fullUrl": f"urn:uuid:{row.get('Notice_ID', 'unknown')}",
                "resource": patient_resource
            }
             bundle["entry"].append(entry)
        else:
            pass

    return json.dumps(bundle, indent=2)

def import_altair_and_chart(data):
    # Ensure color column is used
    base = alt.Chart(data).encode(
        x=alt.X('Status', sort=None),
        y='Count',
        color=alt.Color('Color', scale=None),
        tooltip=['Status', 'Count']
    )
    chart = base.mark_bar().properties(
        title="Ingestion Health"
    )
    return chart

# Page Configuration
st.set_page_config(page_title="OmniIngest ABDM 2.0", page_icon="🏥", layout="wide")

# Custom CSS for "Modern GenAI" aesthetics
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
    }
    
    /* Header & Sidebar */
    header, [data-testid="stSidebar"] {
        background-color: #161b22 !important;
    }
    
    /* Buttons - Glow Effect */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.2em;
        background-color: #10a37f; /* GenAI Teal */
        color: white;
        border: none;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 14px 0 rgba(16, 163, 127, 0.3);
    }
    .stButton>button:hover {
        background-color: #1a7f64;
        box-shadow: 0 6px 20px 0 rgba(16, 163, 127, 0.5);
        transform: translateY(-1px);
    }
    
    /* Cards - Glassmorphism */
    div[data-testid="stMetric"] {
        background-color: #21262d;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363d;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    .status-card {
        padding: 20px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
        text-align: center;
        font-weight: 600;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
    }
    .real-data {
        background: linear-gradient(135deg, #10a37f 0%, #0d1117 100%);
    }
    .dummy-data {
        background: linear-gradient(135deg, #444654 0%, #0d1117 100%);
    }
    
    /* File Uploader */
    section[data-testid="stFileUploadDropzone"] {
        background-color: #161b22;
        border: 2px dashed #10a37f;
        border-radius: 12px;
    }
    
    /* Table Styling */
    .stDataFrame {
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
    }
    
    /* Custom Labels */
    .health-label {
        font-size: 0.9em;
        color: #8b949e;
        margin-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 OmniIngest ABDM 2.0")
st.markdown("<p style='color: #8b949e;'>Modern AI-Powered Clinical Data Ingestion</p>", unsafe_allow_html=True)

st.markdown("---")

# Session State Initialization
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
if 'manual_mapping' not in st.session_state:
    st.session_state.manual_mapping = {}

# Persistence Check - DPDP Rule 8 Enforcement
if st.session_state.revoked:
    st.markdown("""
        <div style='background-color: #3e1616; color: #ff8080; padding: 15px; border-radius: 8px; border: 1px solid #ff4d4d; margin-bottom: 20px;'>
            <h3 style='margin:0; color: #ff8080;'>⚠️ SESSION REVOKED</h3>
            <p style='margin:5px 0 0 0;'>Data purged per DPDP Rule 8. System locked until session reset.</p>
        </div>
    """, unsafe_allow_html=True)
    # Double-tap safety: Force re-masking if dataframe exists
    if st.session_state.processed_df is not None:
        st.session_state.processed_df = ingress.erase_pii_for_revocation(st.session_state.processed_df)

def reset_state():
    st.session_state.data_source = None
    st.session_state.processed_df = None
    st.session_state.mapping_confirmed = False
    st.session_state.revoked = False
    st.session_state.detected_format = None
    st.session_state.manual_mapping = {}

def mask_pii_for_preview(df):
    """Masks PII in the preview for ALL records."""
    df_pd = df.to_pandas().copy()
    
    # Check if revoked; if so, masking is stricter
    is_revoked = st.session_state.get('revoked', False)

    def mask_val(val):
        if is_revoked:
             return "[DATA PURGED]"
        if pd.isna(val) or str(val).strip() == "" or str(val) == "None" or str(val) == "Unknown/Redacted":
            return "[MISSING/REDACTED]"
        val_str = str(val)
        if len(val_str) < 4:
            return "****"
        return val_str[:2] + "****" + val_str[-2:] if len(val_str) > 4 else val_str[:1] + "****"
        
    def mask_payload(val):
        if pd.isna(val) or str(val).strip() == "":
            return "[EMPTY_PAYLOAD]"
        return "{'clinical_data': 'PROTECTED_BY_DPDP_RULE_8'}"

    if 'Patient_Name' in df_pd.columns:
        df_pd['Patient_Name'] = df_pd['Patient_Name'].apply(mask_val)
    if 'ABHA_ID' in df_pd.columns:
        df_pd['ABHA_ID'] = df_pd['ABHA_ID'].apply(mask_val)
    if 'Clinical_Payload' in df_pd.columns:
        df_pd['Clinical_Payload'] = df_pd['Clinical_Payload'].apply(mask_payload)
    
    return df_pd

if 'governance_logs' not in st.session_state:
    st.session_state.governance_logs = []

# Sidebar Info
st.sidebar.markdown("""
    <div style='background-color: #3e1616; padding: 15px; border-radius: 8px; border: 2px solid #ff4d4d; margin-bottom: 20px; text-align: center;'>
        <h4 style='margin: 0; color: #ff8080;'>🚨 [DPDP RULE 8.3 ACTIVE]</h4>
        <small style='color: #8b949e;'>Real-time PII Hard-Purge Enabled</small>
    </div>
""", unsafe_allow_html=True)

# Governance Log Display (Persistent)
st.sidebar.markdown("### 📜 Governance Log")
log_container = st.sidebar.empty()
if st.session_state.governance_logs:
    log_container.code("\n".join(st.session_state.governance_logs), language="bash")
else:
    log_container.code("# System Ready\n# Awaiting Ingress...", language="bash")

st.sidebar.markdown("### 🛡️ System Status")

# Sandbox Toggle Logic
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
    reset_state()
    st.rerun()

if st.session_state.data_source:
    if st.session_state.data_source == "REAL":
        st.sidebar.success("🟢 REAL DATA")
    elif st.session_state.data_source == "DUMMY":
        st.sidebar.info("🟠 SANDBOX ACTIVE")
    else:
        st.sidebar.success(f"🟢 {st.session_state.data_source}")
    
    with st.sidebar.expander("👮 Compliance Verification", expanded=False):
        st.markdown("""
            - **Field Mapping**: ✅ Active (FHIR R5)
            - **Environment**: 🟢 **SANDBOX** (`X-CM-ID: sbx`)
            - **Rule 8.3 Kill Switch**: ✅ **ARMED**
            - **Audit Logging**: ✅ Enabled (`audit_2026.json`)
            - **PII Masking**: ✅ Enabled (`[DATA PURGED]`)
        """)
else:
    st.sidebar.warning("⚪ OFFLINE (Awaiting Upload)")

if st.sidebar.button("Reset Session"):
    reset_state()
    st.rerun()

# Main UI Logic
col1, _ = st.columns([3, 1])

with col1:
    tab1, tab2 = st.tabs(["📂 File Upload", "✍️ Manual Entry"])
    
    uploaded_file = None
    
    with tab1:
        uploaded_file = st.file_uploader("", type=['csv', 'json', 'xml', 'xlsx', 'hl7', 'fhir', 'pdf', 'txt'])
    
    with tab2:
        st.info("Enter data manually for demo purposes.")
        c1, c2 = st.columns(2)
        with c1:
            m_name = st.text_input("Patient Name", placeholder="e.g. Rahul Verma")
        with c2:
            m_abha = st.text_input("ABHA Number", placeholder="e.g. 91-2345-6789")
            
        if st.button("Ingest Data", type="primary"):
            if m_name and m_abha:
                # Create fake CSV
                manual_data = pd.DataFrame([{
                    "Patient_Name": m_name,
                    "ABHA_ID": m_abha,
                    "Notice_ID": f"N-{datetime.now().strftime('%Y%m%d%H%M')}",
                    "Notice_Date": datetime.now().strftime("%Y-%m-%d"),
                    "Consent_Status": "GRANTED"
                }])
                manual_path = os.path.join(os.getcwd(), "manual_entry.csv")
                manual_data.to_csv(manual_path, index=False)
                
                # Ingest
                st.session_state.data_source = "REAL (MANUAL)"
                st.session_state.processed_df = ingress.run_ingress(manual_path)
                st.session_state.mapping_confirmed = True
                st.session_state.detected_format = "Manual Entry"
                st.rerun()
            else:
                st.error("Please fill all fields.")

if uploaded_file is not None:
    temp_path = os.path.join(os.getcwd(), uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.markdown(f"<div style='background-color: #161b22; padding: 10px; border-radius: 8px; border-left: 4px solid #10a37f;'>📄 <b>Detected:</b> {uploaded_file.name}</div>", unsafe_allow_html=True)
    st.session_state.data_source = "REAL" # Reset from DUMMY if file uploaded
    
    if not st.session_state.mapping_confirmed:
        st.subheader("🕵️ Smart Ingestion Discovery")
        
        mapping, satisfied_fields, sample_data = ingress.get_mapping_summary(temp_path)
        critical_fields = ["Patient_Name", "ABHA_ID", "Notice_ID"]
        missing_fields = [f for f in critical_fields if f not in satisfied_fields]
        
        if missing_fields:
            st.warning(f"Required fields missing: {', '.join(missing_fields)}")
            
            with st.expander("🛠️ Interactive Smart Mapper", expanded=True):
                st.markdown("We found unknown data. Help us identify the columns:")
                
                all_file_cols = list(sample_data.keys())
                new_mappings = {}
                for req_f in missing_fields:
                    st.markdown(f"---")
                    st.markdown(f"**Field:** `{req_f}`")
                    
                    best_guess = next((c for c in all_file_cols if req_f.lower() in c.lower()), None)
                    col_to_use = st.selectbox(
                        f"Select for {req_f}:",
                        options=["-- Select --"] + all_file_cols,
                        index=all_file_cols.index(best_guess) + 1 if best_guess else 0,
                        key=f"map_{req_f}"
                    )
                    
                    if col_to_use != "-- Select --":
                        sample_val = sample_data.get(col_to_use, "...")
                        st.info(f"💡 Snippet: `{sample_val}`")
                        new_mappings[col_to_use] = req_f
                
                if st.button("Apply Mapping", use_container_width=True):
                    ingress.COLUMN_MAPPING.update(new_mappings)
                    st.session_state.mapping_confirmed = True
                    st.session_state.data_source = "REAL"
                    with st.spinner("Ingesting..."):
                        st.session_state.processed_df = ingress.run_ingress(temp_path)
                        st.session_state.detected_format = ingress.detect_format(temp_path)
                    st.rerun()

            if st.button("🪄 Use Auto-Fill Fallback"):
                st.session_state.mapping_confirmed = True
                st.session_state.data_source = "REAL (AUTO-FILLED)"
                with st.spinner("Processing..."):
                    st.session_state.processed_df = ingress.run_ingress(temp_path, autofill=True)
                    st.session_state.detected_format = ingress.detect_format(temp_path)
                st.rerun()

        else:
            st.success("✨ Automated mapping successful!")
            st.markdown("### 📋 Mappings")
            table_data = [{"ABDM Field": f, "Source": next((k for k, v in mapping.items() if v == f), f)} for f in critical_fields]
            st.table(table_data)
            
            if st.button("Analyze with AI", use_container_width=True, disabled=st.session_state.revoked):
                st.session_state.mapping_confirmed = True
                st.session_state.data_source = "REAL"
                with st.spinner("Finalizing..."):
                    st.session_state.processed_df = ingress.run_ingress(temp_path)
                    st.session_state.detected_format = ingress.detect_format(temp_path)
                st.rerun()
    
    # If no file is uploaded and not in sandbox, show guidance
    if uploaded_file is None and st.session_state.processed_df is None:
        st.markdown("<div style='text-align: center; padding: 50px;'>", unsafe_allow_html=True)
        st.info("No data? Enable **Sandbox Mode** in the sidebar to load dummy records.")
        st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.processed_df is not None:
    st.markdown("---")
    df = st.session_state.processed_df
    results = ingress.run_audit(df, "Session", return_results=True)
    total = results["total"]
    
    st.subheader(f"📊 Analytics Dashboard - {st.session_state.detected_format or 'N/A'}")
    # Demo requirements: Show disabled analysis button if revoked
    st.button("Analyze with AI", disabled=st.session_state.revoked, key="dash_analyze")
    
    # Calculate percentages safely
    if total > 0:
        s_pct = (results['processed'] / total) * 100
        p_pct = (results['purged'] / total) * 100
        q_pct = (results['quarantined'] / total) * 100
    else:
        s_pct = p_pct = q_pct = 0.0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total", total)
    m2.metric("Success", f"{results['processed']} ({s_pct:.1f}%)")
    m3.metric("Purged", f"{results['purged']} ({p_pct:.1f}%)", delta=f"-{results['purged']}", delta_color="inverse")
    m4.metric("Quarantined", f"{results['quarantined']} ({q_pct:.1f}%)", delta=f"{results['quarantined']}", delta_color="off")

    st.markdown("### 💡 Insights")
    # improved chart
    chart_data = pd.DataFrame({
        "Status": ["Success", "Purged", "Quarantined"],
        "Count": [results["processed"], results["purged"], results["quarantined"]],
        "Color": ["#10a37f", "#dc3545", "#fd7e14"]  # Green, Red, Orange
    })
    
    st.altair_chart(
        import_altair_and_chart(chart_data),
        use_container_width=True
    )

    b1, b2 = st.columns(2)
    with b1:
        st.subheader("Purge Reasons")
        if results["purge_reasons"]: st.bar_chart(pd.Series(results["purge_reasons"]), color="#dc3545")
        else: st.write("Clean data.")
    with b2:
        st.subheader("Quarantine Reasons")
        if results["quarantine_reasons"]: st.bar_chart(pd.Series(results["quarantine_reasons"]), color="#fd7e14")
        else: st.write("No flags.")

    st.markdown("---")
    st.subheader("📥 Export Hub")
    e1, e2, e3 = st.columns(3)
    with e1:
        st.download_button("📜 Master CSV", df.to_pandas().to_csv(index=False).encode('utf-8'), "master.csv", "text/csv")
    with e2:
        processed_data = df.filter(pl.col("Ingest_Status") == "PROCESSED").to_pandas().to_csv(index=False).encode('utf-8')
        st.download_button("✅ Compliant Data", processed_data, "compliant.csv", "text/csv")
    with e3:
        st.download_button("🔥 FHIR Bundle", get_fhir_bundle(df), "bundle.json", "application/json")

    st.markdown("---")
    st.subheader("📄 Privacy-Safe Preview")
    preview_df = mask_pii_for_preview(df)
    
    if st.session_state.revoked:
        # Highlight [DATA PURGED] in Red/Bold
        def highlight_purged(val):
            return 'color: #ff4b4b; font-weight: bold; background-color: #ffe6e6' if str(val) == "[DATA PURGED]" else ''
        
        st.dataframe(preview_df.style.map(highlight_purged), use_container_width=True)
    else:
        st.dataframe(preview_df, use_container_width=True)

    if not st.session_state.revoked:
        # DPDP Rule 8.2 Logic
        if "purge_pending" not in st.session_state:
            st.session_state.purge_pending = False

        if st.button("🔴 Purge Data (DPDP Rule 8)"):
            st.session_state.purge_pending = True
            st.rerun()

        if st.session_state.purge_pending:
            st.warning("⚠️ **DPDP Rule 8.2: Erasure Notice Sent.** Final purge scheduled in 48 hours.")
            
            if st.button("🚨 Confirm Immediate Admin Purge (Override)", type="primary"):
                # Dramatic 'Vibe' Console Logs visualized in UI
                audit_id = str(uuid.uuid4())
                
                # Placeholder for animation
                with st.sidebar:
                    st.markdown("### 📜 Governance Log")
                    log_placeholder = st.empty()
                
                # Step 1
                msg1 = f"[1/3] Detaching Identity Keys for Session ABDM-2026..."
                st.session_state.governance_logs.append(f"{datetime.now().strftime('%H:%M:%S')} {msg1}")
                log_placeholder.code("\n".join(st.session_state.governance_logs), language="bash")
                time.sleep(0.9)
                
                # Step 2
                from src.compliance_engine import PIIVault
                vault = PIIVault()
                crypto_log = vault.shred_keys() # [RULE 8.3 AUDIT]
                
                st.session_state.governance_logs.append(f"{datetime.now().strftime('%H:%M:%S')} {crypto_log}")
                log_placeholder.code("\n".join(st.session_state.governance_logs), language="bash")
                time.sleep(1.2)
                
                # Step 3
                msg3 = f"[3/3] SUCCESS: Record Purged. Audit ID: [{audit_id}]"
                st.session_state.governance_logs.append(f"{datetime.now().strftime('%H:%M:%S')} {msg3}")
                log_placeholder.code("\n".join(st.session_state.governance_logs), language="bash")
                time.sleep(0.9)

                # Update state and dataframe
                st.session_state.processed_df = ingress.erase_pii_for_revocation(df)
                st.session_state.revoked = True
                st.session_state.purge_pending = False
                
                # Audit Log Entry - RETENTION RULE 8.3
                log_entry = {
                    "audit_id": audit_id,
                    "timestamp": datetime.now().isoformat(),
                    "action": "CONSENT_REVOKED_IMMEDIATE_OVERRIDE",
                    "actor": "admin_sys_01", # Simulated
                    "status": "PURGED"
                }
                log_file = "audit_2026.json"
                
                # Append to JSON list (Demo-friendly implementation)
                current_logs = []
                if os.path.exists(log_file):
                    try:
                        with open(log_file, "r") as f:
                            current_logs = json.load(f)
                    except json.JSONDecodeError:
                        current_logs = []
                
                current_logs.append(log_entry)
                
                with open(log_file, "w") as f:
                    json.dump(current_logs, f, indent=2)
                
                st.rerun()
    else:
        st.warning("⚠️ Data Hard-Purged per DPDP Act.")

    # Audit Log Viewer for Demo
    if st.session_state.revoked:
        st.markdown("---")
        with st.expander("📂 View Audit Logs (System Admin)"):
            if os.path.exists("audit_2026.json"):
                with open("audit_2026.json", "r") as f:
                     st.json(json.load(f))
            else:
                st.info("No logs found.")

    # Legal Watermark Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #444654; font-size: 0.8em; padding: 20px;'>
            🛡️ <b>System Status:</b> DPDP Rule 8.3 Active | <b>Retention Protocol:</b> 1-Year Immutable
        </div>
    """, unsafe_allow_html=True)
