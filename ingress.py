import polars as pl
from datetime import datetime, timedelta
import os
from compliance_engine import ComplianceEngine

def detect_format(file_path: str) -> str:
    """
    Detects the file format based on the extension.
    """
    import os
    ext = os.path.splitext(file_path)[1].lower()
    format_map = {
        '.csv': 'CSV (Polars Lazy API)',
        '.json': 'JSON (Universal Adapter)',
        '.xml': 'XML (Universal Adapter)',
        '.xlsx': 'Excel (Universal Adapter)',
        '.xls': 'Excel (Universal Adapter)',
        '.dcm': 'DICOM (Medical Imaging)',
        '.dicom': 'DICOM (Medical Imaging)',
        '.hl7': 'HL7 V2 (Clinical)',
        '.fhir': 'FHIR R5 (Standard)',
        '.pdf': 'PDF (Clinical Report)',
        '.txt': 'Text (Clinical Report)'
    }
    return format_map.get(ext, f"Unknown ({ext.upper() if ext else 'No Extension'})")


# Mapping 'Messy' columns to Canonical Schema (Expanded for ABDM 2.0 Synonyms)
COLUMN_MAPPING = {
    # ABHA_ID Synonyms
    "ID_ABHA": "ABHA_ID",
    "abha_id": "ABHA_ID",
    "Health_ID": "ABHA_ID",
    "ABHA": "ABHA_ID",
    "ABHA_No": "ABHA_ID",
    
    # Patient_Name Synonyms
    "Patient_Name": "Patient_Name",
    "patient_name": "Patient_Name",
    "Full_Name": "Patient_Name",
    "Patient": "Patient_Name",
    "Name": "Patient_Name",
    
    # Notice_ID Synonyms
    "Notice_ID": "Notice_ID",
    "notice_id": "Notice_ID",
    "Doc_ID": "Notice_ID",
    "Reference_No": "Notice_ID",
    "notice_number": "Notice_ID",
    
    # Other Fields
    "Clinical_Details": "Clinical_Payload",
    "clinical_payload": "Clinical_Payload",
    "Consent_Flag": "Consent_Status",
    "consent_status": "Consent_Status",
    "Notice_Issue_Date": "Notice_Date",
    "notice_date": "Notice_Date",
    "Purpose_of_Data": "Data_Purpose",
    "data_purpose": "Data_Purpose"
}

def get_mapping_summary(file_path: str):
    """
    Peeks at the file headers and returns the mapping summary.
    """
    import polars as pl
    import os
    
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext == '.csv':
            lf = pl.scan_csv(file_path)
            existing_cols = lf.collect_schema().names()
        elif ext == '.json':
            df_tmp = pl.read_json(file_path)
            existing_cols = df_tmp.columns
        else:
            # For other formats, we might need a more complex peek, 
            # but for now let's use the universal adapter if possible
            from universal_adapter import parse_data_file
            df_pd = parse_data_file(file_path)
            existing_cols = df_pd.columns.tolist()
            
        target_fields = ["ABHA_ID", "Patient_Name", "Notice_ID", "Notice_Date", "Consent_Status", "Clinical_Payload", "Data_Purpose"]
        
        # Build a case-insensitive lookup
        cols_lower = {c.lower(): c for c in existing_cols}
        actual_mapping = {}
        for k, v in COLUMN_MAPPING.items():
            if k.lower() in cols_lower:
                actual_mapping[cols_lower[k.lower()]] = v
        
        # Identify which canonical fields are satisfied (either via mapping or already present)
        satisfied_canonical = set(actual_mapping.values())
        canonical_lower = [f.lower() for f in target_fields]
        for col in existing_cols:
            if col.lower() in canonical_lower:
                # Find the exact target name
                matching_target = target_fields[canonical_lower.index(col.lower())]
                satisfied_canonical.add(matching_target)
                
        return actual_mapping, list(satisfied_canonical)
    except Exception as e:
        print(f"Error getting mapping summary: {e}")
        return {}, []


def run_ingress(file_path: str, autofill: bool = False):
    """
    Phase 0.1: The Smart Ingress
    Uses Polars to process input data and apply compliance logic.
    Handles multiple formats by detecting extension.
    """
    import polars as pl
    import os
    import random
    from datetime import datetime
    
    ext = os.path.splitext(file_path)[1].lower()
    
    # 1. Loading Phase
    if ext == '.csv':
        lf = pl.scan_csv(file_path)
    elif ext == '.json':
        df_tmp = pl.read_json(file_path)
        lf = df_tmp.lazy()
    else:
        try:
            from universal_adapter import parse_data_file
            df_pd = parse_data_file(file_path)
            lf = pl.from_pandas(df_pd).lazy()
        except Exception as e:
            print(f"Warning: Universal Adapter fallback failed: {e}")
            if ext == '.xlsx' or ext == '.xls':
                df_tmp = pl.read_excel(file_path)
                lf = df_tmp.lazy()
            else:
                raise ValueError(f"Unsupported format for ingress: {ext}")

    existing_cols = lf.collect_schema().names()
    
    # Case-insensitive mapping logic
    cols_lower = {c.lower(): c for c in existing_cols}
    actual_mapping = {}
    for k, v in COLUMN_MAPPING.items():
        if k.lower() in cols_lower:
            actual_mapping[cols_lower[k.lower()]] = v
    
    # Apply Mapping and Ensure Canonical Columns
    q = lf.rename(actual_mapping)
    
    target_canonical_fields = ["ABHA_ID", "Patient_Name", "Clinical_Payload", "Consent_Status", "Notice_ID", "Notice_Date", "Data_Purpose"]
    current_cols = q.collect_schema().names()
    missing_canonical = [f for f in target_canonical_fields if f not in current_cols]
    
    if missing_canonical:
        if autofill:
            # Auto-fill missing critical fields with dummy data for testing
            fill_cols = []
            for f in missing_canonical:
                if f == "Notice_Date":
                    fill_cols.append(pl.lit("2026-01-01").alias(f))
                elif f == "Notice_ID":
                    fill_cols.append(pl.lit("N-2026-AUTO-v1.0").alias(f))
                elif f == "Consent_Status":
                    fill_cols.append(pl.lit("GRANTED").alias(f))
                else:
                    fill_cols.append(pl.lit(f"AUTO_{f}_DUMMY").alias(f))
            q = q.with_columns(fill_cols)
        else:
            q = q.with_columns([pl.lit(None).alias(f) for f in missing_canonical])


    # Define Threshold for DPDP Rule 3 (365 days)
    threshold_date = datetime.now() - timedelta(days=365)
    
    # Transform
    engine = ComplianceEngine()
    
    q = (
        q
        # Cast dates (handle potential string formats)
        .with_columns(
            pl.col("Notice_Date").cast(pl.String).str.to_date("%Y-%m-%d", strict=False)
        )
        # Apply Logic: Tagging Records using modern compliance engine tags
        .with_columns([
            pl.when(pl.col("ABHA_ID").is_null() | (pl.col("ABHA_ID") == ""))
            .then(pl.lit("QUARANTINED"))
            # Strict ABHA Pattern Validation (Clinical Grade)
            .when(pl.col("ABHA_ID").str.contains(r"^[0-9]{2}-[0-9]{4}-[0-9]{4}-[0-9]{4}$").not_())
            .then(pl.lit("QUARANTINED"))
            .when(pl.col("Consent_Status") == "REVOKED")
            .then(pl.lit("PURGED"))
            .when(pl.col("Notice_Date") < engine.threshold_date)
            .then(pl.lit("PURGED"))
            # Compliance Force: Enforce 2026 Notice_ID
            .when(pl.col("Notice_ID").str.starts_with("N-2025"))
            .then(pl.lit("PURGED"))
            .otherwise(pl.lit("PROCESSED"))
            .alias("Ingest_Status"),
            
            pl.when(pl.col("ABHA_ID").is_null() | (pl.col("ABHA_ID") == ""))
            .then(pl.lit("MISSING_ABHA"))
            # Strict ABHA Pattern Reason
            .when(pl.col("ABHA_ID").str.contains(r"^[0-9]{2}-[0-9]{4}-[0-9]{4}-[0-9]{4}$").not_())
            .then(pl.lit("MALFORMED_ID"))
            .when(pl.col("Consent_Status") == "REVOKED")
            .then(pl.lit("CONSENT_REVOKED"))
            .when(pl.col("Notice_Date") < engine.threshold_date)
            .then(pl.lit("NOTICE_EXPIRED"))
            # Compliance Force: Enforce 2026 Notice_ID reason
            .when(pl.col("Notice_ID").str.starts_with("N-2025"))
            .then(pl.lit("OUTDATED_NOTICE_ERROR"))
            .otherwise(pl.lit("N/A"))
            .alias("Status_Reason")
        ])
    )
    
    # Execute Lazy Frame
    df = q.collect()
    return df

def run_audit(df: pl.DataFrame, file_format: str, return_results: bool = False):
    """
    Generates a clean, formatted Execution Dashboard for DPDP Rule 7 audit requirements.
    """
    total = len(df)
    processed = df.filter(pl.col("Ingest_Status") == "PROCESSED")
    purged = df.filter(pl.col("Ingest_Status") == "PURGED")
    quarantined = df.filter(pl.col("Ingest_Status") == "QUARANTINED")
    
    results = {
        "format": file_format,
        "total": total,
        "processed": len(processed),
        "purged": len(purged),
        "quarantined": len(quarantined),
        "purge_reasons": {},
        "quarantine_reasons": {}
    }

    print("\n" + "="*60)
    print(f"       OMNINGEST ABDM 2.0 - EXECUTION DASHBOARD")
    print("="*60)
    print(f"FILE FORMAT INGESTED  : {file_format}")
    print(f"TOTAL PATIENTS DATA   : {total}")
    print("-"*60)
    print(f"[OK] PROCESSED SUCCESS   : {len(processed)}")
    print(f"[FAIL] PURGED (Rule 3/7) : {len(purged)}")
    print(f"[WARN] QUARANTINED (M1)  : {len(quarantined)}")
    print("="*60)
    
    if len(purged) > 0:
        print("\nPURGE BREAKDOWN (Reasons):")
        reasons = purged.group_by("Status_Reason").count()
        for row in reasons.iter_rows():
            print(f" - {row[0]}: {row[1]} patient(s)")
            results["purge_reasons"][row[0]] = row[1]
            
    if len(quarantined) > 0:
        print("\nQUARANTINE BREAKDOWN (Reasons):")
        reasons = quarantined.group_by("Status_Reason").count()
        for row in reasons.iter_rows():
            print(f" - {row[0]}: {row[1]} patient(s)")
            results["quarantine_reasons"][row[0]] = row[1]
    
    print("-"*60)
    print("Audit Log Entry: Compliance Verification Complete.")
    print("="*60 + "\n")

    if return_results:
        return results

def erase_pii_for_revocation(df: pl.DataFrame) -> pl.DataFrame:
    """
    DPDP Rule 8 Kill-Switch: Erases all PII but retains system/audit logs.
    Rule 8.3: Retains audit lineage for compliance verification.
    """
    return (
        df.with_columns([
            # Erase PII
            pl.lit("ERASED_RULE_8").alias("Patient_Name"),
            pl.lit("ERASED_RULE_8").alias("ABHA_ID"),
            pl.lit("ERASED_RULE_8_PII_PROTECT").alias("Clinical_Payload"),
            
            # Update Status
            pl.lit("REVOKED").alias("Consent_Status"),
            pl.lit("PURGED").alias("Ingest_Status"),
            pl.lit("RULE_8_REVOCATION").alias("Status_Reason"),
            
            # FHIR R5 Compliance Status
            pl.lit("Deleted").alias("FHIR_Status")
        ])
    )

if __name__ == "__main__":
    test_file = "raw_data.csv"
    if os.path.exists(test_file):
        # Process the data
        processed_data = run_ingress(test_file)
        
        # Run the audit dashboard
        run_audit(processed_data, detect_format(test_file))
        
        # Save output for reference in next phases
        processed_data.write_csv("ingress_output_audit.csv")
    else:
        print(f"Error: {test_file} not found. Run the test data generator first.")
