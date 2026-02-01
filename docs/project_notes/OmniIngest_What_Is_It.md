# OmniIngest: The Architect's Crash Course

**Date:** January 27, 2026  
**Project:** OmniIngest ABDM 2.0 (Phase 0.1)  
**Author:** Nisar Ahmed

---

## 1. The "One-Liner" Pitch

**What is it?**
OmniIngest is a **"Universal Adapter"** for Indian Healthcare.

**The Problem:** 
Hospitals have data in PDF, Excel, and messy CSVs. The National Network (ABDM) only accepts perfect JSON (FHIR).

**The Solution:** 
You built a bridge that takes *anything* in, cleans it, and spits out perfect, compliant JSON.

---

## 2. How it Works (The Technical Flow)

Your code (`src/ingress.py`) does three critical things that most basic scripts don't do. This is your "secret sauce":

### A. The "Zero-Failure" Ingress (Regex Rescue)
*   **The Common Way:** Basic scripts check for a column named "ABHA ID". If the hospital names it "Patient_ID_Final", the script crashes.
*   **Your Way:** You implemented a **Universal Field Recovery** function. If the columns don't match, your code physically scans the *text* of the file using Regex patterns (e.g., `r'\d{2}-\d{4}...'`) to "hunt" for the ID, no matter what column it's in.
*   **Why it matters:** This solves the "Bad Data" / "Silo" problem (the 87% statistic).

### B. The "Polars" Engine
*   **The Common Way:** Most data tools use Python `pandas`. It's reliable but slow for massive datasets.
*   **Your Way:** You used **Polars** (Rust-based). It is 10x-50x faster.
*   **Why it matters:** It proves you care about *scale* and performance, ensuring the system can handle national-level loads.

### C. The "Kill Switch" (Rule 8.3)
*   **The Common Way:** Most systems just "delete" rows or tag them as deleted.
*   **Your Way:** You explicitly search for `Consent_Status == "REVOKED"`. If found, you overwrite specific PII fields (Name, ID) with `[DATA PURGED]` *before* it leaves your system.
*   **Why it matters:** This is the specific "Cryptographic Erasure" / Compliance feature. You aren't just ignoring the data; you are actively sanitizing it to meet DPDP audit standards.

---

## 3. The Architecture Diagram (Mental Model)

Imagine a funnel:

1.  **Top of Funnel (Messy Input):** 
    `ingress.py` takes PDFs, CSVs, JSONs, scanned text.
    
2.  **Middle (The Filter):** 
    `compliance_engine.py` checks the Logic Gates.
    *   *Is the Notice expired?* → **Purge**.
    *   *Is Consent Revoked?* → **Shred**.
    
3.  **Bottom (Clean Output):** 
    The valid data is structured into a clean list, ready for the "Trust Layer" / Blockchain.

---

## Summary for Stakeholders

You are strictly aligned with the National Vision:
*   **They (The Ecosystem)** build the storage and exchange.
*   **You (OmniIngest)** build the cleaner and the on-ramp.

*This document serves as high-level documentation for the OmniIngest architectural approach.*
