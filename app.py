import json
import os
import re
from typing import Any

import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(
    page_title="AI Interview Prep Coach",
    page_icon="🎯",
    layout="centered",
)

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def get_api_key() -> str:
    """Read the Gemini key from Streamlit secrets first, then environment."""
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        key = ""
    return key or os.getenv("GEMINI_API_KEY", "")


def get_client():
    key = get_api_key()
    if not key:
        return None
    return genai.Client(api_key=key)


def extract_json(text: str) -> dict[str, Any]:
    """Parse JSON from a model response, tolerating accidental code fences."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start < 0 or end < start:
        raise ValueError("The AI response did not contain a JSON object.")
    return json.loads(cleaned[start : end + 1])


def ask_gemini(client, prompt: str) -> str:
    response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.4,
            response_mime_type="application/json",
        ),
    )
    if not response.text:
        raise ValueError("Gemini returned an empty response. Please try again.")
    return response.text


def make_question(client, role: str, level: str, interview_type: str,
                  focus: str, asked_questions: list[str]) -> dict[str, Any]:
    prompt = f"""
You are a supportive but honest interview coach. Create exactly one realistic
interview question and return only a JSON object with keys:
question (string), what_it_tests (string), answer_tips (array of 3 short strings).
Role/target: {role}
Candidate level: {level}
Interview style: {interview_type}
Focus areas: {focus or "general role-related skills"}
Questions already asked (avoid repeating these): {json.dumps(asked_questions)}
Make the question appropriate to the role and level. Do not answer the question.
"""
    data = extract_json(ask_gemini(client, prompt))
    if not isinstance(data.get("question"), str) or not data["question"].strip():
        raise ValueError("Gemini did not provide a valid question.")
    data.setdefault("what_it_tests", "Communication, reasoning, and role knowledge")
    data.setdefault("answer_tips", [])
    return data


def review_answer(client, role: str, level: str, question: str,
                  answer: str) -> dict[str, Any]:
    prompt = f"""
You are an experienced interview coach. Evaluate the candidate's answer fairly,
constructively, and specifically. Do not reward length alone. Account for the
role and candidate level. Return ONLY valid JSON with this exact structure:
{{
  "overall_score": 0,
  "criteria": [
    {{"name": "Relevance", "score": 0, "max_score": 10, "comment": "..."}},
    {{"name": "Specificity and examples", "score": 0, "max_score": 10, "comment": "..."}},
    {{"name": "Structure and clarity", "score": 0, "max_score": 10, "comment": "..."}},
    {{"name": "Impact and reflection", "score": 0, "max_score": 10, "comment": "..."}}
  ],
  "what_went_well": ["...", "..."],
  "mistakes": ["...", "..."],
  "improved_answer": "...",
  "next_steps": ["...", "..."],
  "coach_summary": "..."
}}
All scores must be integers from 0 to 10. overall_score must be the average of
the four criterion scores, rounded to the nearest whole number. Keep feedback
respectful and practical. If the answer lacks details, say what details are
missing; do not invent candidate experience. The improved answer is a template
the candidate should personalize, not a claim that they did things they did not do.
For behavioral questions, mention STAR (Situation, Task, Action, Result) where useful.
Role: {role}
Candidate level: {level}
Interview question: {question}
Candidate answer: {answer}
"""
    data = extract_json(ask_gemini(client, prompt))
    criteria = data.get("criteria", [])
    if not isinstance(criteria, list) or not criteria:
        raise ValueError("Gemini returned feedback in an unexpected format.")
    for item in criteria:
        score = max(0, min(10, int(item.get("score", 0))))
        item["score"] = score
        item["max_score"] = 10
    data["overall_score"] = round(sum(x["score"] for x in criteria) / len(criteria))
    data.setdefault("what_went_well", [])
    data.setdefault("mistakes", [])
    data.setdefault("improved_answer", "")
    data.setdefault("next_steps", [])
    data.setdefault("coach_summary", "")
    return data


def show_bullets(items, empty_message="No items provided."):
    if items:
        for item in items:
            st.markdown(f"- {item}")
    else:
        st.caption(empty_message)


st.title("🎯 AI Interview Prep Coach")
st.write(
    "Practice interview questions, get actionable feedback, understand your "
    "mistakes, and track your score as you improve."
)
st.caption(f"Model: `{DEFAULT_MODEL}` · Powered by Google Gemini")

with st.sidebar:
    st.header("Interview setup")
    role = st.text_input("Target role", placeholder="e.g. Junior Python Developer")
    level = st.selectbox("Experience level", ["Beginner", "Intermediate", "Advanced"])
    interview_type = st.selectbox(
        "Interview type",
        ["Mixed", "Technical", "Behavioral", "HR / General", "Leadership"],
    )
    focus = st.text_input(
        "Focus areas (optional)", placeholder="e.g. Python, SQL, teamwork"
    )
    st.divider()
    st.markdown("**Scoring rubric**")
    st.caption("Relevance · Examples · Structure · Impact (each scored out of 10)")
    if st.button("Reset practice", use_container_width=True):
        for key in (
            "question_data", "question_history", "feedback_history",
            "current_answer", "last_feedback",
        ):
            st.session_state.pop(key, None)
        st.rerun()

if "question_history" not in st.session_state:
    st.session_state.question_history = []
if "feedback_history" not in st.session_state:
    st.session_state.feedback_history = []
if "question_data" not in st.session_state:
    st.session_state.question_data = None
if "last_feedback" not in st.session_state:
    st.session_state.last_feedback = None
if "current_answer" not in st.session_state:
    st.session_state.current_answer = ""

client = get_client()
if client is None:
    st.warning(
        "Gemini API key not found. Add `GEMINI_API_KEY` to your local "
        "environment or Streamlit secrets before generating questions."
    )
    st.code('GEMINI_API_KEY = "your-gemini-api-key"', language="toml")
    st.markdown(
        "For deployment, add this under **Streamlit Community Cloud → "
        "App → Settings → Secrets**. Never commit your real API key to GitHub."
    )

if not role.strip():
    st.info("Start by entering the target role in the sidebar.")
else:
    left, right = st.columns(2)
    with left:
        generate_clicked = st.button(
            "✨ Generate interview question",
            type="primary",
            use_container_width=True,
            disabled=client is None,
        )
    with right:
        st.metric("Questions practiced", len(st.session_state.feedback_history))

    if generate_clicked:
        with st.spinner("Preparing a question for your interview..."):
            try:
                data = make_question(
                    client, role.strip(), level, interview_type, focus.strip(),
                    st.session_state.question_history,
                )
                st.session_state.question_data = data
                st.session_state.question_history.append(data["question"])
                st.session_state.current_answer = ""
                st.session_state.last_feedback = None
            except Exception as exc:
                st.error(f"Could not generate a question: {exc}")

    question_data = st.session_state.question_data
    if question_data:
        st.subheader("Your interview question")
        st.markdown(f"### {question_data['question']}")
        with st.expander("What this question is testing"):
            st.write(question_data.get("what_it_tests", ""))
        with st.expander("Tips before answering"):
            show_bullets(question_data.get("answer_tips", []))

        answer = st.text_area(
            "Your answer",
            key="current_answer",
            height=220,
            placeholder=(
                "Write the answer as if you were speaking to an interviewer. "
                "For behavioral questions, explain the situation, your action, "
                "and the result."
            ),
        )
        evaluate_clicked = st.button(
            "🧠 Review my answer",
            use_container_width=True,
            disabled=client is None or not answer.strip(),
        )
        if evaluate_clicked:
            with st.spinner("Reviewing your answer and preparing improvement tips..."):
                try:
                    feedback = review_answer(
                        client, role.strip(), level,
                        question_data["question"], answer.strip(),
                    )
                    st.session_state.last_feedback = feedback
                    st.session_state.feedback_history.append(
                        {
                            "question": question_data["question"],
                            "score": feedback["overall_score"],
                        }
                    )
                except Exception as exc:
                    st.error(f"Could not review your answer: {exc}")

    feedback = st.session_state.last_feedback
    if feedback:
        st.divider()
        st.subheader("Your feedback")
        score = int(feedback.get("overall_score", 0))
        st.metric("Overall answer score", f"{score}/10")
        st.progress(max(0, min(100, score * 10)))
        st.write(feedback.get("coach_summary", ""))

        st.markdown("#### Score breakdown")
        for item in feedback.get("criteria", []):
            name = item.get("name", "Criterion")
            criterion_score = int(item.get("score", 0))
            st.write(f"**{name}: {criterion_score}/10**")
            st.progress(max(0, min(100, criterion_score * 10)))
            st.caption(item.get("comment", ""))

        good_col, improve_col = st.columns(2)
        with good_col:
            st.markdown("#### What went well")
            show_bullets(feedback.get("what_went_well", []))
        with improve_col:
            st.markdown("#### Mistakes / gaps to fix")
            show_bullets(feedback.get("mistakes", []))

        st.markdown("#### Example of a stronger answer")
        st.info(
            feedback.get("improved_answer", "")
            + "\n\nPersonalize this example so it accurately reflects your own "
            "experience; do not claim experience you do not have."
        )
        st.markdown("#### Your next steps")
        show_bullets(feedback.get("next_steps", []))

    if st.session_state.feedback_history:
        st.divider()
        st.subheader("Practice progress")
        scores = [item["score"] for item in st.session_state.feedback_history]
        st.write("Scores from reviewed answers:")
        st.line_chart(
            {"Answer score (/10)": scores},
            x_label="Practice attempt",
            y_label="Score",
        )
        st.caption(
            "Scores are AI-generated coaching estimates, not an official or "
            "scientifically validated assessment."
        )

st.divider()
st.caption(
    "Privacy tip: avoid entering passwords, government ID numbers, confidential "
    "employer information, or other sensitive personal data."
)
