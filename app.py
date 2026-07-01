import streamlit as st

from database import get_all_calculations, get_all_employees
from ui.analytics import render_analytics
from ui.calculate import render_calculate_section
from ui.header import render_header
from ui.session import clear_last_result_if_no_employees, init_session_state
from ui.sidebar import render_sidebar
from ui.styles import apply_styles

st.set_page_config(
    page_title="Зарплата флористов",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_styles()
init_session_state()

employees = get_all_employees()
history = get_all_calculations()

clear_last_result_if_no_employees(bool(employees))

render_header()

with st.sidebar:
    render_sidebar(employees, len(history))

history = render_calculate_section(employees, history)
render_analytics(history)
