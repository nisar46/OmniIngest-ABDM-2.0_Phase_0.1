import streamlit as st
import pandas as pd
import polars as pl
import os
import ingress
import create_sample_data
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="OmniIngest ABDM 2.0", page_icon="🏥", layout="wide")

# Custom CSS for "ChatGPT Health" aesthetics
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
        background-color: #10a37f; /* ChatGPT Teal */
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

def reset_state():
    st.session_state.data_source = None
    st.session_state.processed_df = None
    st.session_state.mapping_confirmed = False
    st.session_state.revoked = False
    st.session_state.detected_format = None
    st.session_state.manual_mapping = {}

def get_fhir_bundle(df):
    """Generates a FHIR R5 Bundle collection from the processed dataframe."""
    import json
    bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "timestamp": datetime.now().isoformat(),
        "entry": []
    }
    
    processed_df = df.filter(pl.col("Ingest_Status") == "PROCESSED")
    
    for row in processed_df.to_dicts():
        entry = {
            "fullUrl": f"urn:uuid:{row.get('Notice_ID', 'unknown')}",
            "resource": {
                "resourceType": "Patient",
                "identifier": [{"system": "https://abdm.gov.in", "value": row.get("ABHA_ID")}],
                "name": [{"text": row.get("Patient_Name")}],
                "extension": [
                    {"url": "https://abdm.gov.in/fhir/StructureDefinition/consent-status", "valueString": row.get("Consent_Status")},
                    {"url": "https://abdm.gov.in/fhir/StructureDefinition/notice-id", "valueString": row.get("Notice_ID")}
                ]
            }
        }
        bundle["entry"].append(entry)
    return json.dumps(bundle, indent=2)

def mask_pii_for_preview(df):
    """Masks PII in the preview for ALL records."""
    df_pd = df.to_pandas().copy()
    
    def mask_val(val):
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

# Sidebar Info
st.sidebar.markdown("### 🛡️ System Status")
if st.session_state.data_source:
    if st.session_state.data_source == "REAL":
        st.sidebar.success("🟢 REAL DATA")
    else:
        st.sidebar.info("🟠 SANDBOX")
else:
    st.sidebar.warning("⚪ OFFLINE")

if st.sidebar.button("Reset Session"):
    reset_state()
    st.rerun()

# Main UI Logic
col1, _ = st.columns([3, 1])

with col1:
    uploaded_file = st.file_uploader("", type=['csv', 'json', 'xml', 'xlsx', 'hl7', 'fhir', 'pdf', 'txt'])

if uploaded_file is not None:
    temp_path = os.path.join(os.getcwd(), uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.markdown(f"<div style='background-color: #161b22; padding: 10px; border-radius: 8px; border-left: 4px solid #10a37f;'>📄 <b>Detected:</b> {uploaded_file.name}</div>", unsafe_allow_html=True)
    
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
            
            if st.button("Launch Analytics", use_container_width=True):
                st.session_state.mapping_confirmed = True
                st.session_state.data_source = "REAL"
                with st.spinner("Finalizing..."):
                    st.session_state.processed_df = ingress.run_ingress(temp_path)
                    st.session_state.detected_format = ingress.detect_format(temp_path)
                st.rerun()
    
else:
    st.markdown("<div style='text-align: center; padding: 50px;'>", unsafe_allow_html=True)
    st.info("No data? Start with the 2026 Sandbox.")
    if st.button("Load Sandbox Mode"):
        st.session_state.data_source = "DUMMY"
        with st.spinner("Building test environment..."):
            create_sample_data.main()
            st.session_state.processed_df = ingress.run_ingress("raw_data.csv")
            st.session_state.mapping_confirmed = True
            st.session_state.detected_format = ingress.detect_format("raw_data.csv")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.processed_df is not None:
    st.markdown("---")
    df = st.session_state.processed_df
    results = ingress.run_audit(df, "Session", return_results=True)
    total = results["total"]
    
    st.subheader(f"📊 Analytics Dashboard - {st.session_state.detected_format or 'N/A'}")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total", total)
    m2.metric("Success", f"{results['processed']} ({(results['processed']/total*100):.1f}%)")
    m3.metric("Purged", results['purged'], delta="-"+str(results["purged"]), delta_color="inverse")
    m4.metric("Quarantined", results['quarantined'])

    st.markdown("### 💡 Insights")
    health_data = pd.DataFrame({"Status": ["Success", "Purged", "Quarantined"], "Count": [results["processed"], results["purged"], results["quarantined"]]}).set_index("Status")
    st.bar_chart(health_data, color="#10a37f")

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
    st.dataframe(mask_pii_for_preview(df), use_container_width=True)

    if not st.session_state.revoked:
        if st.button("🔴 Purge Data (DPDP Rule 8)"):
            st.session_state.processed_df = ingress.erase_pii_for_revocation(df)
            st.session_state.revoked = True
            st.rerun()
    else:
        st.warning("⚠️ Data Hard-Purged per DPDP Act.")
