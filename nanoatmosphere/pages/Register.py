import streamlit as st
from src.auth_store import register_user

st.set_page_config(page_title="Register", layout="wide")

# Hide sidebar on auth pages and add custom styles
st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .form-container {
            border: 1px solid #e6e6e6;
            border-radius: 10px;
            padding: 2rem;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            background-color: #f9f9f9;
        }
        /* Center the title */
        h1 {
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown(
    """
    <h1 style='text-align: center;'>
        <span style='color: #F46DC3;'>Kalam </span><span style='color: #FBD85B;'>Nano</span><span style='color: #56D5F2;'>Atmosphere</span>
    </h1>
    """,
    unsafe_allow_html=True
)
st.title("Register")

_, col2, _ = st.columns([1, 2, 1])

with col2:
    with st.container(border=True):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        password2 = st.text_input("Confirm password", type="password")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Create account"):
                if password != password2:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = register_user(email, password)
                    if ok:
                        st.success(msg)
                        st.info("Now go to Login page and sign in.")
                    else:
                        st.error(msg)
        with c2:
            if st.button("Back to Login"):
                st.switch_page("pages/Login.py")