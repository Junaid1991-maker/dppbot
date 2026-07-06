import os
import json
import bleach
from typing import TypedDict, List
from dotenv import load_dotenv
import anthropic
import chromadb
from chromadb.utils import embedding_functions
from langgraph.graph import StateGraph, END
import streamlit as st

load_dotenv("dppbot/.env")
api_key = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=api_key)

chroma_client = chromadb.PersistentClient(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "dppbot", "chromadb_sto
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection_names = ["certifications-guide", "espr-regulation", "pakistan-exporter-guide", "product-specific", "reach-requirements", "zdhc-guide"]
collections = {}
for name in collection_names:
    collections[name] = chroma_client.get_collection(name=name, embedding_function=embedding_function)

class DPPBotState(TypedDict):
    query: str
    clean_query: str
    query_category: str
    product_type: str
    retrieved_chunks: List[str]
    compliance_gaps: List[str]
    action_plan: dict
    compliance_score: int
    show_calendly: bool
    final_answer: str

def node_query_classifier(state):
    clean = bleach.clean(state["query"], strip=True)[:500]
    valid_categories = ["WHAT_IS_DPP", "PRODUCT_SPECIFIC", "CERTIFICATION_QUERY", "TIMELINE_QUERY", "SUPPLIER_QUERY", "CHEMICAL_QUERY", "CARBON_QUERY", "ACTION_PLAN", "CONSULTATION"]
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=20,
        messages=[{"role": "user", "content": f"Classify into one category: {clean}\nCategories: {valid_categories}\nRespond with category name only."}]
    )
    category = response.content[0].text.strip()
    if category not in valid_categories:
        category = "WHAT_IS_DPP"
    state["clean_query"] = clean
    state["query_category"] = category
    return state

def node_product_detector(state):
    clean = state["clean_query"]
    valid_products = ["denim", "knitwear", "home_textiles", "garments", "towels", "general"]
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=10,
        messages=[{"role": "user", "content": f"Identify textile product in: {clean}\nOptions: {valid_products}\nOne word only."}]
    )
    product = response.content[0].text.strip().lower()
    if product not in valid_products:
        product = "general"
    state["product_type"] = product
    return state

def node_rag_retriever(state):
    clean = state["clean_query"]
    all_chunks = []
    for name, collection in collections.items():
        results = collection.query(query_texts=[clean], n_results=min(2, collection.count()))
        if results['documents'][0]:
            all_chunks.extend(results['documents'][0])
    state["retrieved_chunks"] = all_chunks
    return state

def node_gap_analyser(state):
    query_lower = state["clean_query"].lower()
    all_certs = ["oeko-tex", "zdhc", "gots", "grs", "iso 14001", "bluesign", "sa8000"]
    missing = [cert for cert in all_certs if cert not in query_lower]
    state["compliance_gaps"] = missing
    return state

def node_action_plan_generator(state):
    plan = {
        "phase1": "Get REACH testing at SGS Pakistan or Bureau Veritas",
        "phase2": "Apply for OEKO-TEX certification",
        "phase3": "Register with ZDHC gateway",
        "phase4": f"Get product specific certification for {state['product_type']}",
        "estimated_cost_pkr": "300,000 to 600,000",
        "timeline_months": "6 to 12"
    }
    state["action_plan"] = plan
    return state

def node_compliance_scorer(state):
    score = 0
    query_lower = state["clean_query"].lower()
    scoring_map = {"oeko-tex": 20, "oekotex": 20, "zdhc": 20, "bluesign": 15, "iso 14001": 15, "grs": 10, "gots": 10, "sa8000": 10}
    for keyword, points in scoring_map.items():
        if keyword in query_lower:
            score += points
    state["compliance_score"] = min(score, 100)
    return state

def node_consultation_trigger(state):
    state["show_calendly"] = state["compliance_score"] < 60
    return state

def node_final_answer(state):
    context = "\n\n".join(state["retrieved_chunks"])
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        messages=[{"role": "user", "content": f"""You are DPPBot, EU DPP compliance expert for Pakistani textile exporters.
Context: {context}
Product: {state['product_type']}
Question: {state['clean_query']}
Give practical answer with specific steps."""}]
    )
    answer = response.content[0].text
    if state["show_calendly"]:
        answer += "\n\n📅 Book a free consultation: https://calendly.com/your-link/dpp-assessment"
    state["final_answer"] = answer
    return state

graph = StateGraph(DPPBotState)
graph.add_node("classify", node_query_classifier)
graph.add_node("detect", node_product_detector)
graph.add_node("retrieve", node_rag_retriever)
graph.add_node("gap_analyse", node_gap_analyser)
graph.add_node("plan", node_action_plan_generator)
graph.add_node("score", node_compliance_scorer)
graph.add_node("consult", node_consultation_trigger)
graph.add_node("answer", node_final_answer)
graph.set_entry_point("classify")
graph.add_edge("classify", "detect")
graph.add_edge("detect", "retrieve")
graph.add_edge("retrieve", "gap_analyse")
graph.add_edge("gap_analyse", "plan")
graph.add_edge("plan", "score")
graph.add_edge("score", "consult")
graph.add_edge("consult", "answer")
graph.add_edge("answer", END)
app = graph.compile()

def run_dppbot(query):
    initial_state = DPPBotState(
        query=query, clean_query="", query_category="", product_type="",
        retrieved_chunks=[], compliance_gaps=[], action_plan={},
        compliance_score=0, show_calendly=False, final_answer=""
    )
    return app.invoke(initial_state)

st.set_page_config(page_title="DPPBot", page_icon="🤖", layout="wide")
st.title("🤖 DPPBot — EU Digital Product Passport Compliance Agent")
st.caption("Helping Pakistani textile exporters comply with EU DPP regulations")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 Ask DPPBot")
    
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    query = st.chat_input("Ask about EU DPP compliance...")
    
    if query:
        st.session_state.chat_history.append({"role": "user", "content": query})
        
        with st.spinner("DPPBot is thinking..."):
            result = run_dppbot(query)
        
        st.session_state.chat_history.append({"role": "assistant", "content": result["final_answer"]})
        st.session_state.last_result = result
        st.rerun()

with col2:
    st.subheader("📊 Compliance Dashboard")
    
    if "last_result" in st.session_state:
        result = st.session_state.last_result
        score = result["compliance_score"]
        
        st.metric("Compliance Score", f"{score}/100")
        st.progress(score / 100)
        
        if score < 30:
            st.error("🔴 NOT READY")
        elif score < 60:
            st.warning("🟡 PARTIAL")
        elif score < 80:
            st.info("🔵 MOSTLY READY")
        else:
            st.success("🟢 COMPLIANT")
        
        st.write(f"**Category:** {result['query_category']}")
        st.write(f"**Product:** {result['product_type']}")
        
        st.subheader("📋 Action Plan")
        plan = result["action_plan"]
        st.write(f"1. {plan.get('phase1', '')}")
        st.write(f"2. {plan.get('phase2', '')}")
        st.write(f"3. {plan.get('phase3', '')}")
        st.write(f"4. {plan.get('phase4', '')}")
        st.write(f"**Cost:** {plan.get('estimated_cost_pkr', '')} PKR")
        st.write(f"**Timeline:** {plan.get('timeline_months', '')} months")
    else:
        st.info("Ask a question to see your compliance dashboard")