
import streamlit as st
import altair as alt

def setup_page():
    st.set_page_config(page_title="OmniIngest ABDM 2.0", page_icon="🏥", layout="wide")
    
    # Custom CSS for "Modern GenAI" aesthetics
    st.markdown("""
        <style>
        /* Main Background */
        .stApp {
            background-color: #0d1117;
            color: #e6edf3;
        }
        
        /* Header & Sidebar */
        header, [data-testid="stSidebar"] {
            background-color: #161b22 !important;
        }
        
        /* Buttons - Glow Effect */
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            height: 3.2em;
            background-color: #10a37f; /* GenAI Teal */
            color: white;
            border: none;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 14px 0 rgba(16, 163, 127, 0.3);
        }
        .stButton>button:hover {
            background-color: #1a7f64;
            box-shadow: 0 6px 20px 0 rgba(16, 163, 127, 0.5);
            transform: translateY(-1px);
        }
        
        /* Cards - Glassmorphism */
        div[data-testid="stMetric"] {
            background-color: #21262d;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #30363d;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        
        /* File Uploader */
        section[data-testid="stFileUploadDropzone"] {
            background-color: #161b22;
            border: 2px dashed #10a37f;
            border-radius: 12px;
        }
        
        /* Table Styling */
        .stDataFrame {
            border: 1px solid #30363d !important;
            border-radius: 8px !important;
        }
        </style>
        """, unsafe_allow_html=True)

def render_header():
    st.title("🏥 OmniIngest ABDM 2.0")
    st.markdown("<p style='color: #8b949e;'>Modern AI-Powered Clinical Data Ingestion</p>", unsafe_allow_html=True)
    st.markdown("---")

def render_governance_sidebar(governance_logs):
    st.sidebar.markdown("""
        <div style='background-color: #3e1616; padding: 15px; border-radius: 8px; border: 2px solid #ff4d4d; margin-bottom: 20px; text-align: center;'>
            <h4 style='margin: 0; color: #ff8080;'>🚨 [DPDP RULE 8.3 ACTIVE]</h4>
            <small style='color: #8b949e;'>Real-time PII Hard-Purge Enabled</small>
        </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("### 📜 Governance Log")
    log_container = st.sidebar.empty()
    if governance_logs:
        log_container.code("\n".join(governance_logs), language="bash")
    else:
        log_container.code("# System Ready\n# Awaiting Ingress...", language="bash")

def render_revoked_warning():
    st.markdown("""
        <div style='background-color: #3e1616; color: #ff8080; padding: 15px; border-radius: 8px; border: 1px solid #ff4d4d; margin-bottom: 20px;'>
            <h3 style='margin:0; color: #ff8080;'>⚠️ SESSION REVOKED</h3>
            <p style='margin:5px 0 0 0;'>Data purged per DPDP Rule 8. System locked until session reset.</p>
        </div>
    """, unsafe_allow_html=True)

def get_chart(data):
    # Ensure color column is used
    base = alt.Chart(data).encode(
        x=alt.X('Status', sort=None),
        y='Count',
        color=alt.Color('Color', scale=None),
        tooltip=['Status', 'Count']
    )
    chart = base.mark_bar().properties(
        title="Ingestion Health"
    )
    return chart
