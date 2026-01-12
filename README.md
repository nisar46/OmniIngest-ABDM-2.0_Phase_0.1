# 🏥 OmniIngest ABDM 2.0: Clinical-Grade Data Ingestion & Compliance Engine

> **A "Privacy-By-Design" solution for India's Digital Health Revolution.**

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![ABDM 2.0](https://img.shields.io/badge/Standard-ABDM_2.0-green.svg)
![DPDP Act](https://img.shields.io/badge/Compliance-DPDP_Rule_8-orange.svg)
![FHIR R5](https://img.shields.io/badge/Data_Standard-FHIR_R5-red.svg)

## 🌟 Project Overview
OmniIngest ABDM 2.0 is a high-performance, interactive data ingestion layer designed to bridge the gap between messy legacy healthcare data and the strict requirements of the **Ayushman Bharat Digital Mission (ABDM)**. 

### 💎 The "ChatGPT Health" UX
Phase 0.1 features a premium, health-tech focused UI inspired by the minimalist and efficient design of ChatGPT.
- **Dark Mode by Default**: Optimized for clinical environments to reduce eye strain.
- **Glowing Teal Aesthetics**: A modern, high-contrast palette that feels like "The Future of Health."
- **Glassmorphism Metrics**: Clean, elevated cards for real-time compliance tracking.

---

## 🔥 Key Technical Strengths: The "Zero-Failure" Bedrock

### 🧠 Universal Field Recovery (Bedrock Engine)
The core strength of this code is its **Resilience**. Unlike traditional parsers that crash on messy headers, OmniIngest features a **Universal Extraction Fallback**:
- **Safety Net**: If a formal column mapping fails, the engine performs a "Full-Cell Scan" across every column in the record.
- **AI-Pattern Recognition**: Uses clinical-grade regex to recover `ABHA ID`s and `Patient Names` buried deep within unstructured text or raw message strings.
- **Format Agnostic**: Seamlessly processes PDF (written reports), HL7, FHIR, CSV, and XML without a single crash.

### 🕵️ Interactive Smart Mapper
- **Conversational Mapping**: When mapping is ambiguous, the app starts a dialogue with the user.
- **Live Snippets**: Displays actual data snippets (e.g., *"We found `12-34xx...`. Is this the ABHA ID?"*) to guide manual confirmation.
- **One-Click Synchronization**: Users can map unknown legacy headers to ABDM canonical fields in real-time.

### 🛡️ Clinical-Grade Privacy (DPDP Rule 8)
- **Privacy-By-Default**: Automatic PII masking across the entire dashboard to prevent accidental data leaks.
- **Rule 8 Kill-Switch**: A one-click "Hard-Purge" facility that erases PII while maintaining encrypted audit lineages as per DPDP Rule 8.3.

---

## 📽️ Tech Stack
- **Language**: Python 3.9+
- **Data Engine**: **Polars** (Sub-millisecond high-speed DataFrame processing)
- **Extraction**: **pdfplumber**, **PyPDF2**, & Custom Regex Engines
- **Interface**: **Streamlit** (Modern "ChatGPT Health" Theme)

---

## 🚀 Getting Started

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
3. Launch the Bedrock dashboard:
   ```bash
   streamlit run app.py
   ```

---

## 👨‍💻 Author: The Techno-Legal Vision

**Nisar Ahmed**
*Health Ops Veteran ➡️ AI Architect & Regulatory Engineer*

I specialize in building **"Techno-Legal" guardrails** that ensure healthcare innovation remains compliant with **India's DPDP Act** and **ABDM 2.0** standards. By combining 10 years of clinical domain expertise with **Vibe-Coding** (Agentic AI collaboration), I create high-quality, medical-grade solutions that are both legally sound and technologically superior.

---
*Developed as the core "Smart Ingress" foundation for Phase 0.1.*
