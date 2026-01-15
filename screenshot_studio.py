import streamlit as st
import pandas as pd
import graphviz
from datetime import datetime
import time

# Page Config (Teal/Dark Mode)
st.set_page_config(page_title="OmniIngest Studio", page_icon="📸", layout="wide")

# Custom CSS for the "2026 Vibe"
st.markdown("""
<style>
    /* Dark Mode Background */
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
    }
    
    /* Global Teal Accent #008080 */
    .stButton>button {
        background-color: #008080 !important;
        color: white !important;
        border-radius: 6px;
        border: none;
        box-shadow: 0 0 10px rgba(0, 128, 128, 0.3);
    }
    
    /* Metrics / Cards */
    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Segoe UI', sans-serif;
        color: #008080 !important; /* Teal Headers */
    }
    
    /* Mock Terminal for Screen 2 */
    .terminal-window {
        background-color: #000;
        color: #0f0;
        font-family: 'Courier New', monospace;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #333;
        box-shadow: 0 0 20px rgba(0, 128, 128, 0.2);
    }
    
    /* Architecture Map Nodes */
    .arch-node {
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Controller
st.sidebar.title("📸 Screenshot Studio")
screen = st.sidebar.radio("Select View", ["1. Clinical Dashboard", "2. Rule 8.3 Audit Log", "3. Compliance Architecture"])

# --- SCREEN 1: THE CLINICAL DASHBOARD ---
if screen == "1. Clinical Dashboard":
    st.markdown("## 🏥 Clinical Dashboard (2026)")
    st.markdown("_Live Patient Feed | FHIR R5 Protocol_")
    
    # Top Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Active Sessions", "142", "+12")
    c2.metric("Pending Consent", "8", "-2")
    c3.metric("Avg Ingest Time", "0.4s", "⚡ Lightning")
    c4.metric("Rule 8.3 Status", "ARMED", delta_color="off")
    
    st.markdown("---")
    
    # Fake FHIR R5 Data
    data = [
        {"Patient ID": "P-2026-X92", "Resource": "Patient", "Last Encounter": "2026-01-15 09:30 AM", "Consent Status": "GRANTED", "Triage": "High"},
        {"Patient ID": "P-2026-A11", "Resource": "Observation", "Last Encounter": "2026-01-15 10:15 AM", "Consent Status": "GRANTED", "Triage": "Normal"},
        {"Patient ID": "P-2026-C44", "Resource": "Condition", "Last Encounter": "2026-01-14 16:45 PM", "Consent Status": "REVOKED", "Triage": "Purged"},
        {"Patient ID": "P-2026-B88", "Resource": "Encounter", "Last Encounter": "2026-01-15 11:00 AM", "Consent Status": "GRANTED", "Triage": "Normal"},
        {"Patient ID": "P-2026-D01", "Resource": "MedicationRequest", "Last Encounter": "2026-01-15 11:20 AM", "Consent Status": "GRANTED", "Triage": "High"},
    ]
    df = pd.DataFrame(data)
    
    # Custom highlighting
    def highlight_status(val):
        if val == "REVOKED": return 'background-color: #3e1616; color: #ff4b4b; font-weight: bold;'
        if val == "GRANTED": return 'color: #008080; font-weight: bold;'
        return ''

    st.dataframe(df.style.map(highlight_status, subset=["Consent Status"]), use_container_width=True)
    
    st.button("Main Action: Ingest New Bundle")

# --- SCREEN 2: THE "RULE 8.3" AUDIT LOG ---
elif screen == "2. Rule 8.3 Audit Log":
    st.markdown("## 🛡️ Rule 8.3 Kill Switch Audit")
    st.markdown("_Cryptographic Shredding Event Log_")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # The Log Component
    audit_log_html = """
    <div class="terminal-window">
        <div>$ initiate_purge_sequence --target=SESSION_ABDM_2026</div>
        <div style="color: #888;">> Verifying Admin Privileges... [OK]</div>
        <div style="color: #888;">> Locating PII Blocks in Memory... [FOUND 12 BLOCKS]</div>
        <br>
        <div style="color: #orange;">[WARNING] Irreversible Action Initiated...</div>
        <div>> Unlinking Identity Keys... [DONE]</div>
        <div>> Overwriting Memory (Pass 1/3)... [DONE]</div>
        <div>> Overwriting Memory (Pass 2/3)... [DONE]</div>
        <div>> Overwriting Memory (Pass 3/3)... [DONE]</div>
        <br>
        <div style="color: #ff4b4b; font-weight: bold; font-size: 1.1em; border: 1px solid #ff4b4b; padding: 10px;">
        [RULE 8.3 AUDIT] - PII Decryption Keys Permanently Shredded. <br>
        Data is now mathematically unrecoverable.
        </div>
        <br>
        <div style="color: #008080;">> Governance Log Updated (Audit ID: SHA-256-X99)</div>
        <div>$ _</div>
    </div>
    """
    st.markdown(audit_log_html, unsafe_allow_html=True)

# --- SCREEN 3: COMPLIANCE ARCHITECTURE ---
elif screen == "3. Compliance Architecture":
    st.markdown("## 🏗️ Technical Proof: The Secure Gateway")
    st.markdown("_Separation of Concerns: PII Vault vs Clinical Metadata_")
    
    # Graphviz Diagram
    graph = graphviz.Digraph()
    graph.attr(bgcolor='#0d1117', fontcolor='white')
    graph.attr('node', style='filled', fontname='Segoe UI', shape='box')
    
    # Nodes
    graph.node('A', 'Unstructured Input\n(PDF/CSV/HL7)', fillcolor='#21262d', fontcolor='white')
    
    graph.node('G', 'ABDM 2.0\nSecure Gateway', fillcolor='#008080', fontcolor='white', penwidth='2')
    
    graph.node('P', 'PII Vault\n(Encrypted Keys)', fillcolor='#3e1616', fontcolor='#ff4b4b', shape='cylinder')
    graph.node('C', 'Clinical Metadata\n(FHIR R5)', fillcolor='#0d1117', fontcolor='#00ff00', color='#00ff00')
    
    # Edges
    graph.edge('A', 'G', color='white')
    graph.edge('G', 'P', label=' Extract Identity', color='#ff4b4b', fontcolor='#ff4b4b')
    graph.edge('G', 'C', label=' Anonymized Resources', color='#00ff00', fontcolor='#00ff00')
    
    # Rule 8.3 Cut line
    graph.edge('P', 'P', label=' Rule 8.3\nKill Switch', color='red', style='dashed')
    
    st.graphviz_chart(graph)
    
    st.markdown("""
    <div style='text-align: center; border: 1px dashed #30363d; padding: 20px; border-radius: 10px;'>
        <small>Architecture Diagram: Phase 0.1 Implementation</small>
    </div>
    """, unsafe_allow_html=True)
