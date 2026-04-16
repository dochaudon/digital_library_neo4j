# 🤖 AI AGENTS RULES - DIGITAL LIBRARY SYSTEM

This file defines rules and constraints for AI agents (Codex) working on this project.

---

# 🏗️ PROJECT OVERVIEW

This is a Digital Library System with:

- Backend: Flask (Blueprint architecture)
- Database: Neo4j (Graph database)
- Search: Hybrid (NLP + Graph + Fulltext)
- Frontend: Jinja2 + Static CSS/JS

---

# 📁 PROJECT STRUCTURE

- routes/ → Flask routes (controllers)
- services/ → Business logic layer
- models/ → Database queries (Neo4j Cypher)
- templates/ → HTML (Jinja2)
- static/ → CSS, JS

---

# ⚙️ ARCHITECTURE RULES (STRICT)

## 1. LAYERED ARCHITECTURE

MUST follow:

routes → services → models

DO NOT:
- query database directly inside routes
- put business logic in templates
- duplicate logic across layers

---

## 2. DOCUMENT SYSTEM

All documents include:

- Book
- Article
- Thesis

Each document MUST have:
- id
- title
- year
- type

---

## 3. ROUTING RULES (CRITICAL)

Correct routes:

- Book → /book/<id>
- Article → /article/<id>
- Thesis → /thesis/<id>

DO NOT:
- use /document/<id>
- mix document types

---

## 4. SEARCH SYSTEM RULES (VERY IMPORTANT)

### Priority:

Graph Search > Fulltext Search

---

### Behavior:

IF filters exist:
→ MUST use graph search ONLY

IF no filters:
→ use fulltext search

---

### Filters include:

- doc_type
- author
- subject
- publisher
- university
- year

---

### NLP RULES:

- MUST normalize Vietnamese text
- MUST remove stopwords:
  - "nam"
  - "cua"
  - "tac gia"
  - "viet boi"

- MUST NOT create noisy subject filters

---

### YEAR RULE (CRITICAL):

Neo4j stores year as STRING

ALWAYS use:

```cypher
toInteger(d.year)