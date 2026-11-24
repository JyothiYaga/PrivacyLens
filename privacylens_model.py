import pandas as pd
import mlflow
from mlflow.pyfunc import PythonModel
from mlflow.models import set_model
from mlflow.deployments import get_deploy_client
from retrieval import retrieve_context

LLM = "databricks-meta-llama-3-3-70b-instruct"

SYSTEM_PROMPT = """You are PrivacyLens, an educational assistant for India's DPDP Act 2023 and the EU GDPR.
Rules:
1. Answer ONLY using the context provided. Do not use outside knowledge.
2. Cite every claim with its source in square brackets, exactly as labelled in the context, e.g. [GDPR Article 17] or [DPDP Section 12].
3. If the context does not contain the answer, reply exactly: "I could not find this in the GDPR or DPDP Act text provided."
4. When both laws are relevant, explain each and note key differences.
5. Keep the answer under 200 words. This is not legal advice."""

def short_cite(h):
    if h["section_num"] == "Schedule":
        return f"{h['law']} Schedule"
    unit = "Article" if h["law"] == "GDPR" else "Section"
    return f"{h['law']} {unit} {h['section_num']}"

def build_context(hits):
    return "\n\n---\n\n".join(f"[{short_cite(h)}]\n{h['chunk_text']}" for h in hits)

@mlflow.trace(span_type="RETRIEVER")
def traced_retrieve(question, law=None):
    return retrieve_context(question, law)

class PrivacyLensModel(PythonModel):
    def load_context(self, context):
        self.deploy = get_deploy_client("databricks")

    @mlflow.trace(span_type="LLM")
    def _call_llm(self, messages):
        resp = self.deploy.predict(endpoint=LLM, inputs={
            "messages": messages, "max_tokens": 600, "temperature": 0,
        })
        return resp["choices"][0]["message"]["content"]

    @mlflow.trace(span_type="CHAIN")
    def predict(self, context, model_input, params=None):
        # Accept a dict or a DataFrame; always work with one row per question
        if isinstance(model_input, dict):
            model_input = pd.DataFrame(model_input)
        records = model_input.to_dict("records")

        outputs = []
        for r in records:
            question = r["question"]
            law = r.get("law")
            law = law if isinstance(law, str) and law else None
            hits = traced_retrieve(question, law)
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Context:\n{build_context(hits)}\n\nQuestion: {question}"},
            ]
            outputs.append({
                "answer": self._call_llm(messages),
                "sources": "; ".join(sorted({short_cite(h) for h in hits})),
            })
        return pd.DataFrame(outputs)

set_model(PrivacyLensModel())