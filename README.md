# 🏥 OmniIngest ABDM 2.0: Clinical-Grade Data Ingestion & Compliance Engine

> **A "Privacy-By-Design" solution for India's Digital Health Revolution.**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![ABDM 2.0](https://img.shields.io/badge/Standard-ABDM_2.0-green.svg)](https://abdm.gov.in/)
[![DPDP Act](https://img.shields.io/badge/Compliance-DPDP_Rule_8-orange.svg)](https://www.meity.gov.in/)
[![FHIR R5](https://img.shields.io/badge/Data_Standard-FHIR_R5-red.svg)](http://hl7.org/fhir/R5/)

## 🌟 Project Overview
OmniIngest ABDM 2.0 is a high-performance, interactive data ingestion layer designed to bridge the gap between messy legacy healthcare data and the strict requirements of the **Ayushman Bharat Digital Mission (ABDM)**. 

Built with **Privacy-By-Default** principles, this project is built by a **Healthcare Domain Expert** leveraging the power of **Vibe-Coding (Agentic AI Assisted)**. It ensures that every record entering the system is compliant with the **India DPDP Act (2025/2026)** before it even touches a database.

> [!NOTE]
> This repository represents **Phase 0.1 (Smart Ingress)** of a multi-phase HealthTech roadmap.

---

## 🔥 Key Technical Features

### 🧠 Smart Ingress & Case-Insensitive Mapping
- **Polars Powered**: Utilizes the Polars Lazy API for sub-millisecond data transformation and compliance logic.
- **Header Intelligence**: Implements a case-insensitive synonym dictionary that automatically maps messy input (e.g., `pt_name`, `ID_ABHA`) to canonical ABDM fields.

### 🛡️ Clinical-Grade Privacy (Universal Masking)
- **Zero-PII Exposure**: The interactive dashboard implements universal data masking. All PII (Name, ABHA ID, Clinical Payload) is masked in the UI to prevent data leaks during administrative sessions.
- **Rule 8 Kill-Switch**: A one-click "Hard-Purge" facility that erases PII while maintaining encrypted audit lineages as per DPDP Rule 8.3 (365-day retention).

### 🚀 Advanced Compliance Engine
- **Vocal Validation**: A "Yell" layer that identifies missing critical fields (`ABHA_ID`, `Patient_Name`) and prompts for interactive recovery.
- **Format Verification**: Strict Regex-based validation for ABHA IDs (`XX-XXXX-XXXX-XXXX`) and 2026 Notice ID enforcement.
- **FHIR R5 Integration**: Native support for exporting compliant records as standardized **FHIR R5 JSON Bundles**, ready for the ABDM Gateway.

## 🛠️ Tech Stack
- **Language**: Python 3.9+
- **Data Engine**: Polars (High-speed DataFrame library)
- **Interface**: Streamlit (Modern Interactive Dashboard)
- **Standards**: FHIR R5, ABDM 2.0, DPDP Act 2025/2026

---

## 📽️ Dashboard Walkthrough & Vibe-Coding
The system provides a real-time **Compliance Health Overview**. This project demonstrates how a **Healthcare Domain Expert** can leverage **Vibe-Coding** (Agentic AI Collaboration) to rapidly build complex, compliant, and medical-grade software.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/nisar46/OmniIngest-ABDM-2.0_Phase_0.1.git
   cd OmniIngest-ABDM-2.0_Phase_0.1
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Launch the dashboard:
   ```bash
   streamlit run app.py
   ```

---

## 📜 Legal & Compliance Disclaimer
This project is built for the **NHA Sandbox Environment** and implements the latest draft rules of the Digital Personal Data Protection (DPDP) Act. It is designed to demonstrate "Privacy-By-Design" in large-scale healthcare systems.

---

## 👨‍💻 Author
**Nisar**
*A Healthcare Domain Expert turned Tech Innovator. This project (Phase 0.1) demonstrates my commitment to bridging the gap between clinical excellence and secure, ABDM-compliant digital infrastructure using modern Vibe-Coding techniques.*

---
*Developed as part of the Phase 0.1 Smart Ingress Initiative.*
