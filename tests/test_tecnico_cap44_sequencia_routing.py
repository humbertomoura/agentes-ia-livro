"""Cap. 44 — os trechos do livro são fragmentos; aqui eles rodam contra stubs."""
from types import SimpleNamespace as NS
import pytest
LABEL = {}
def classify_intent(text): return LABEL.get(text, "???")
def route(ticket):
    if ticket.amount_cents > 100_000:
        return "human_finance"
    label = classify_intent(ticket.text)  # structured output
    return {
        "billing": "billing_flow",
        "technical": "support_flow",
        "general": "faq_flow",
    }.get(label, "human_triage")

@pytest.mark.parametrize("amount,text,label,exp",[
 (100_001,"x","billing","human_finance"),   # regra de alto impacto ignora o label
 (100_000,"x","billing","billing_flow"),    # fronteira exata
 (0,"y","technical","support_flow"),
 (0,"z","general","faq_flow"),
 (0,"w","refund_now","human_triage"),       # label fora do enum
 (0,"v",None,"human_triage"),
])
def test_route(amount,text,label,exp):
    LABEL.clear(); LABEL[text]=label
    assert route(NS(amount_cents=amount,text=text))==exp

class ValidationError(Exception): pass
calls=[]
def extract_fields(r): calls.append("extract"); return r
def validate(e):
    calls.append("validate")
    if not e.get("ok"): raise ValidationError
def generate_draft(e): calls.append("draft"); return e
def verify_draft(d): calls.append("verify"); return d
def publish_if_allowed(c): calls.append("publish"); return "published"
def run_pipeline(request):
    extracted = extract_fields(request)
    validate(extracted)  # raises: the pipeline stops here
    draft = generate_draft(extracted)
    checked = verify_draft(draft)
    return publish_if_allowed(checked)
def test_pipeline_stops_on_invalid():
    calls.clear()
    with pytest.raises(ValidationError): run_pipeline({"ok":False})
    assert calls==["extract","validate"]
def test_pipeline_happy():
    calls.clear(); assert run_pipeline({"ok":True})=="published"
