# 🏥 OmniIngest Phase 0.3: Enterprise Clinical Gateway
> **Status: Final Release | High-Performance Clinical Ingestion Core**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=for-the-badge&logo=python)
![Rust](https://img.shields.io/badge/Engine-Rust_Accelerated-black.svg?style=for-the-badge&logo=rust)
![Governance](https://img.shields.io/badge/Governance-ABDM_Native-0284C7.svg?style=for-the-badge)
![Security](https://img.shields.io/badge/DPDP-Rule_8.3_Kill_Switch-red.svg?style=for-the-badge)

## ⚡ Executive Summary
**OmniIngest Phase 0.3** is a high-performance clinical data engine designed to solve the "Dark Data" crisis in global healthcare. It transforms fragmented, unstructured clinical records (PDF, CSV, HL7) into type-safe, **ABDM-compliant** streams. 

Built with a **Rust-based processing core**, Phase 0.3 delivers enterprise-grade normalization at scale, serving as the foundational layer for the next generation of **Universal Health Intelligence** applications.

---

## 💎 Phase 0.3 Key Technical Pillars

### 1. Rust-Accelerated "Dark Data" Rescue
Under the hood, OmniIngest uses **Polars** (Rust-based) for deterministic data normalization, achieving near C-level speeds when processing massive clinical legacy files.

### 2. The Semantic Bridge
Phase 0.3 introduces the **Reasoning Layer preparation**—ensuring every piece of ingested data is mapped to **HL7 FHIR R5** standards, making clinical logic accessible and auditable.

### 3. The DPDP "Kill Switch" (Rule 8.3)
Compliance is baked into the architecture:
- **Autonomous Shredding**: Immediate cryptographic erasure of PII.
- **Rule 8.3 Logging**: Real-time governance logs ensuring that Data Principal rights (Right to Erasure) are respected natively in the code.

---

## 🏗️ Technical Architecture

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Ingestion Engine** | `Polars` (Rust-based) | High-performance normalization. |
| **Persistence** | `SQLite` | Enterprise-grade state management. |
| **Compliance** | `fhir.resources` | Strict FHIR R5 schema validation. |
| **Governance** | `DPDP Logic` | Automated PII purge & Rule 8 compliance. |

---

## 📜 Regulatory Alignment
- **ABDM 2.0**: Health Information Provider (HIP) compliance.
- **DPDP Act 2023**: Hard-coded strict adherence to Rule 8.3 (Right to Erasure).
- **Medical Law (IIT-KGP)**: Architecture verified against Bioethics and Regulatory standards.

---

## 🚀 Launch the Foundation
1. **Clone & Setup**
   ```bash
   git clone https://github.com/nisar46/OmniIngest-ABDM-2.0_Phase_0.1.git
   pip install -r requirements.txt
   ```
2. **Execute**
   ```bash
   streamlit run app.py
   ```

---

## 👨‍💻 Author & Architect
**Nisar Ahmed**  
*Senior Agentic Solutions Architect | Solutions Orchestrator*  
[LinkedIn Profile](https://linkedin.com/in/nisar-ahmed-8440763a3)

> *"Building the 'Google' for Reliable Healthcare Data."*

---
*© 2026 Nisar Ahmed. Licensed under MIT.*
