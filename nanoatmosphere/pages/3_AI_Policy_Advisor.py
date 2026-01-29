import os
import textwrap
import streamlit as st
from datetime import datetime
import google.generativeai as genai
import google.api_core.exceptions as gexceptions

# ─── BACK BUTTON + AUTH GUARD ───
if st.button("🏠 ← Back to Home", use_container_width=False):
    st.switch_page("app.py")
if "user_logs" not in st.session_state:
    st.session_state.user_logs = []

# Log with CONSISTENT keys
st.session_state.user_logs.append({
    "user": st.session_state.get("user_email", "guest"),
    "action": "Page visited",
    "page": "AI Policy Advisor",  # Change per page
    "timestamp": datetime.now().strftime("%H:%M:%S")
})

# ---------- GEMINI / GenAI CONFIG ----------

# Choose a fast model that exists in your account
GEMINI_MODEL = "gemini-2.5-flash"

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error(
        "GEMINI_API_KEY is not set. "
        "Add it as an environment variable or in .streamlit/secrets.toml."
    )
    st.stop()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL)

# ---------- PROMPT BUILDING ----------

SYSTEM_INSTRUCTION = """
You are Kalam NanoAtmosphere, an AI co-pilot helping Indian city officials reduce
urban NO2, SO2, and CO from traffic and industry.

Rules:
- Be concise and practical, prefer bullet points.
- Always quantify impact using Kalam NanoAtmosphere terms:
  - Breathability Index (0–100, higher is better).
  - Risk Level: Low / Medium / High.
- Assume Sentinel-5P satellite inputs at ~1 km resolution.
- Suggest levers like odd-even traffic, diesel bans, low-emission zones,
  school-time red alerts, and industrial stack controls.
- Always close with 3 concrete actions that can be done in the next 30 days.
"""

def build_policy_prompt(city: str,
                        baseline_no2: float,
                        breathe_score: float,
                        risk_level: str,
                        user_goal: str) -> str:
    prompt = f"""
    {SYSTEM_INSTRUCTION}

    City: {city}
    Current NO2 (mol/m²): {baseline_no2:.1e}
    Current Breathability Index: {breathe_score:.0f}/100
    Current Risk Level: {risk_level}

    Policy maker's goal (from user): {user_goal}

    Tasks:
    1. Briefly explain what the current numbers mean in plain language.
    2. Propose 3–5 targeted interventions tailored to this city.
    3. For each intervention, estimate:
       - Expected NO2 change (approx %).
       - Expected Breathability improvement (points).
       - Implementation difficulty: Low / Medium / High.
    4. Highlight any trade-offs (traffic, economy, schools, etc.).
    5. Give a 30-day action plan as 3 bullet points.

    Use short bullet lists, no long paragraphs.
    """
    return textwrap.dedent(prompt).strip()

# ---------- GEMINI CALL WITH QUOTA HANDLING ----------
PREDEFINED_FALLBACK = """
Kalam NanoAtmosphere AI is currently unavailable, so this is a cached playbook for Indian urban micro-zones.

- Tighten traffic around schools and hospitals during peak hours using dynamic diversion and no-parking rings.
- Enforce no-idling and stricter checks on old diesel vehicles and autos in the dirtiest corridors first.
- Upgrade or retrofit a small set of top-emitting industrial stacks with low-NOₓ burners and continuous monitoring.
- Use red / orange alert days to push work-from-home, staggered school timings, and public transport fare discounts.
- Run one weekly 'clean corridor' where only public transport and EVs are allowed for a fixed 2–3 hour window.

Expected impact (if seriously enforced in the focus micro-zones):
- NO₂ reduction: roughly 15–25% over 6 months.
- Breathability Index: +10 to +18 points.
- Risk Level: can often shift from High → Medium, or Medium → Low for the target corridor.
"""

def call_gemini_policy_advisor(prompt: str) -> str:
    if not API_KEY:
        st.error("No GEMINI_API_KEY found. Please set it to use the AI Advisor.")
        return PREDEFINED_FALLBACK

    try:
        if not GEMINI_MODEL:
            st.error("GEMINI_MODEL is not set. Please specify a valid model name.")
            return PREDEFINED_FALLBACK

        response = model.generate_content(
            contents=prompt,
            generation_config={
                "temperature": 0.4,
                "max_output_tokens": 2048,
            },
        )
        text = response.text
        if not text:
            st.warning("Gemini AI returned an empty response. Using fallback.")
            return PREDEFINED_FALLBACK
        return text
    except gexceptions.ResourceExhausted:
        st.warning(
            "Gemini AI quota exhausted or billing not enabled. "
            "Using fallback. Check your Google Cloud project settings."
        )
        return PREDEFINED_FALLBACK
    except gexceptions.ServiceUnavailable:
        st.warning("Gemini AI service is temporarily unavailable. Using fallback.")
        return PREDEFINED_FALLBACK
    except gexceptions.InvalidArgument as e:
        st.error(f"Gemini AI received an invalid argument: {e}. Using fallback.")
        return PREDEFINED_FALLBACK
    except gexceptions.GoogleAPIError as e:
        st.error(f"A Google API error occurred: {e}. Using fallback.")
        return PREDEFINED_FALLBACK
    except Exception as e:
        st.error(f"An unexpected error occurred with Gemini AI: {e}. Using fallback.")
        return PREDEFINED_FALLBACK

# ---------- STREAMLIT UI ----------

st.title("AI Policy Advisor")

st.write(
    """
    Kalam NanoAtmosphere's **AI Policy Advisor** converts satellite-driven gas readings
    into targeted action plans for your chosen micro-zone or city.
    """
)

col_left, col_right = st.columns([2, 3])

with col_left:
    city = st.selectbox(
        "Select city",
        ["Chennai", "Delhi", "Mumbai"],
        index=0,
    )

    baseline_no2 = st.number_input(
        "Baseline NO₂ for this zone (mol/m²)",
        value=9.8e-05,
        format="%.1e",
        help="Use the value from the Predictive Micro‑Cloud page for the selected micro‑zone.",
    )

    breathe_score = st.slider(
        "Current Breathability Index",
        min_value=0,
        max_value=100,
        value=76,
        step=1,
    )

    risk_level = st.selectbox(
        "Current Risk Level",
        ["Low", "Medium", "High"],
        index=1,
    )

    user_goal = st.text_area(
        "Policy goal / constraints",
        value="Reduce NO₂ by at least 20% in 6 months without fully banning private vehicles.",
        height=120,
    )

    ask_button = st.button("Ask Kalam NanoAtmosphere AI Advisor", type="primary")

with col_right:
    st.subheader("Advisor Output")

    if ask_button:
        with st.spinner("Consulting Gemini policy brain..."):
            full_prompt = build_policy_prompt(
                city=city,
                baseline_no2=baseline_no2,
                breathe_score=breathe_score,
                risk_level=risk_level,
                user_goal=user_goal,
            )
            advice = call_gemini_policy_advisor(full_prompt)

        st.markdown(advice)
    else:
        st.info(
            "Set the city, NO₂ baseline, Breathability Index, and your policy goal, "
            "then click **Ask Kalam NanoAtmosphere AI Advisor** to generate a strategy."
        )
