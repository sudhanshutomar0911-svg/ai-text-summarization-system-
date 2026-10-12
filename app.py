
import re
import math
from collections import Counter
import streamlit as st

st.set_page_config(
    page_title="AI Text Summarizer",
    page_icon="📝"
)

STOP_WORDS = set("""
a an the and or but if while with to from of in on at by for as
is are was were be been being it this that these those he she
they them we you your i my our their not do does did can could
should would may might will have has had also than then so
""".split())

def split_sentences(text):
    text = re.sub(r"\s+", " ", text).strip()
    return [
        s.strip() for s in
        re.split(r'(?<=[.!?])\s+', text) if s.strip()
    ]

def summarize(text, percent):
    sentences = split_sentences(text)

    if len(sentences) <= 1:
        return text

    words_by_sentence = [
        re.findall(r"\b[a-zA-Z0-9]+\b", s.lower())
        for s in sentences
    ]

    filtered = [
        [w for w in words if w not in STOP_WORDS]
        for words in words_by_sentence
    ]

    total_words = sum(len(words) for words in filtered)
    if total_words == 0:
        return sentences[0]

    counts = Counter(w for words in filtered for w in words)
    document_frequency = Counter(
        w for words in filtered for w in set(words)
    )

    scores = []
    for words in filtered:
        score = sum(
            (counts[w] / total_words) *
            (math.log((1 + len(sentences)) /
                      (1 + document_frequency[w])) + 1)
            for w in words
        )
        scores.append(score / math.sqrt(max(len(words), 1)))

    count = max(
        1, min(len(sentences),
               math.ceil(len(sentences) * percent / 100))
    )
    selected = set(
        sorted(range(len(sentences)),
               key=lambda i: scores[i], reverse=True)[:count]
    )

    return " ".join(
        s for i, s in enumerate(sentences) if i in selected
    )

st.title("AI-Based Text Summarization System")
st.write("Paste long text below to generate a shorter summary.")

text = st.text_area("Enter your text", height=250)
percent = st.slider("Summary size (%)", 10, 80, 30, 10)

if st.button("Summarize Text"):
    if not text.strip():
        st.warning("Please enter some text first.")
    else:
        result = summarize(text, percent)
        st.subheader("Generated Summary")
        st.write(result)

        original_words = len(text.split())
        summary_words = len(result.split())
        st.metric("Original words", original_words)
        st.metric("Summary words", summary_words)

        st.download_button(
            "Download Summary",
            result,
            file_name="summary.txt"
        )
