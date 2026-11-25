import mlflow
import pandas as pd
from mlflow.pyfunc import PythonModel
from mlflow.models import set_model
from mlflow.deployments import get_deploy_client
from retrieval import retrieve_context

LLM = "databricks-meta-llama-3-3-70b-instruct"

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
        # The prompt text is pinned into the model when it is logged
        self.system_prompt = context.model_config["system_prompt"]

    @mlflow.trace(span_type="LLM")
    def _call_llm(self, messages):
        resp = self.deploy.predict(endpoint=LLM, inputs={
            "messages": messages, "max_tokens": 600, "temperature": 0,
        })
        return resp["choices"][0]["message"]["content"]

    @mlflow.trace(span_type="CHAIN")
    def predict(self, context, model_input, params=None):
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
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Context:\n{build_context(hits)}\n\nQuestion: {question}"},
            ]
            outputs.append({
                "answer": self._call_llm(messages),
                "sources": "; ".join(sorted({short_cite(h) for h in hits})),
            })
        return pd.DataFrame(outputs)

set_model(PrivacyLensModel())