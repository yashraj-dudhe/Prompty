import streamlit as st
import requests
import os
import json
import csv
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set Gemini API Key and Endpoint
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  
GEMINI_API_ENDPOINT = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent?key={GEMINI_API_KEY}"

if not GEMINI_API_KEY:
    st.error("Error: GEMINI_API_KEY is not set. Please check your .env file.")
    st.stop()

LOG_FILE = "prompt_history.csv"

# Initialize session state for conversation history
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# Function to send requests to Gemini API
def send_request(prompt):
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}]
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(GEMINI_API_ENDPOINT, json=payload, headers=headers)

    if response.status_code == 200:
        response_json = response.json()

        if "candidates" in response_json:
            return response_json["candidates"][0]["content"]["parts"][0]["text"]
        else:
            st.error(f"Error: No candidates available in the response. Full response: {response_json}")
            return "No candidates available in the response"
    else:
        st.error(f"Error: API request failed with status code {response.status_code}: {response.text}")
        return f"API request failed with status code {response.status_code}"

# Function to evaluate the prompt
def evaluate_prompt(prompt):
    evaluation_instruction = (
        "Evaluate this prompt based on: "
        "1. Clarity (1-10), 2. Conciseness (1-10), 3. Specificity (1-10), 4. Relevance (1-10). "
        "Provide a numerical score for each category."
        f"\nPrompt: {prompt}"
    )
    return send_request(evaluation_instruction)

# Function to optimize the prompt
def optimize_prompt(prompt):
    optimization_instruction = (
        "Rewrite this prompt to be clearer, more concise, and more specific while keeping the original intent.\n"
        f"Original Prompt: {prompt}"
    )
    return send_request(optimization_instruction)

# Function to get LLM response
def get_llm_response(prompt):
    return send_request(prompt)

# Function to log and save conversation history
def log_conversation(original, optimized, evaluation, original_response, optimized_response):
    entry = {
        "timestamp": str(datetime.now()),
        "original_prompt": original,
        "optimized_prompt": optimized,
        "evaluation": evaluation,
        "original_response": original_response,
        "optimized_response": optimized_response
    }

    # Append to session state for display
    st.session_state.conversation.append(entry)

    # Save to CSV file
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=entry.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(entry)

# Streamlit UI
st.title("🔍 AI Prompt Optimization (with History)")

user_prompt = st.text_area("Enter your prompt:", height=150)

if st.button("Analyze & Optimize"):
    if user_prompt:
        with st.spinner("Evaluating prompt..."):
            evaluation = evaluate_prompt(user_prompt)
        with st.spinner("Optimizing prompt..."):
            optimized_prompt = optimize_prompt(user_prompt)

        st.subheader("🔹 Evaluation:")
        st.write(evaluation)

        st.subheader("✨ Optimized Prompt:")
        st.code(optimized_prompt, language="text")

        with st.spinner("Generating responses..."):
            original_response = get_llm_response(user_prompt)
            optimized_response = get_llm_response(optimized_prompt)

        st.subheader("📊 Comparison:")
        st.write("**Original Response:**", original_response)
        st.write("**Optimized Response:**", optimized_response)

        # Save conversation history
        log_conversation(user_prompt, optimized_prompt, evaluation, original_response, optimized_response)
    else:
        st.warning("Please enter a prompt to analyze.")

# Show conversation history
st.sidebar.title("📜 Conversation History")

if st.session_state.conversation:
    for entry in reversed(st.session_state.conversation):
        st.sidebar.markdown(f"**🕒 {entry['timestamp']}**")
        st.sidebar.markdown(f"🔹 **Original Prompt:** {entry['original_prompt']}")
        st.sidebar.markdown(f"✨ **Optimized Prompt:** {entry['optimized_prompt']}")
        st.sidebar.markdown(f"📊 **Evaluation:** {entry['evaluation']}")
        st.sidebar.markdown(f"📢 **Original Response:** {entry['original_response']}")
        st.sidebar.markdown(f"🎯 **Optimized Response:** {entry['optimized_response']}")
        st.sidebar.markdown("---")
else:
    st.sidebar.write("No conversation history yet.")