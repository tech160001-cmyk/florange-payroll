import streamlit as st


def init_session_state() -> None:
    if "last_result" not in st.session_state:
        st.session_state.last_result = None


def clear_last_result_if_no_employees(has_employees: bool) -> None:
    if not has_employees:
        st.session_state.last_result = None
