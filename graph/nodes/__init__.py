"""
graph/nodes — Individual Pipeline Nodes

Each node is a function that:
1. Takes a state object
2. Processes it with specific logic
3. Updates and returns the state

Nodes:
  1. spell_check.py      - Auto-fix all typos
  2. tone_detect.py      - Detect user emotion
  3. topic_guard.py      - Filter off-topic questions
  4. retrieve.py         - FAISS semantic search
  5. grade_documents.py  - Relevance grading
  6. generate.py         - Answer generation
  7. web_search.py       - DuckDuckGo fallback
  8. grade_answer.py     - Hallucination check
  9. emotional.py        - Tone-aware response
"""
