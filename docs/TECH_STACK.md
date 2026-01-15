# 🛠️ Technical Stack & Architecture

**OmniIngest ABDM 2.0** is built on a high-performance, compliance-first stack designed for the Indian Healthcare ecosystem (ABDM / DPDP 2026).

## 🧰 Core Stack

| Component | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Language** | **Python** | 3.10+ | Core logic & type safety. |
| **Ingestion** | **Polars** | 0.19+ | Rust-backed DataFrame library for sub-second ETL on large datasets. |
| **UI Framework** | **Streamlit** | 1.28+ | Rapid frontend prototyping for clinical dashboards. |
| **Testing** | **Playwright** | 1.40+ | Automated E2E testing for rule compliance verification. |
| **Compliance** | **Regex & SHA-256** | Standard | Zero-dependency cryptographic shredding & format validation. |

## 🧬 Key Compliance Implemenations

### 1. FHIR R5 Adapter (`src/ingress.py`)
We enforce HL7 FHIR Release 5 nesting standards for patient identity, ensuring interoperability with the National Health Stack.

```json
/* FHIR R5 Compliant Structure */
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

### 2. DPDP Rule 8.3 "Kill Switch" (`src/compliance_engine.py`)
The system implements "Cryptographic Shredding". When consent is revoked:
1.  **Decryption Keys** are dropped from memory (`PIIVault.shred_keys()`).
2.  **PII Fields** are overwritten with `[DATA PURGED]`.
3.  **Action is Logged**, but the data is unrecoverable.

```python
def shred_keys(self):
    """
    [RULE 8.3 COMPLIANCE]
    Destroys the decryption keys for the current session.
    """
    self._key_store = None
    log_msg = "[RULE 8.3 AUDIT] - PII Decryption Keys Permanently Shredded."
    safe_log(log_msg, level="WARNING")
    return log_msg
```

### 3. Universal Ingress (`src/universal_adapter.py`)
To handle real-world hospital data chaos, we use a "Zero-Failure" fallback strategy:
*   **Tier 1**: Structured Parsing (JSON/FHIR).
*   **Tier 2**: Fuzzy Header Matching (for messy CSV/Excel).
*   **Tier 3**: Regex Heuristics (for PDF/Text dumps).

---
**License**: MIT 2026  
**Architect**: Nisar Ahmed
