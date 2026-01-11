import streamlit as st
import pandas as pd
import polars as pl
import os
import ingress
import create_sample_data
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="OmniIngest ABDM 2.0", page_icon="🏥", layout="wide")

# Custom CSS for premium feel
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    .status-card {
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
        text-align: center;
        font-weight: bold;
    }
    .real-data {
        background-color: #28a745;
    }
    .dummy-data {
        background-color: #6c757d;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 OmniIngest ABDM 2.0 - Dashboard")
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

def reset_state():
    st.session_state.data_source = None
    st.session_state.processed_df = None
    st.session_state.mapping_confirmed = False
    st.session_state.revoked = False
    st.session_state.detected_format = None

def get_fhir_bundle(df):
    """Generates a FHIR R5 Bundle collection from the processed dataframe."""
    import json
    bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "timestamp": datetime.now().isoformat(),
        "entry": []
    }
    
    # Only export PROCESSED records
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
    """Masks PII in the preview for ALL records to maintain maximum privacy (Phase 0.1 Standard)."""
    df_pd = df.to_pandas().copy()
    
    def mask_val(val):
        if pd.isna(val) or str(val).strip() == "" or str(val) == "None":
            return "[MISSING]"
        val_str = str(val)
        if len(val_str) < 4:
            return "****"
        # Masking Pattern: Show first 2 and last 2 characters
        return val_str[:2] + "****" + val_str[-2:] if len(val_str) > 4 else val_str[:1] + "****"
        
    def mask_payload(val):
        if pd.isna(val) or str(val).strip() == "":
            return "[EMPTY_PAYLOAD]"
        return "{'clinical_data': 'PROTECTED_BY_DPDP_RULE_8'}"

    # Apply masking to ALL rows for safety
    df_pd['Patient_Name'] = df_pd['Patient_Name'].apply(mask_val)
    df_pd['ABHA_ID'] = df_pd['ABHA_ID'].apply(mask_val)
    df_pd['Clinical_Payload'] = df_pd['Clinical_Payload'].apply(mask_payload)
    
    return df_pd

# Sidebar Info
st.sidebar.header("System Status")
if st.session_state.data_source:
    if st.session_state.data_source == "REAL":
        st.sidebar.success("🟢 REAL USER DATA")
    else:
        st.sidebar.info("🟠 DUMMY DATA (SANDBOX)")
else:
    st.sidebar.warning("⚪ NO DATA LOADED")

if st.sidebar.button("Reset Session"):
    reset_state()
    st.rerun()

# Main UI Logic
col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader("Upload Patient Data (CSV, JSON, XLSX, etc.)", type=['csv', 'json', 'xml', 'xlsx', 'hl7', 'fhir', 'pdf', 'txt'])

if uploaded_file is not None:
    # Save uploaded file temporarily to process with existing logic
    temp_path = os.path.join(os.getcwd(), uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success(f"User file detected: `{uploaded_file.name}`")
    
    # Vocal Validation Layer
    if not st.session_state.mapping_confirmed:
        st.subheader("🔍 Vocal Validation & Mapping")
        
        mapping, satisfied_fields = ingress.get_mapping_summary(temp_path)
        critical_fields = ["Patient_Name", "ABHA_ID", "Notice_ID"]
        missing_fields = [f for f in critical_fields if f not in satisfied_fields]
        
        if missing_fields:
            st.error(f"🚨 YELL: CRITICAL ABDM 2.0 FIELDS MISSING! {', '.join(missing_fields)}")
            st.warning("The file is non-compliant. Would you like to Fix & Re-upload or Auto-fill missing fields with Dummy Data?")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("❌ Fix & Re-upload"):
                    st.info("Please fix your file and upload again.")
                    st.stop()
            with c2:
                if st.button("🪄 Auto-fill with Dummy Data"):
                    st.session_state.mapping_confirmed = True
                    st.session_state.data_source = "REAL (AUTO-FILLED)"
                    with st.spinner("Auto-filling and analyzing for ABDM 2.0 compliance..."):
                        st.session_state.processed_df = ingress.run_ingress(temp_path, autofill=True)
                    st.rerun()
        
        elif mapping:
            st.success("All critical ABDM 2.0 fields detected via synonyms!")
            st.write("The system identified the following clinical mappings:")
            mapping_data = [{"Source Column": k, "ABDM Field": v} for k, v in mapping.items()]
            st.table(mapping_data)
            
            if st.button("Confirm Mapping & Continue"):
                st.session_state.mapping_confirmed = True
                st.session_state.data_source = "REAL"
                with st.spinner("Analyzing for ABDM 2.0 compliance..."):
                    st.session_state.processed_df = ingress.run_ingress(temp_path)
                    st.session_state.detected_format = ingress.detect_format(temp_path)
                st.rerun()
        else:
            st.error("Could not detect any valid ABDM columns. Please check your file format.")
    
else:
    # No file uploaded
    st.info("No data source found. Would you like to use the 2026 ABDM Dummy Data to test the flow?")
    if st.button("Use Dummy Data"):
        st.session_state.data_source = "DUMMY"
        # Force fresh creation of dummy data with updated compliance scenarios
        with st.spinner("Regenerating 2026 ABDM Dummy Data..."):
            create_sample_data.main()
            st.session_state.processed_df = ingress.run_ingress("raw_data.csv")
            st.session_state.mapping_confirmed = True
            st.session_state.detected_format = ingress.detect_format("raw_data.csv")
        st.rerun()

# Display Results if data is processed
if st.session_state.processed_df is not None:
    st.markdown("---")
    
    # Status Banner
    if st.session_state.data_source == "REAL":
        st.markdown('<div class="status-card real-data">REAL USER DATA MODE</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-card dummy-data">DUMMY DATA (SANDBOX MODE)</div>', unsafe_allow_html=True)

    # Summary Dashboard & Metrics
    df = st.session_state.processed_df
    results = ingress.run_audit(df, "Streamlit Processed", return_results=True)
    
    total = results["total"]
    def get_percent(val):
        return f"({(val/total*100):.1f}%)" if total > 0 else "(0%)"

    st.subheader(f"📊 Dataset Analytics - {st.session_state.detected_format or 'Unknown Format'}")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Records", total)
    m2.metric("Processed (Success)", f"{results['processed']} {get_percent(results['processed'])}", delta_color="normal")
    m3.metric("Purged (Rule 3/7)", f"{results['purged']} {get_percent(results['purged'])}", delta="-"+str(results["purged"]), delta_color="inverse")
    m4.metric("Quarantined (M1)", f"{results['quarantined']} {get_percent(results['quarantined'])}", delta_color="off")

    # Compliance Health Overview Chart
    st.subheader("💡 Compliance Health Overview")
    health_data = pd.DataFrame({
        "Status": ["Processed", "Purged", "Quarantined"],
        "Count": [results["processed"], results["purged"], results["quarantined"]]
    }).set_index("Status")
    st.bar_chart(health_data, color="#28a745" if results["purged"] == 0 else "#ffc107")

    # Visual Breakdown of Failures
    b1, b2 = st.columns(2)
    with b1:
        st.subheader("Purge Reasons (DPDP Rule 8)")
        if results["purge_reasons"]:
            st.bar_chart(pd.Series(results["purge_reasons"]), color="#dc3545")
        else:
            st.write("No purged records.")
    
    with b2:
        st.subheader("Quarantine Reasons (ABDM M1)")
        if results["quarantine_reasons"]:
            st.bar_chart(pd.Series(results["quarantine_reasons"]), color="#fd7e14")
        else:
            st.write("No quarantined records.")
            
    # New: General Data Quality Audit (Missing Details)
    st.markdown("---")
    st.subheader("🔎 General Data Quality Audit")
    q_col1, q_col2 = st.columns(2)
    
    # Identify missing details in the overall dataset
    missing_raw = {
        "Missing ABHA ID": df.filter(pl.col("ABHA_ID").is_null() | (pl.col("ABHA_ID") == "")).height,
        "Malformed ABHA IDs": df.filter((pl.col("Ingest_Status") != "PROCESSED") & (pl.col("Status_Reason") == "MALFORMED_ID")).height,
        "Missing Patient Name": df.filter(pl.col("Patient_Name").is_null() | (pl.col("Patient_Name") == "") | (pl.col("Patient_Name") == "REDACTED")).height,
        "Missing Clinical Info": df.filter(pl.col("Clinical_Payload").is_null() | (pl.col("Clinical_Payload") == "")).height,
    }
    
    with q_col1:
        st.write("Counts of missing/invalid fields detected:")
        st.table(pd.DataFrame(list(missing_raw.items()), columns=["Detail", "Count"]))
    
    with q_col2:
        if any(missing_raw.values()):
            st.warning("⚠️ Some records are incomplete or redacted. Quarantined records require these fields for ABDM 2.0 success.")
        else:
            st.success("✅ Excellent data quality! All critical fields are populated.")

    # Export Section
    st.markdown("---")
    st.subheader("📥 Clinical Data Export Hub")
    e1, e2, e3, e4 = st.columns(4)
    
    with e1:
        csv_full = df.to_pandas().to_csv(index=False).encode('utf-8')
        st.download_button("📜 Download Master CSV", data=csv_full, file_name="abdm_standardized_master.csv", mime="text/csv")
    
    with e2:
        processed_only = df.filter(pl.col("Ingest_Status") == "PROCESSED").to_pandas().to_csv(index=False).encode('utf-8')
        st.download_button("✅ Download Compliant CSV", data=processed_only, file_name="abdm_only_compliant.csv", mime="text/csv")
        
    with e3:
        purged_only = df.filter(pl.col("Ingest_Status") == "PURGED").to_pandas().to_csv(index=False).encode('utf-8')
        st.download_button("📂 Download Audit Logs", data=purged_only, file_name="abdm_audit_logs_purged.csv", mime="text/csv")
    
    with e4:
        fhir_bundle = get_fhir_bundle(df)
        st.download_button("🔥 Download FHIR R5 Bundle", data=fhir_bundle, file_name="abdm_bundle.json", mime="application/json")

    # Data Preview
    st.subheader("📄 Universal Privacy-Safe Preview")
    st.info("�️ Privacy By Default: All PII (Name, ABHA, Clinical Data) is automatically masked in this preview for non-repudiation. Full data is only accessible via secure Export buttons.")
    masked_preview = mask_pii_for_preview(df)
    st.dataframe(masked_preview, use_container_width=True)

    # Audit Log
    st.markdown("---")
    
    # Consent Kill-Switch (DPDP Rule 8)
    if not st.session_state.revoked:
        if st.button("🔴 Revoke Consent & Erase PII"):
            with st.spinner("Executing DPDP Rule 8 Hard-Purge..."):
                st.session_state.processed_df = ingress.erase_pii_for_revocation(st.session_state.processed_df)
                st.session_state.revoked = True
                st.toast("PII Erased successfully. System Audit Logs retained for 365 days per DPDP Rule 8.3 compliance.", icon="🛡️")
            st.rerun()
    else:
        st.warning("⚠️ This data has been purged under DPDP Rule 8. Minimal audit logs preserved.")

    st.caption(f"Audit Log Entry: Compliance Verification Complete at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
