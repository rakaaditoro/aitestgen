import streamlit as st
import pandas as pd
import simplejson as json
import re
from autogen import UserProxyAgent, AssistantAgent

# Streamlit UI Setup
st.set_page_config(page_title="QA Test Case Generator", layout="wide")
st.markdown("<h1 style='text-align: center; font-size: 32px;'>🧪 AI-Powered QA Test Case Generator</h1>", unsafe_allow_html=True)

# Sample User Stories for Copy-Paste
sample_stories = """ 
User Login => As a user, I want to log in so that I can access my account.

Password Reset => As a user, I want to reset my password so that I can regain access to my account if I forget my credentials.

Product Checkout => As a customer, I want to add products to my cart and proceed to checkout so that I can purchase items online.

Profile Update => As a user, I want to update my profile information so that I can keep my account details up to date.

Search Functionality => As a user, I want to search for products by name or category so that I can quickly find what I need.
"""

st.markdown("### 📜 Sample User Stories (Copy-Paste)")
st.code(sample_stories, language="text")
st.write("Enter a user story, and the AI will generate detailed test cases for you!")

# User Input
user_story = st.text_area("📜 Enter User Story:", "As a user, I want to log in so that I can access my account.")

user_instruction = st.text_area(
    "🤖 AI Instruction (Optional)",
    value="""
Generate Gherkin scenarios.
Focus on happy path and negative scenarios.
Use Scenario Outline when applicable.
"""
)

config_list = [
    {
        "model": "llama3.2",
        "api_type": "ollama",
        "stream": False,
    }
]

# AutoGen Agents Setup
qa_agent = AssistantAgent(
    name="QA_Agent",
    max_consecutive_auto_reply=1,
    human_input_mode="NEVER",
    llm_config={
        "timeout": 600,
        "cache_seed": 42,
        "config_list": config_list,
    }
)

user_proxy = UserProxyAgent(
    name="User",
    max_consecutive_auto_reply=1,
    human_input_mode="NEVER",
    code_execution_config=False
)


# Function to Generate Test Cases
def generate_test_cases(story):
    prompt = f"""
    You are a Senior QA Engineer specialized in:

    - Manual Testing
    - Automation Testing
    - BDD
    - Test Design Techniques
    - Risk Based Testing

    Your task is to analyze requirements and generate test scenarios.

    Requirement:
    {story}

    Additional Instructions:
    {user_instruction}

    General Rules:
    - Identify business rules.
    - Identify validations.
    - Identify positive scenarios.
    - Identify negative scenarios.
    - Identify boundary scenarios.
    - Identify edge cases.
    - Avoid duplicate scenarios.
    - Use professional QA terminology.

    Output Format:
    Generate output in JSON.

    Example:

    [
        {{
            "Scenario ID": "SC001",
            "Scenario Name": "Successful Login",
            "Scenario Type": "Positive",
            "Priority": "High",
            "Precondition": "User is on login page",
            "Test Steps": [
                "Enter valid username",
                "Enter valid password",
                "Click Login"
            ],
            "Expected Result": "User is redirected to dashboard"
        }}
    ]

    Return only valid JSON.
    """


    

    # Initiating chat with the QA agent
    response = user_proxy.initiate_chat(qa_agent, message=prompt)

    # Extract JSON from AI response
    return extract_json_from_response(response)

preset = st.selectbox(
    "🎯 Test Strategy",
    [
        "Full Coverage",
        "Happy Path Only",
        "Negative Testing",
        "Boundary Testing",
        "Security Testing",
        "Regression Suite",
        "BDD Gherkin"
    ]
)

PROMPT_PRESETS = {
    "Full Coverage":
        "Generate complete coverage including positive, negative, edge, boundary, security, and regression scenarios.",

    "Happy Path Only":
        "Generate only happy path scenarios.",

    "Negative Testing":
        "Focus on invalid inputs, error handling, and failure scenarios.",

    "Boundary Testing":
        "Focus on boundary value analysis and equivalence partitioning.",

    "Security Testing":
        "Include authentication, authorization, session management, and security scenarios.",

    "Regression Suite":
        "Generate only business critical regression scenarios.",

    "BDD Gherkin":
        "Generate output in Gherkin Feature/Scenario format."
}

selected_preset_prompt = PROMPT_PRESETS[preset]


# Function to Extract JSON from AI Response
def extract_json_from_response(response):
    chat_messages = response.chat_history

    # Look for the user response from the AI agent (role == 'user' or 'assistant')
    for message in reversed(chat_messages):
        if 'content' in message and isinstance(message['content'], str):
            possible_json = message['content'].strip()

            # Try parsing directly
            try:
                return json.loads(possible_json)
            except json.JSONDecodeError:
                pass  # fallback to regex below

            # Try regex fallback if direct load fails
            match = re.search(r'(\[\s*{.*?}\s*\])', possible_json, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError as e:
                    print("❌ JSON decode failed:", e)
                    print("🔧 Problematic JSON Block:\n", match.group(1))
                    return None

    print("❌ No valid JSON found in chat history.")
    return None



# Generate Button
if st.button("🚀 Generate Test Cases"):
    with st.spinner("Generating test cases..."):
        test_cases = generate_test_cases(user_story)

        if test_cases:
            # Convert JSON data into a DataFrame
            df = pd.DataFrame(test_cases)
            st.dataframe(df)

            # Download as CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Test Cases as CSV", data=csv, file_name="test_cases.csv", mime="text/csv")
        else:
            st.error("❌ Failed to generate test cases. Check AI response.")
