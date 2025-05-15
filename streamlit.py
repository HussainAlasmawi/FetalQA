import json
import pandas as pd
import streamlit as st
import os
# ─── Constants ────────────────────────────────────────────────────────────

QUESTIONS_PATH = "code/fetal_questions_to_review_by_doctor.json"
if not os.path.isfile(QUESTIONS_PATH):
    QUESTIONS_PATH="fetal_questions_to_review_by_doctor.json"
CHECKLIST = [
    ("Factual accuracy", "accuracy"),
    ("Clear stem", "clarity"),
    ("Plausible distractors", "distractors"),
    ("Cognitive level", "cognitive_level"),
]

# ─── Data Loading ─────────────────────────────────────────────────────────

@st.cache_data
def load_questions(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return json.load(f)

questions = load_questions(QUESTIONS_PATH)
total_qs = len(questions)

# ─── Session State Setup ──────────────────────────────────────────────────

if "page_idx" not in st.session_state:
    st.session_state.page_idx = 0
if "reviews" not in st.session_state:
    st.session_state.reviews = {}

# ─── Helper Functions ─────────────────────────────────────────────────────

def get_current_question():
    return questions[st.session_state.page_idx]

def initialize_review_state(idx: int):
    """Initialize or restore the state for a question."""
    review = st.session_state.reviews.get(idx, {})
    for _, key in CHECKLIST:
        state_key = f"{idx}_{key}"
        st.session_state.setdefault(state_key, review.get(key, None))

    comments_key = f"{idx}_comments"
    st.session_state.setdefault(comments_key, review.get("comments", ""))

def save_review(idx: int):
    """Persist current answers into reviews dict."""
    st.session_state.reviews[idx] = {
        "index": idx,
        "question": questions[idx]["question"],
        **{key: st.session_state[f"{idx}_{key}"] for _, key in CHECKLIST},
        "comments": st.session_state[f"{idx}_comments"],
    }

def render_question(q: dict, idx: int):
    st.subheader(f"Question {idx + 1} of {total_qs}")
    st.write(q["question"])
    for opt_key, opt_text in q["options"].items():
        st.markdown(f"**{opt_key}.** {opt_text}")
    st.markdown(f"**Answer:** {q['answer']}")

def render_checklist(idx: int):
    st.markdown("---")
    st.write("### Quick Review Checklist")
    cols = st.columns(2)

    for i, (label, key) in enumerate(CHECKLIST):
        col = cols[i % 2]
        with col:
            st.radio(
                f"{i + 1}. {label}",
                options=[True, False],
                format_func=lambda x: "Yes" if x else "No",
                key=f"{idx}_{key}"
            )

    st.text_area(
        "Comments (optional)",
        key=f"{idx}_comments",
        height=80
    )

# ─── Navigation Callbacks ─────────────────────────────────────────────────

def go_next():
    idx = st.session_state.page_idx
    save_review(idx)
    if idx < total_qs - 1:
        st.session_state.page_idx += 1

def go_prev():
    idx = st.session_state.page_idx
    save_review(idx)
    if idx > 0:
        st.session_state.page_idx -= 1

# ─── Main Application ─────────────────────────────────────────────────────

idx = st.session_state.page_idx
initialize_review_state(idx)  # <-- FIXED: initialize BEFORE rendering widgets

current_question = get_current_question()
render_question(current_question, idx)
render_checklist(idx)

# ─── Navigation Buttons ───────────────────────────────────────────────────

col1, _, col3 = st.columns([1, 2, 1])
with col1:
    st.button("⬅ Previous", on_click=go_prev, disabled=(idx == 0))
with col3:
    st.button("Next ➡", on_click=go_next, disabled=(idx == total_qs - 1))

# ─── Download CSV on Last Question ────────────────────────────────────────

if idx == total_qs - 1 and st.session_state.reviews:
    save_review(idx)
    df = pd.DataFrame(st.session_state.reviews.values())
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download All Reviews as CSV",
        data=csv,
        file_name="mcq_reviews.csv",
        mime="text/csv"
    )
