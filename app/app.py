"""
PrivacyLens: Databricks App (Streamlit).

Flow: question -> serving endpoint (privacylens-api) -> cited answer
      -> saved to Lakebase (chat_messages) -> thumbs up/down saved to Lakebase (feedback).

Auth: the app's service principal. The serving endpoint and the Lakebase
database are added to the app as resources; Databricks injects the
connection settings (PGHOST, PGUSER, ...) and the SDK supplies OAuth tokens.
"""

import os
import time
import uuid

import psycopg
import streamlit as st
from databricks.sdk import WorkspaceClient

ENDPOINT = os.getenv("SERVING_ENDPOINT", "privacylens-api")
MODEL_VERSION = os.getenv("MODEL_VERSION", "2")

LAW_OPTIONS = {"Both laws": None, "GDPR only": "GDPR", "DPDP Act only": "DPDP"}

EXAMPLES = [
    "Can a user make a company delete their data?",
    "When must a personal data breach be reported?",
    "How do the two laws treat children's data?",
]

w = WorkspaceClient()


# ---------- Lakebase ----------

def db_connect():
    """Open a short-lived connection with a fresh OAuth token as the password."""
    return psycopg.connect(
        host=os.environ["PGHOST"],
        port=os.getenv("PGPORT", "5432"),
        dbname=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"],
        password=w.config.oauth_token().access_token,
        sslmode=os.getenv("PGSSLMODE", "require"),
    )


def save_message(session_id, question, law, answer, sources, latency_ms):
    with db_connect() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO chat_messages
                (session_id, question, law_filter, answer, sources, latency_ms, model_version)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (session_id, question, law, answer, sources, latency_ms, MODEL_VERSION),
        )
        return cur.fetchone()[0]


def save_feedback(message_id, rating):
    with db_connect() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO feedback (message_id, rating) VALUES (%s, %s)",
            (message_id, rating),
        )


# ---------- Model ----------

def ask(question, law):
    record = {"question": question}
    if law:
        record["law"] = law
    start = time.time()
    resp = w.serving_endpoints.query(name=ENDPOINT, dataframe_records=[record])
    latency_ms = int((time.time() - start) * 1000)
    pred = resp.predictions[0]
    return pred["answer"], pred["sources"], latency_ms


def handle_question(question, law):
    with st.spinner("Searching both laws and writing a cited answer..."):
        try:
            answer, sources, latency_ms = ask(question, law)
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"The answer service didn't respond ({type(e).__name__}). "
                           "If the app was idle, the service may be waking up; ask again in a minute.",
                "sources": "", "id": None,
            })
            return

    message_id = None
    try:
        message_id = save_message(st.session_state.session_id, question, law,
                                  answer, sources, latency_ms)
    except Exception as e:
        st.toast(f"Answer shown, but the chat couldn't be saved ({type(e).__name__}).")

    st.session_state.messages.append({
        "role": "assistant", "content": answer, "sources": sources,
        "id": message_id, "rated": None,
    })


# ---------- Page ----------

st.set_page_config(page_title="PrivacyLens", page_icon="⚖️", layout="centered")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())   # random; no user identity stored
    st.session_state.messages = []

st.title("PrivacyLens")
st.write(
    "Ask about India's DPDP Act 2023 and the EU GDPR. "
    "Every answer cites the article or section it comes from, so you can check it."
)
st.caption("Educational tool, not legal advice. Questions outside these two laws are declined.")

law_choice = st.radio("Search in", list(LAW_OPTIONS), horizontal=True)
law = LAW_OPTIONS[law_choice]

pending = None

if not st.session_state.messages:
    st.write("Try one of these:")
    for i, example in enumerate(EXAMPLES):
        if st.button(example, key=f"example_{i}"):
            pending = example

for i, m in enumerate(st.session_state.messages):
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m["role"] == "assistant" and m.get("sources"):
            st.caption("Sources retrieved: " + m["sources"])
        if m["role"] == "assistant" and m.get("id"):
            if m.get("rated") is None:
                up, down, _ = st.columns([1, 1, 6])
                if up.button("👍 Helpful", key=f"up_{i}"):
                    save_feedback(m["id"], 1)
                    m["rated"] = 1
                    st.rerun()
                if down.button("👎 Not helpful", key=f"down_{i}"):
                    save_feedback(m["id"], -1)
                    m["rated"] = -1
                    st.rerun()
            else:
                st.caption("Thanks, feedback saved.")

typed = st.chat_input("Ask a question about the GDPR or the DPDP Act")
question = typed or pending

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    handle_question(question, law)
    st.rerun()