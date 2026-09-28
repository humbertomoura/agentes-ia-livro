"""Testes do Cap. 42 (versão técnica), extraídos do livro."""
from tecnico.cap42_rag_runtime.runtime import *  # noqa: F401,F403
def build_demo_runtime(generator=None):
    chunks = [
        Chunk("c1", "policy-v2", "Production deploys require human approval.",
              {"tenant": "acme", "active": True, "kind": "policy"}),
        Chunk("c2", "runbook-auth",
              "Auth incidents: verify token expiry before rollback.",
              {"tenant": "acme", "active": True, "kind": "runbook"}),
        Chunk("c3", "other-tenant", "Production deploys can skip approval.",
              {"tenant": "other", "active": True, "kind": "policy"}),
    ]
    return RAGRuntime(HybridRetriever(chunks, HashEmbedder()), generator)

ACME = {"tenant": "acme", "active": True}

def test_tokenizer_strips_trailing_punctuation():
    assert tokens("human approval.") == ["human", "approval"]
    assert tokens("use text-embedding-3 v2.1") == [
        "use", "text-embedding-3", "v2.1"]

def test_ranking_and_isolation():
    result = build_demo_runtime().ask(
        "Does a production deploy need approval?", ACME)
    assert result["status"] == "RETRIEVED"
    assert result["evidence"][0]["source_id"] == "policy-v2"
    sources = {e["source_id"] for e in result["evidence"]}
    assert "other-tenant" not in sources

def test_irrelevant_question_abstains():
    result = build_demo_runtime().ask("What is the capital of France?", ACME)
    assert result["status"] == "INSUFFICIENT_EVIDENCE"

def test_empty_scope():
    result = build_demo_runtime().ask(
        "approval", {"tenant": "missing", "active": True})
    assert result["status"] == "INSUFFICIENT_EVIDENCE"

class FakeGenerator:
    def __init__(self, text):
        self.text = text
    def answer(self, question, evidence):
        return self.text

def test_citations_must_exist():
    ok = build_demo_runtime(FakeGenerator("Approval is required [E1]."))
    bad = build_demo_runtime(FakeGenerator("Approval is required [E9]."))
    assert ok.ask("deploy approval", ACME)["status"] == "SUCCESS"
    assert bad.ask("deploy approval", ACME)["status"] == "UNSUPPORTED_ANSWER"

def test_chunk_document():
    text = "Section A.\n\nSection B.\n\n" + "x" * 900
    parts = chunk_document("doc-1", text, {"tenant": "acme"})
    assert [c.chunk_id for c in parts] == ["doc-1#1", "doc-1#2", "doc-1#3"]
    assert all(len(c.text) <= 800 for c in parts)
    assert all(c.metadata["tenant"] == "acme" for c in parts)
def test_unauthorized_docs_do_not_change_bm25_scores():
    base = [
        Chunk("a", "p1", "approval approval deploy", {"tenant": "acme"}),
        Chunk("b", "p2", "approval runbook", {"tenant": "acme"}),
    ]
    noisy = base + [
        Chunk(f"x{i}", f"other-{i}", "approval " * 20, {"tenant": "other"})
        for i in range(100)
    ]
    base_scores = dict(BM25Index(base).search("approval", {0, 1}, k=2))
    noisy_scores = dict(BM25Index(noisy).search("approval", {0, 1}, k=2))
    assert base_scores.keys() == noisy_scores.keys()
    assert all(abs(base_scores[i] - noisy_scores[i]) < 1e-12
               for i in base_scores)
