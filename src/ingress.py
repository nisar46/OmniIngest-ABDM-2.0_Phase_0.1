import polars as pl
import os
import re
from datetime import datetime, timedelta
from .compliance_engine import ComplianceEngine

# Configuration: Mapping synonyms for messy columns to Canonical ABDM schema
COLUMN_MAPPING = {
    # ABHA_ID Synonyms
    "ID_ABHA": "ABHA_ID",
    "abha_id": "ABHA_ID",
    "Health_ID": "ABHA_ID",
    "ABHA": "ABHA_ID",
    "ABHA_No": "ABHA_ID",
    "ABHA Number": "ABHA_ID", # Added per request
    
    # Patient_Name Synonyms
    "Patient_Name": "Patient_Name",
    "patient_name": "Patient_Name",
    "Full_Name": "Patient_Name",
    "Patient": "Patient_Name",
    "Pt_Name": "Patient_Name",
    "PT_NAME": "Patient_Name",
    
    # Notice_ID Synonyms
    "Consent_ID": "Notice_ID",
    "Notice_ID": "Notice_ID",
    "Doc_ID": "Notice_ID",
    "Reference_No": "Notice_ID",
    
    # Consent_Status Synonyms
    "Consent": "Consent_Status",
    "Consent_Status": "Consent_Status",
    "Status": "Consent_Status",
    
    # Notice_Date Synonyms
    "Date": "Notice_Date",
    "Notice_Date": "Notice_Date",
    "Consent_Date": "Notice_Date",
    
    # Clinical_Payload Synonyms
    "Data": "Clinical_Payload",
    "Clinical_Payload": "Clinical_Payload",
    "Report": "Clinical_Payload",
    "Diagnosis": "Clinical_Payload",
    "Summary": "Clinical_Payload"
}

def detect_format(file_path: str) -> str:
    """Detects the file format based on the extension."""
    ext = os.path.splitext(file_path)[1].lower()
    format_map = {
        '.csv': 'CSV (Polars)',
        '.json': 'JSON (Universal)',
        '.xml': 'XML (Universal)',
        '.xlsx': 'Excel (Universal)',
        '.xls': 'Excel (Universal)',
        '.dcm': 'DICOM (Imaging)',
        '.hl7': 'HL7 V2 (Clinical)',
        '.fhir': 'FHIR R5 (Standard)',
        '.pdf': 'PDF (Clinical Report)',
        '.txt': 'Text (Clinical Report)'
    }
    return format_map.get(ext, f"Unknown ({ext.upper()})")

def get_mapping_summary(file_path: str):
    """Peeks at the file headers and returns mapping summary + sample data."""
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == '.csv':
            df_tmp = pl.read_csv(file_path, n_rows=1)
            existing_cols = df_tmp.columns
        elif ext == '.json':
            df_tmp = pl.read_json(file_path)
            existing_cols = df_tmp.columns
        else:
            from .universal_adapter import parse_data_file
            df_pd = parse_data_file(file_path)
            existing_cols = df_pd.columns.tolist()
            df_tmp = pl.from_pandas(df_pd.head(1))
            
        target_fields = ["ABHA_ID", "Patient_Name", "Notice_ID", "Notice_Date", "Consent_Status", "Clinical_Payload", "Data_Purpose"]
        cols_lower = {c.lower(): c for c in existing_cols}
        actual_mapping = {}
        for k, v in COLUMN_MAPPING.items():
            if k.lower() in cols_lower:
                actual_mapping[cols_lower[k.lower()]] = v
        
        satisfied_canonical = set(actual_mapping.values())
        canonical_lower = [f.lower() for f in target_fields]
        for col in existing_cols:
            if col.lower() in canonical_lower:
                satisfied_canonical.add(target_fields[canonical_lower.index(col.lower())])
        
        sample_data = {}
        if not df_tmp.is_empty():
            row = df_tmp.to_dicts()[0]
            for col in existing_cols:
                sample_data[col] = str(row.get(col, ""))[:100]
                
        return actual_mapping, list(satisfied_canonical), sample_data
    except Exception as e:
        print(f"Error peeking file: {e}")
        return {}, [], {}

def run_ingress(file_path: str, autofill: bool = False):
    """
    Phase 0.1 Ingress with Zero-Failure Logic & Universal Fallback.
    
    ARCHITECT'S NOTE (2026):
    In real-world hospital ops, data hygiene is low. We cannot reject files just because headers are messy.
    This module implements a 'Universal Adapter' pattern:
      1. Try structured read (Polars/JSON).
      2. If headers mismatch, fuzzy-match against Canonical ABDM Dictionary.
      3. If critical fields missing, use Regex Heuristics (Zero-Failure) to extract from raw text.
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    # 1. Loading
    if ext == '.csv':
        lf = pl.scan_csv(file_path)
    elif ext == '.json':
        lf = pl.read_json(file_path).lazy()
    else:
        try:
            from .universal_adapter import parse_data_file
            df_pd = parse_data_file(file_path)
            lf = pl.from_pandas(df_pd).lazy()
        except:
            if ext in ['.xlsx', '.xls']:
                lf = pl.read_excel(file_path).lazy()
            else:
                raise ValueError(f"Ingress failed for format: {ext}")

    existing_cols = lf.collect_schema().names()
    cols_lower = {c.lower(): c for c in existing_cols}
    actual_mapping = {}
    for k, v in COLUMN_MAPPING.items():
        if k.lower() in cols_lower:
            actual_mapping[cols_lower[k.lower()]] = v
    
    q = lf.rename(actual_mapping)
    target_canonical_fields = ["ABHA_ID", "Patient_Name", "Clinical_Payload", "Consent_Status", "Notice_ID", "Notice_Date", "Data_Purpose"]
    current_cols = q.collect_schema().names()
    
    missing_canonical = [f for f in target_canonical_fields if f not in current_cols]
    if missing_canonical:
        if autofill:
            fills = []
            for f in missing_canonical:
                if f == "Notice_Date": fills.append(pl.lit("2026-01-01").alias(f))
                elif f == "Notice_ID": fills.append(pl.lit("N-2026-AUTO").alias(f))
                elif f == "Consent_Status": fills.append(pl.lit("GRANTED").alias(f))
                else: fills.append(pl.lit(f"AUTO_{f}").alias(f))
            q = q.with_columns(fills)
        else:
            q = q.with_columns([pl.lit(None).alias(f) for f in missing_canonical])

    # 2. Universal Field Recovery (Zero-Failure)
    df = q.collect()
    abha_pat = r'\b(?:\d{2}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}|[a-zA-Z0-9.]+@sbx)\b'
    name_pat = r'(?:Patient Name|Pt Name|Patient|Name|Name of Pt)[:\s_-]*([A-Z][a-z]+(?:[\s_-][A-Z][a-z]+)*)'
    
    def recover(row):
        text = " ".join([str(v) for v in row.values() if v])
        if not row.get('ABHA_ID'):
            m = re.search(abha_pat, text)
            if m: row['ABHA_ID'] = m.group(0).replace(" ", "-")
        if not row.get('Patient_Name') or row.get('Patient_Name') == 'Unknown/Redacted' or 'AUTO_Patient_Name' in str(row.get('Patient_Name')):
            m = re.search(name_pat, text)
            if m: row['Patient_Name'] = m.group(1)
        return row

    # Define Schema for recovered records to prevent Polars type errors
    schema = {f: pl.Utf8 for f in target_canonical_fields}
    recovered_records = [recover(r) for r in df.to_dicts()]
    df = pl.from_dicts(recovered_records, schema=schema)

    # 3. Compliance Logic
    engine = ComplianceEngine()
    # Ensure Notice_Date is a date type
    df = df.with_columns([
        pl.col("Notice_Date").cast(pl.Utf8).str.to_date("%Y-%m-%d", strict=False).fill_null(datetime.now())
    ])
    
    # Audit statuses
    df = df.with_columns([
        pl.when(pl.col("ABHA_ID").is_null() | (pl.col("ABHA_ID") == "") | (pl.col("ABHA_ID").str.contains(r"^([0-9]{2}-[0-9]{4}-[0-9]{4}-[0-9]{4}|[a-zA-Z0-9.]+@sbx)$").not_()))
        .then(pl.lit("QUARANTINED"))
        .when(pl.col("Consent_Status") == "REVOKED")
        .then(pl.lit("PURGED"))
        .when(pl.col("Notice_Date") < engine.threshold_date)
        .then(pl.lit("PURGED"))
        .when(pl.col("Notice_ID").cast(pl.Utf8).str.starts_with("N-2025"))
        .then(pl.lit("PURGED"))
        .otherwise(pl.lit("PROCESSED"))
        .alias("Ingest_Status"),
        
        pl.when(pl.col("ABHA_ID").is_null() | (pl.col("ABHA_ID") == ""))
        .then(pl.lit("MISSING_ABHA"))
        .when(pl.col("ABHA_ID").str.contains(r"^([0-9]{2}-[0-9]{4}-[0-9]{4}-[0-9]{4}|[a-zA-Z0-9.]+@sbx)$").not_())
        .then(pl.lit("MALFORMED_ID"))
        .when(pl.col("Consent_Status") == "REVOKED")
        .then(pl.lit("CONSENT_REVOKED"))
        .when(pl.col("Notice_Date") < engine.threshold_date)
        .then(pl.lit("NOTICE_EXPIRED"))
        .otherwise(pl.lit("N/A"))
        .alias("Status_Reason")
    ])
    return df

def run_audit(df, label, return_results=False):
    """Generates execution dashboard stats."""
    res = {
        "format": label, "total": len(df),
        "processed": len(df.filter(pl.col("Ingest_Status") == "PROCESSED")),
        "purged": len(df.filter(pl.col("Ingest_Status") == "PURGED")),
        "quarantined": len(df.filter(pl.col("Ingest_Status") == "QUARANTINED")),
        "purge_reasons": df.filter(pl.col("Ingest_Status") == "PURGED").group_by("Status_Reason").count().to_dicts(),
        "quarantine_reasons": df.filter(pl.col("Ingest_Status") == "QUARANTINED").group_by("Status_Reason").count().to_dicts()
    }
    # Convert reasons to friendly dict
    res["purge_reasons"] = {r["Status_Reason"]: r["count"] for r in res["purge_reasons"]}
    res["quarantine_reasons"] = {r["Status_Reason"]: r["count"] for r in res["quarantine_reasons"]}
    
    if return_results: return res
    
    from .utils.logger import safe_log
    safe_log(f"Audit for {label}: Total={res['total']}, OK={res['processed']}, PURGED={res['purged']}, QUARANTINE={res['quarantined']}")

def erase_pii_for_revocation(df):
    """
    DPDP Rule 8 Kill-Switch.
    Replaces PII in Patient_Name and ABHA_ID with [DATA PURGED] for REVOKED records.
    Robust against missing columns.
    """
    cols_to_purge = ["Patient_Name", "ABHA_ID"]
    current_cols = df.columns
    
    exprs = []
    
    for col_name in cols_to_purge:
        if col_name in current_cols:
            exprs.append(
                pl.when(pl.col("Consent_Status") == "REVOKED")
                .then(pl.lit("[DATA PURGED]"))
                .otherwise(pl.col(col_name))
                .alias(col_name)
            )
            
    # CRITICAL: Also update status for Audit Graph
    if "Ingest_Status" in current_cols:
         exprs.append(
            pl.when(pl.col("Consent_Status") == "REVOKED")
            .then(pl.lit("PURGED"))
            .otherwise(pl.col("Ingest_Status"))
            .alias("Ingest_Status")
         )
         
    if "Status_Reason" in current_cols:
         exprs.append(
            pl.when(pl.col("Consent_Status") == "REVOKED")
            .then(pl.lit("CONSENT_REVOKED"))
            .otherwise(pl.col("Status_Reason"))
            .alias("Status_Reason")
         )
    
    if exprs:
        return df.with_columns(exprs)
    return df
