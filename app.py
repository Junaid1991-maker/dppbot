import os
import streamlit as st
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# ── Compliance scoring ───────────────────────────────────────────
def score_compliance(text: str) -> int:
    text_lower = text.lower()
    score = 0
    certs = {
        "oeko-tex": 20, "zdhc": 20, "bluesign": 15,
        "iso 14001": 15, "grs": 10, "gots": 10, "sa8000": 10,
    }
    for cert, pts in certs.items():
        if cert in text_lower:
            score += pts
    return min(score, 100)

def score_label(score: int) -> str:
    if score <= 30:  return "🔴 NOT READY"
    if score <= 60:  return "🟡 PARTIAL"
    if score <= 80:  return "🟠 MOSTLY READY"
    return "🟢 COMPLIANT"

# ── Query classifier ─────────────────────────────────────────────
def classify_query(query: str) -> tuple:
    q = query.lower()
    cat = "GENERAL"
    if any(w in q for w in ["what is", "explain", "define"]):         cat = "WHAT_IS_DPP"
    elif any(w in q for w in ["certif", "oeko", "gots", "grs"]):      cat = "CERTIFICATION_QUERY"
    elif any(w in q for w in ["gap", "missing", "need"]):             cat = "GAP_ANALYSIS"
    elif any(w in q for w in ["action", "plan", "step", "phase"]):    cat = "ACTION_PLAN"
    elif any(w in q for w in ["cost", "price", "pkr", "fee"]):        cat = "COST_QUERY"
    elif any(w in q for w in ["denim", "knitwear", "towel", "garment"]): cat = "PRODUCT_SPECIFIC"
    elif any(w in q for w in ["score", "ready", "compliant"]):        cat = "COMPLIANCE_SCORE"

    product = "general"
    for p in ["denim", "knitwear", "towels", "garments", "home textiles"]:
        if p in q:
            product = p
            break

    return cat, product

# ── Action plan ──────────────────────────────────────────────────
ACTION_PLAN = {
    "phase1": "Immediate: Get ZDHC MRSL Level 1 certification (3-6 months, PKR 150,000–300,000)",
    "phase2": "Short-term: Obtain OEKO-TEX Standard 100 (4-8 months, PKR 200,000–400,000)",
    "phase3": "Medium-term: ISO 14001 Environmental Management (6-12 months, PKR 300,000–500,000)",
    "phase4": "Long-term: Full DPP data system implementation (12-18 months, PKR 500,000–1,000,000)",
}

# ── Main pipeline ────────────────────────────────────────────────
def run_pipeline(query: str, chat_history: list) -> dict:
    cat, product = classify_query(query)
    score = score_compliance(query)
    show_calendly = score < 60

    system_prompt = """You are DPPBot, an expert AI compliance assistant for Pakistani textile exporters preparing for EU Digital Product Passport (DPP) regulations.

KEY FACTS YOU KNOW:
- EU DPP mandatory for all textiles by 2027 (ESPR regulation Article 7)
- Non-compliance = banned from EU market (Pakistan exports $1.2B textiles to EU annually)
- Key certifications: OEKO-TEX Standard 100 (PKR 200,000-400,000), ZDHC MRSL (PKR 150,000-300,000), GOTS (PKR 250,000-450,000), GRS, Bluesign, ISO 14001, SA8000
- Pakistan labs: PCSIR Karachi, Intertek Karachi, SGS Pakistan, Bureau Veritas
- GSP Plus status means Pakistan already has preferential EU access — DPP compliance protects it
- Common Pakistani exporter mistakes: no chemical tracking, no supply chain traceability, no digital data systems
- REACH regulation: 197 SVHC substances banned, testing costs PKR 50,000-150,000 per product
- ZDHC levels: Level 1 (basic, 3-6 months), Level 2 (intermediate), Level 3 (advanced)
- DPP data must include: material composition, certifications, carbon footprint, repairability, recycling info

RESPONSE RULES:
- Be specific, practical, give PKR costs
- Reference Pakistani context (Karachi labs, GSP Plus, local costs)
- Structure action plans in 4 phases
- Always mention 2027 deadline
- Keep responses under 350 words
- Be encouraging — this is achievable for Pakistani exporters"""

    messages = chat_history + [{"role": "user", "content": query}]

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        system=system_prompt,
        messages=messages,
    )

    return {
        "query_category": cat,
        "product_type": product,
        "compliance_score": score,
        "action_plan": ACTION_PLAN,
        "show_calendly": show_calendly,
        "final_answer": response.content[0].text,
    }

# ── Streamlit UI ─────────────────────────────────────────────────
st.set_page_config(page_title="DPPBot", page_icon="🧵", layout="wide")
st.title("🧵 DPPBot — EU DPP Compliance Agent")
st.caption("Helping Pakistani textile exporters comply with EU Digital Product Passport regulations by 2027")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("💬 Ask a Compliance Question")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    query = st.chat_input("e.g. What certifications do I need for denim exports to EU?")
    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.write(query)
        with st.chat_message("assistant"):
            with st.spinner("Analysing compliance requirements..."):
                history = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages[:-1]
                ]
                result = run_pipeline(query, history)
                st.session_state.last_result = result
                st.write(result["final_answer"])
        st.session_state.messages.append(
            {"role": "assistant", "content": result["final_answer"]}
        )

with col2:
    st.subheader("📊 Compliance Dashboard")
    if st.session_state.last_result:
        r = st.session_state.last_result
        score = r["compliance_score"]
        st.metric("Compliance Score", f"{score}/100")
        st.progress(score / 100)
        st.write(score_label(score))
        st.divider()
        st.write(f"**Query Category:** {r['query_category']}")
        st.write(f"**Product Type:** {r['product_type'].title()}")
        st.divider()
        st.subheader("📋 4-Phase Action Plan")
        plan = r["action_plan"]
        st.info(f"**Phase 1:** {plan['phase1']}")
        st.warning(f"**Phase 2:** {plan['phase2']}")
        st.warning(f"**Phase 3:** {plan['phase3']}")
        st.error(f"**Phase 4:** {plan['phase4']}")
        if r["show_calendly"]:
            st.divider()
            st.warning("📅 Score below 60 — book a free DPP assessment:")
            st.link_button("Book Free Assessment", "https://calendly.com/junaid19tex/dpp-assessment")
    else:
        st.info("Ask a question to see your compliance score and action plan.")
        st.metric("Compliance Score", "—")
        st.progress(0)