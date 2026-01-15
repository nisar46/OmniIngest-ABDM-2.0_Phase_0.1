# 🛡️ Compliance & Standards Alignment

**OmniIngest ABDM 2.0** is built with a "Compliance-First" architecture. It is not just a data mover; it is a regulatory enforcement engine.

## 1. ABDM Alignment (Ayushman Bharat Digital Mission)
This project adheres to the **National Resource Centre for EHR Standards (NRCeS)** guidelines for Health Information Providers (HIPs).

### FHIR R5 Implementation
We utilize the latest **HL7 FHIR Release 5 (R5)** standard for all internal data representations. 
- **Key Deviation Handling**: Unlike R4, R5 has stricter nesting requirements for human names.
- **Implementation**: The `get_fhir_bundle` function in `app.py` enforces this deep nesting:
  ```json
  "name": [
      {
          "text": "Patient Name Here"
      }
  ]
  ```
- **Validation**: Every resource passes through a `verify_fhir_structure` Auditor Check before inclusion in a bundle.

## 2. DPDP Act 2023 (Digital Personal Data Protection)
We implement a hard-coded adherence to **Rule 8 (Right to Erasure)**.

### Rule 8.3: The "Kill Switch"
The **Data Principal (Patient)** has the right to revoke consent and demand erasure of their personal data.
- **Mechanism**: The application features a "Session Revoked" state that triggers a cryptographic shredding simulation.
- **Process**:
    1. **Detach**: Identity keys are unlinked.
    2. **Overwrite**: PII memory blocks are overwritten with a zero-fill pattern.
    3. **Audit**: The *action* is logged, but the *data* is gone.
- **Visual Verification**: The Dashboard displays a "DATA PURGED" state in red/bold for all PII fields (Name, ABHA ID) post-revocation, proving to the operator that the data is no longer accessible in memory.

## 3. Security Architecture
- **Sandbox Isolation**: The environment provides a "Sandbox Mode" (`X-CM-ID: sbx`) that is physically isolated from the "Real Data" pipeline.
- **Local Processing**: All ingress processing happens locally within the instance; no raw patient data is sent to external cloud APIs during the parsing phase.
