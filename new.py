import streamlit as st
import google.generativeai as genai

# ==========================================
# STREAMLIT CONFIG
# ==========================================

st.set_page_config(
    page_title="AI Gherkin Generator",
    layout="wide"
)

st.title("🧪 AI Test Scenario Generator")
st.markdown(
    "Generate BDD Gherkin scenarios from Requirements / User Stories"
)

# ==========================================
# SAMPLE STORIES
# ==========================================

sample_stories = """
User Login =>
As a user, I want to log in so that I can access my account.

Password Reset =>
As a user, I want to reset my password so that I can regain access to my account.

Product Checkout =>
As a customer, I want to purchase products online.
"""

with st.expander("📜 Sample User Stories"):
    st.code(sample_stories)

# ==========================================
# USER INPUT
# ==========================================

user_story = st.text_area(
    "📜 Requirement / User Story",
    height=200,
    value=""
)

preset = st.selectbox(
    "🎯 Test Strategy",
    [
        "Full Coverage",
        "Happy Path Only",
        "Negative Testing",
        "Boundary Testing",
        "Security Testing",
        "Regression Suite",
        "BDD Automation Friendly"
    ]
)

PROMPT_PRESETS = {
    "Full Coverage":
        """
Generate comprehensive coverage including:
- Positive scenarios
- Negative scenarios
- Validation scenarios
- Boundary scenarios
- Error handling
- Business rules
        """,

    "Happy Path Only":
        """
Generate only successful business flow scenarios.
        """,

    "Negative Testing":
        """
Focus on:
- Invalid inputs
- Error handling
- Validation failures
- Unexpected user actions
        """,

    "Boundary Testing":
        """
Focus on:
- Boundary Value Analysis
- Equivalence Partitioning
- Input limits
        """,

    "Security Testing":
        """
Include:
- Authentication
- Authorization
- Session handling
- Invalid access attempts
        """,

    "Regression Suite":
        """
Generate only high-priority business critical scenarios.
        """,

    "BDD Automation Friendly":
        """
Generate reusable automation-friendly steps.

Rules:
- Reuse Given steps
- Avoid UI-specific wording
- Suitable for Selenium/Appium automation
- Use Scenario Outline when appropriate
        """
}

output_mode = st.selectbox(
    "📦 Output Mode",
    [
        "Gherkin",
        "Test Cases",
        "Gherkin + Step Definition",
        "Gherkin + Selenium Skeleton",
        "Gherkin + Appium Skeleton"
    ]
)

user_instruction = st.text_area(
    "🤖 Additional AI Instruction (Optional)",
    height=120,
    value=""
)

# ==========================================
# OLLAMA CONFIG
# ==========================================

genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

# ==========================================
# GENERATE GHERKIN
# ==========================================

def generate_gherkin(
    requirement,
    strategy,
    output_mode,
    additional_instruction
):

    prompt = f"""
Requirement:
{requirement}

Test Strategy:
{strategy}

Output Mode:
{output_mode}

Additional Instruction:
{additional_instruction}

Generate output according to the selected Output Mode.
Return only the requested output.
"""

    model = genai.GenerativeModel("gemini-2.5-flash")

    response = model.generate_content(prompt)

    return response.text

# ==========================================
# GENERATE BUTTON
# ==========================================

if st.button("🚀 Generate"):

    with st.spinner("Generating scenarios..."):

        result = generate_gherkin(
            user_story,
            PROMPT_PRESETS[preset],
            output_mode,
            user_instruction
        )

        st.subheader("Generated Output")

        st.code(result)

        st.download_button(
            "📥 Download",
            result,
            file_name="output.feature"
        )