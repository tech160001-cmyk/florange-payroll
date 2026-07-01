import streamlit as st


def render_header() -> None:
    st.markdown(
        """
        <div class="main-header">
            <h1>🌸 Зарплата флористов</h1>
            <p>Калькулятор выплат: оклад + 5% от выручки − штрафы</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
