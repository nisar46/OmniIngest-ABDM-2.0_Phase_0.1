# 🚀 Technical Fact Sheet: OmniIngest ABDM 2.0 (Phase 0.1)

Below are the technical "proofs of tech" for recruiters and compliance leads. These snippets demonstrate the robust architecture underlying the OmniIngest dashboard.

### 🩺 1. FHIR R5 Patient Resource (NRCeS Compliant)
A nested JSON structure ensuring interoperability with India's ABDM Gateway.
```json
{
  "resourceType": "Patient",
  "identifier": [
    {
      "system": "https://healthidsbx.abdm.gov.in",
      "value": "91-1234-5678-9012"
    }
  ],
  "name": [{ "text": "Rahul Verma" }]
}
```

### ✂️ 2. Rule 8.3: PII Shredder (Python/Polars)
High-performance logic to overwrite PII the moment consent is revoked.
```python
def shred_pii(df):
    # Rule 8.3: Automatic deep-purge based on Consent_Status
    exprs = [pl.when(pl.col("Consent_Status") == "REVOKED")
             .then(pl.lit("[DATA PURGED]")).otherwise(pl.col(c)).alias(c)
             for c in ["Patient_Name", "ABHA_ID"]]
    return df.with_columns(exprs)
```

### 📜 3. Audit Lineage (Compliance Traceability)
Verifiable audit trails with 1-year statutory retention logic.
```csv
Request_ID,Timestamp,Action,Statutory_Retention_Until
550e8400-e29b-41d4-a716-446655440000,2026-01-14T21:16:12,CONSENT_REVOKED_OVERRIDE,2027-01-14
392a8b11-d14c-42e1-a532-112233445566,2026-01-14T21:18:05,COMPLIANCE_PURGE_SUCCESS,2027-01-14
```

---
**Standard**: ABDM 2.0 / DPDP Rule 8.3  
**Architecture**: Techno-Legal Middleware  
**Author**: Nisar Ahmed
