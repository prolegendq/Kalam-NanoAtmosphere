import time
import streamlit as st
from src.auth_store import verify_password
from auth_email import generate_otp, send_otp_email

# If already logged in, redirect to Home
if st.session_state.get("logged_in"):
    st.switch_page("app.py")

# Hide sidebar on auth pages (clean look)
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
st.title("Login")

# session init
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "role" not in st.session_state:
    st.session_state.role = "user"

if "login_stage" not in st.session_state:
    st.session_state.login_stage = "credentials"
if "otp_code" not in st.session_state:
    st.session_state.otp_code = None
if "otp_ts" not in st.session_state:
    st.session_state.otp_ts = None
if "pending_email" not in st.session_state:
    st.session_state.pending_email = None

# Centered layout
_, col2, _ = st.columns([1, 2, 1])

with col2:
    with st.container(border=True):
        # already logged in
        if st.session_state.logged_in:
            st.success(f"Logged in as {st.session_state.user_email}")
            st.stop()

        # stage 1: credentials
        if st.session_state.login_stage == "credentials":
            if st.button("Back to Home"):
                st.switch_page("app.py")

            email = st.text_input("Email")
            password = st.text_input("Password", type="password")

            if st.button("Next"):
                if verify_password(email, password):
                    otp = generate_otp()
                    st.session_state.otp_code = otp
                    st.session_state.otp_ts = time.time()
                    st.session_state.pending_email = email.strip().lower()
                    st.session_state.login_stage = "otp"

                    send_otp_email(st.session_state.pending_email, otp)
                    st.success("OTP sent. Enter it below.")
                    st.rerun()  # Rerun to show OTP page
                else:
                    st.error("Invalid email or password. If new, register first.")

        # stage 2: otp
        elif st.session_state.login_stage == "otp":
            OTP_EXPIRY_SECONDS = 300
            remaining = int(OTP_EXPIRY_SECONDS - (time.time() - st.session_state.otp_ts))
            if remaining <= 0:
                st.error("OTP expired. Go back and resend.")
                if st.button("Back"):
                    st.session_state.login_stage = "credentials"
                    st.session_state.otp_code = None
                    st.session_state.otp_ts = None
                    st.session_state.pending_email = None
                    st.rerun()
                st.stop()

            st.info(f"OTP expires in {remaining}s")
            otp_in = st.text_input("Enter OTP")

            c1, c2 = st.columns(2)
            with c1:
                if st.button("Verify"):
                    if otp_in.strip() == st.session_state.otp_code:
                        st.session_state.logged_in = True
                        st.session_state.user_email = st.session_state.pending_email

                        # admin rule: only your email becomes admin
                        if st.session_state.user_email == "prolegendq7@gmail.com":
                            st.session_state.role = "admin"
                        else:
                            st.session_state.role = "user"

                        # reset otp state
                        st.session_state.login_stage = "credentials"
                        st.session_state.otp_code = None
                        st.session_state.otp_ts = None
                        st.session_state.pending_email = None

                        st.success("Login successful.")
                        st.switch_page("app.py")
                    else:
                        st.error("Wrong OTP.")

            with c2:
                if st.button("Resend OTP"):
                    otp = generate_otp()
                    st.session_state.otp_code = otp
                    st.session_state.otp_ts = time.time()
                    send_otp_email(st.session_state.pending_email, otp)
                    st.success("New OTP sent.")
                    st.rerun()