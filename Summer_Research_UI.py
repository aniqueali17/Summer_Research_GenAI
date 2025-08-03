
# Summer Research 2025 - GenAI- Lecture Notes Processing Script
# Instructor/Supervisor: Dr.Rami Sabouni, Systems and Computer Engineering Department, Carleton University
# Authors: Anique and Rotimi


import streamlit as st
import os
import requests
import time
from striprtf.striprtf import rtf_to_text
from dotenv import load_dotenv


# Load environment variables
load_dotenv("api.env")
groq_api_key = os.getenv("GROQ_API_KEY")
model = "llama3-70b-8192"


# === Helper functions ===

def extract_text_from_rtf(file):
    rtf_content = file.read()
    return rtf_to_text(rtf_content.decode(errors="ignore"))

def ask_groq(text, prompt, max_retries= 10, delay= 3.5):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    attempt = 0
    while attempt < max_retries:
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip().replace("*","")
        except Exception as e:
            attempt += 1
            print(f"⚠️ Attempt {attempt} failed: {e}")
            time.sleep(delay)

    raise Exception(f"❌ All {max_retries} attempts failed. Please try again later.")

def get_headings(text):
    prompt = (
        "Extract and list all the slide-level or section headings from the following lecture notes. "
        "Return only the titles, one per line. Ignore bullet points and body content.\n\n"
        f"{text}"
    )
    return ask_groq(text, prompt)

def get_summary(text):
    prompt = (
        "Provide a short and clear summary of the following file provided to you, suitable for quick review by students.\n\n"
        f"{text}"
    )
    return ask_groq(text, prompt)

def get_exercises(text, style="general"):
    if style == "mcq":
        exercise_type = "multiple choice questions"
    elif style == "theory":
        exercise_type = "theory questions"
    else:
        exercise_type = "a mix of different exercises"

    prompt = (
        f"Based on the following lecture notes, generate 5 {exercise_type} with their answers. "
        "Make sure they reflect the key topics covered in the lecture.\n\n"
        f"{text}"
    )
    return ask_groq(text, prompt)

# === Streamlit UI ===

st.title("📄 Lecture Notes Processor")  # set title 

uploaded_file = st.file_uploader("Upload RTF file", type="rtf")  # upload rtf file 

if uploaded_file:
    try:
        text = extract_text_from_rtf(uploaded_file)
        st.success("RTF file loaded and converted to text.") #  (check if file uploadaded)

        if st.button("Extract Headings"):  #extract heading button this button is clickable
            with st.spinner("Extracting headings..."):
                try:
                    headings = get_headings(text)  # call get heading function on line 38
                    st.text_area("📚 Headings Found", headings, height=200) # display heading in text area (text_area is scrollable)
                except Exception as e: # error handling
                    st.error(f"Failed to extract headings: {e}")

        if st.button("Generate Summary"):  # generate summary button
            with st.spinner("Generating summary..."):
                try:
                    summary = get_summary(text) # call get summary function on line 46
                    st.text_area("📘 Summary", summary, height=200) # display summary in the text area
                except Exception as e: # error handling
                    st.error(f"Failed to generate summary: {e}")

        st.subheader("📝 Generate Exercises") # generate excercise title 
        exercise_type = st.selectbox("Choose exercise type:", ["mixed", "mcq", "theory"]) # dropdown for exercise type

        if st.button("Create Exercises"): # create exercises button
            with st.spinner("Generating exercises..."):
                try:
                    exercises = get_exercises(text, style=exercise_type)   # call get exercises function on line 53
                    st.text_area(f"{exercise_type.upper()} Exercises", exercises, height=300) # display different types of excercises in the text area
                except Exception as e:
                    st.error(f"Failed to generate exercises: {e}")

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")