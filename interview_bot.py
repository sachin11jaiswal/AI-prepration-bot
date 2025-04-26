import streamlit as st
import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Streamlit App Setup
st.set_page_config(page_title="Interview Preparation Bot", page_icon="🤖")
st.title("🤖 Interview Preparation Bot🎯")

# Sidebar for settings
st.sidebar.header("🛠️ Setup Your Interview")
role = st.sidebar.text_input("Enter your Target Role (e.g., Software Engineer)")
domain = st.sidebar.text_input("Enter your Domain (optional, e.g., Backend)")
mode = st.sidebar.selectbox("Interview Mode", ["Technical", "Behavioral"])

# Session state to store all feedbacks and scores
if 'feedback_list' not in st.session_state:
    st.session_state.feedback_list = []
if 'scores_list' not in st.session_state:
    st.session_state.scores_list = []
if 'questions_list' not in st.session_state:
    st.session_state.questions_list = []

# Start Interview
if st.sidebar.button("Start Interview"):

    if not role:
        st.error("❗ Please enter your target role to begin.")
    else:
        st.success(f"🚀 Starting a {mode} interview for a {role} ({domain if domain else 'General'})")

        # Clear previous session
        st.session_state.feedback_list = []
        st.session_state.scores_list = []
        st.session_state.questions_list = []

        # Generate Questions
        prompt = f"Act like an interviewer. Ask 3 {mode.lower()} questions for a {role} in {domain if domain else 'general domain'}. Number them 1., 2., 3."
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional interviewer asking thoughtful questions."},
                {"role": "user", "content": prompt}
            ]
        )

        questions = response['choices'][0]['message']['content'].split('\n')

        for idx, question in enumerate(questions):
            if question.strip():
                st.session_state.questions_list.append(question.strip())

# Show Questions and Collect Answers
if st.session_state.questions_list:
    st.header("🧠 Interview Questions")

    for idx, question in enumerate(st.session_state.questions_list):
        st.subheader(f"Question {idx + 1}:")
        st.write(question)

        user_answer = st.text_area(f"✍️ Your Answer for Question {idx + 1}", key=f"answer_{idx}")

        if user_answer:
            if st.button(f"Get Feedback for Question {idx + 1}", key=f"feedback_button_{idx}"):

                feedback_prompt = f"""
                Evaluate the following interview answer:

                Role: {role}
                Domain: {domain}
                Interview Mode: {mode}
                Question: {question}
                Answer: {user_answer}

                Please provide:
                - A short feedback on strengths and weaknesses
                - A numeric score out of 10
                - Specific suggestions for improvement
                """

                feedback_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system",
                         "content": "You are an expert technical/HR interviewer providing constructive, detailed feedback."},
                        {"role": "user", "content": feedback_prompt}
                    ]
                )

                feedback_text = feedback_response['choices'][0]['message']['content']

                # Extract score from feedback using simple parsing (optional improvement later)
                score = None
                for line in feedback_text.split('\n'):
                    if 'score' in line.lower():
                        try:
                            score = int(''.join(filter(str.isdigit, line)))
                        except:
                            pass

                if score is None:
                    score = 7  # default if parsing fails

                # Store feedback and score
                st.session_state.feedback_list.append((idx + 1, feedback_text))
                st.session_state.scores_list.append(score)

                st.success("✅ Feedback Generated!")
                st.info(feedback_text)

# Final Result / Summary
if st.button("Show Final Summary") and st.session_state.scores_list:

    avg_score = sum(st.session_state.scores_list) / len(st.session_state.scores_list)

    st.header("📋 Final Interview Summary")

    st.subheader("Your Feedbacks:")
    for q_num, feedback in st.session_state.feedback_list:
        st.markdown(f"**Question {q_num}:**")
        st.info(feedback)

    st.subheader("🔢 Your Scores:")
    st.write(f"Scores per question: {st.session_state.scores_list}")
    st.write(f"**Average Score:** {round(avg_score, 2)} / 10")

    st.subheader("🌟 Overall Assessment:")
    if avg_score >= 8:
        st.success("Excellent performance! You're ready for real interviews! 🚀")
    elif avg_score >= 6:
        st.warning("Good effort! A little more polishing needed. ✨")
    else:
        st.error("Keep practicing! Focus on structuring your answers and clarity. 💪")

    st.balloons()

