import streamlit as st

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.main-header {
    background: linear-gradient(135deg, #f8b4d9 0%, #e8a0bf 40%, #c9e4ca 100%);
    padding: 2rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 24px rgba(232, 160, 191, 0.25);
}

.main-header h1 {
    color: #2d3436;
    font-size: 2rem;
    font-weight: 700;
    margin: 0;
}

.main-header p {
    color: #636e72;
    margin: 0.5rem 0 0 0;
    font-size: 1rem;
}

.result-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.75rem 2rem;
    border-radius: 16px;
    color: white;
    text-align: center;
    margin: 1rem 0;
    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.35);
}

.result-card .amount {
    font-size: 2.5rem;
    font-weight: 700;
    letter-spacing: -0.02em;
}

.result-card .label {
    font-size: 0.9rem;
    opacity: 0.9;
    margin-top: 0.25rem;
}

div[data-testid="stMetric"] {
    background: #f8f9fa;
    padding: 1rem 1.25rem;
    border-radius: 12px;
    border: 1px solid #e9ecef;
}

div[data-testid="stMetric"] label {
    font-size: 0.85rem !important;
    color: #636e72 !important;
}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    color: #2d3436 !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    border-radius: 10px;
    padding: 0.6rem 2rem;
    font-weight: 600;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #fdf6f9 0%, #f0f4f8 100%);
}

.shop-badge {
    display: inline-block;
    background: #fff;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    margin: 0.25rem 0;
    border: 1px solid #e9ecef;
    font-size: 0.9rem;
}
</style>
"""


def apply_styles() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
