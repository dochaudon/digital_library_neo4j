import json
import os

import requests


def is_llm_enabled():
    enabled = os.getenv("QA_ENABLE_LLM", "").strip().lower()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    return enabled in {"1", "true", "yes", "on"} and bool(api_key)


def extract_text_from_response(payload):
    output = payload.get("output", [])
    parts = []

    for item in output:
        for content in item.get("content", []):
            if content.get("type") == "output_text" and content.get("text"):
                parts.append(content["text"])

    if parts:
        return "\n".join(parts).strip()

    if payload.get("output_text"):
        return str(payload["output_text"]).strip()

    return ""


def create_responses_payload(model, instructions, input_text, text_format=None):
    payload = {
        "model": model,
        "instructions": instructions,
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": input_text,
                    }
                ],
            }
        ],
    }

    if text_format:
        payload["text"] = {"format": text_format}

    return payload


def send_responses_request(payload):
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")

    response = requests.post(
        f"{base_url}/responses",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def extract_json_from_response(payload):
    text = extract_text_from_response(payload)
    if not text:
        return None

    try:
        return json.loads(text)
    except Exception:
        return None


def build_llm_prompt(question, history, draft_answer, documents, facts):
    history_lines = []
    for item in (history or [])[-6:]:
        role = item.get("role", "user")
        content = (item.get("content") or "").strip()
        if content:
            history_lines.append(f"{role}: {content}")

    doc_lines = []
    for doc in (documents or [])[:5]:
        doc_lines.append(
            {
                "id": doc.get("id"),
                "title": doc.get("title"),
                "type": doc.get("type"),
                "year": doc.get("year"),
                "authors": doc.get("authors"),
                "publisher": doc.get("publisher"),
                "university": doc.get("university"),
            }
        )

    return (
        "Cau hoi nguoi dung:\n"
        f"{question}\n\n"
        "Lich su hoi dap gan day:\n"
        f"{chr(10).join(history_lines) if history_lines else '(khong co)'}\n\n"
        "Cau tra loi nhap duoc sinh tu du lieu:\n"
        f"{draft_answer}\n\n"
        "Du lieu xac thuc de duoc phep su dung:\n"
        f"{json.dumps({'documents': doc_lines, 'facts': facts}, ensure_ascii=False)}\n\n"
        "Yeu cau:\n"
        "- Tra loi bang tieng Viet tu nhien, ngan gon, ro rang.\n"
        "- Chi duoc dung thong tin trong phan du lieu xac thuc.\n"
        "- Neu du lieu khong du, hay noi ro la he thong chua co thong tin.\n"
        "- Khong duoc bịa them ten tac gia, nam, nha xuat ban, truong hay so lieu.\n"
        "- Neu co danh sach tai lieu lien quan thi co the nhac toi 1-3 tieu de tieu bieu.\n"
    )


def build_cypher_prompt(question, history, schema_context):
    history_lines = []

    for item in (history or [])[-6:]:
        role = item.get("role", "user")
        content = (item.get("content") or "").strip()
        docs = item.get("documents") or []
        doc_titles = [doc.get("title") for doc in docs if doc.get("title")]

        line = f"{role}: {content}"
        if doc_titles:
            line += f" | documents: {', '.join(doc_titles[:3])}"
        history_lines.append(line)

    return (
        "You generate safe read-only Cypher queries for a digital library graph.\n"
        "Use only the schema below.\n\n"
        f"{schema_context}\n\n"
        "Rules:\n"
        "- Generate one read-only Cypher query only.\n"
        "- Never use CREATE, MERGE, DELETE, SET, REMOVE, DROP, LOAD CSV, FOREACH, APOC, or dbms procedures.\n"
        "- Always include RETURN.\n"
        "- For listing queries, prefer LIMIT 10 unless the user asks for totals.\n"
        "- Use parameters instead of hardcoding user text whenever practical.\n"
        "- Return scalar fields, not raw Neo4j nodes or relationships.\n"
        "- If the query returns documents, prefer aliases: id, title, type, year, authors, publisher, university.\n"
        "- If the user asks something not answerable from the schema, set use_cypher=false.\n"
        "- If the question references a previously mentioned document, use the history context.\n\n"
        f"Conversation history:\n{chr(10).join(history_lines) if history_lines else '(none)'}\n\n"
        f"Current user question:\n{question}\n"
    )


def generate_cypher_plan(question, history, schema_context):
    if not is_llm_enabled():
        return None

    model = os.getenv("OPENAI_CYPHER_MODEL", "").strip() or "gpt-4o-mini"

    schema = {
        "type": "json_schema",
        "name": "qa_cypher_plan",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "use_cypher": {"type": "boolean"},
                "intent": {"type": "string"},
                "cypher": {"type": "string"},
                "params": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string"},
                            "value": {"type": "string"},
                        },
                        "required": ["key", "value"],
                        "additionalProperties": False,
                    },
                },
                "answer_hint": {"type": "string"},
            },
            "required": ["use_cypher", "intent", "cypher", "params", "answer_hint"],
            "additionalProperties": False,
        },
    }

    payload = create_responses_payload(
        model=model,
        instructions=(
            "You are a Cypher planner for a Neo4j-backed digital library. "
            "Return only valid structured data."
        ),
        input_text=build_cypher_prompt(question, history, schema_context),
        text_format=schema,
    )

    try:
        return extract_json_from_response(send_responses_request(payload))
    except Exception:
        return None


def rewrite_answer_with_llm(question, history, draft_answer, documents=None, facts=None):
    if not is_llm_enabled():
        return None

    model = os.getenv("OPENAI_MODEL", "").strip() or "gpt-4.1-mini"

    payload = create_responses_payload(
        model=model,
        instructions=(
            "Ban la tro ly hoi dap cho thu vien so. "
            "Nhiem vu la dien dat cau tra loi bang tieng Viet dua tren du lieu da cho, "
            "khong duoc suy doan them."
        ),
        input_text=build_llm_prompt(
            question=question,
            history=history,
            draft_answer=draft_answer,
            documents=documents or [],
            facts=facts or {},
        ),
        text_format={"type": "text"},
    )

    try:
        rewritten = extract_text_from_response(send_responses_request(payload))
        return rewritten or None
    except Exception:
        return None
