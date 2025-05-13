# import streamlit as st
# import json
# import pandas as pd

# # 1. Load questions once at startup
# @st.cache_data
# def load_questions(path="dataset/llama_questions_rate5_axolotl_format_10_questions.jsonl"):
#     questions = []
#     with open(path, "r", encoding="utf-8") as f:
#         for line in f:
#             line = line.strip()
#             if not line:
#                 continue
#             questions.append(json.loads(line))
#     return questions

# questions = load_questions()

# # 2. Initialize page state
# if "page_idx" not in st.session_state:
#     st.session_state.page_idx = 0
# total = len(questions)

# # 3. Navigation buttons
# col1, col2, col3 = st.columns([1,6,1])
# with col1:
#     if st.button("Previous") and st.session_state.page_idx > 0:
#         st.session_state.page_idx -= 1
# with col3:
#     if st.button("Next") and st.session_state.page_idx < total - 1:
#         st.session_state.page_idx += 1

# # 4. Show current question
# q = questions[st.session_state.page_idx]
# st.header(f"Question {st.session_state.page_idx + 1} of {total}")
# st.write(f"**Q:** {q['question']}")
# for choice in q["choices"]:
#     st.write(f"- {choice}")
# st.write(f"**Answer:** {q['solution']}")

# # 5. Minimal review checklist
# st.subheader("Quick Review Checklist")
# # 5 key items:
# c1 = st.checkbox("1. Factual accuracy (evidence-based)", key=f"{st.session_state.page_idx}_c1")
# c2 = st.checkbox("2. Clear, unambiguous stem", key=f"{st.session_state.page_idx}_c2")
# c3 = st.checkbox("3. Plausible distractors", key=f"{st.session_state.page_idx}_c3")
# c4 = st.checkbox("4. Appropriate cognitive level", key=f"{st.session_state.page_idx}_c4")
# comments = st.text_area("General comments (optional)", key=f"{st.session_state.page_idx}_comments")

# # 6. Save or display current page’s review
# if st.button("Save Review for This Question"):
#     record = {
#         "index": st.session_state.page_idx,
#         "question": q["question"],
#         "accuracy": c1,
#         "clarity": c2,
#         "distractors": c3,
#         "cognitive_level": c4,
#         "comments": comments
#     }
#     # Append to session list
#     if "reviews" not in st.session_state:
#         st.session_state.reviews = []
#     st.session_state.reviews.append(record)
#     st.success("Review saved!")

# # 7. At the end, allow download of all reviews
# if st.session_state.page_idx == total - 1 and "reviews" in st.session_state:
#     df = pd.DataFrame(st.session_state.reviews)
#     csv = df.to_csv(index=False).encode("utf-8")
#     st.download_button(
#         "Download All Reviews as CSV",
#         data=csv,
#         file_name="mcq_reviews.csv",
#         mime="text/csv"
#     )

import streamlit as st
import json
import pandas as pd

# 1. Load questions once at startup
@st.cache_data
def load_questions(path="fetal_questions_to_review_by_doctor.json"):
    with open(path, "r", encoding="utf-8") as f:
        questions = json.load(f)
    return questions

questions = load_questions()

# 2. Initialize session state
if "page_idx" not in st.session_state:
    st.session_state.page_idx = 0
if "reviews" not in st.session_state:
    st.session_state.reviews = []

total = len(questions)

# Function to save the current review
def save_current_review():
    idx = st.session_state.page_idx
    q = questions[idx]
    record = {
        "index": idx,
        "question": q["question"],
        "accuracy": st.session_state.get(f"{idx}_c1", False),
        "clarity": st.session_state.get(f"{idx}_c2", False),
        "distractors": st.session_state.get(f"{idx}_c3", False),
        "cognitive_level": st.session_state.get(f"{idx}_c4", False),
        "comments": st.session_state.get(f"{idx}_comments", "")
    }

    # Replace or append record
    updated = False
    for i, r in enumerate(st.session_state.reviews):
        if r["index"] == idx:
            st.session_state.reviews[i] = record
            updated = True
            break
    if not updated:
        st.session_state.reviews.append(record)

# 3. Navigation buttons
col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    if st.button("Previous") and st.session_state.page_idx > 0:
        save_current_review()
        st.session_state.page_idx -= 1
with col3:
    if st.button("Next") and st.session_state.page_idx < total - 1:
        save_current_review()
        st.session_state.page_idx += 1

# 4. Display current question
q = questions[st.session_state.page_idx]
st.header(f"Question {st.session_state.page_idx + 1} of {total}")
st.write(f"**Q:** {q['question']}")
for key, text in q["options"].items():
    st.write(f"- **{key}**: {text}")
st.write(f"**Answer:** {q['answer']}")
#if "reference" in q:
#    st.markdown(f"**Reference:** {q['reference']}")

# 5. Minimal review checklist
st.subheader("Quick Review Checklist")
c1 = st.checkbox("1. Factual accuracy (evidence-based)", key=f"{st.session_state.page_idx}_c1")
c2 = st.checkbox("2. Clear, unambiguous stem", key=f"{st.session_state.page_idx}_c2")
c3 = st.checkbox("3. Plausible distractors", key=f"{st.session_state.page_idx}_c3")
c4 = st.checkbox("4. Appropriate cognitive level", key=f"{st.session_state.page_idx}_c4")
comments = st.text_area("General comments (optional)", key=f"{st.session_state.page_idx}_comments")

# # 6. Manual save button (optional)
# if st.button("Save Review for This Question"):
#     save_current_review()
#     st.success("Review saved manually!")

# 7. Download all reviews
if st.session_state.page_idx == total - 1 and st.session_state.reviews:
    save_current_review()  # Ensure latest page is saved
    df = pd.DataFrame(st.session_state.reviews)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download All Reviews as CSV",
        data=csv,
        file_name="mcq_reviews.csv",
        mime="text/csv"
    )
