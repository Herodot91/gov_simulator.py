# app.py (enhanced)
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from copy import deepcopy
import json

st.set_page_config(page_title="Florești Metropole — CivicTech Simulator", layout="wide")

SCENARIOS = [
    {"title":"Decentralization of Customs & Border Police",
     "options":{"A":("Centralize for control", {"Governance":-5,"Risk":+5},10),
                "B":("Decentralize to regions", {"Governance":+10,"Stability":+5},20)},
     "intl":"EU encourages decentralization."},
    {"title":"Create Technical University in Bender",
     "options":{"A":("Skip investment", {"Economy":-5},0),
                "B":("IT faculty only", {"Economy":+5},15),
                "C":("Full technical university", {"Economy":+10,"Governance":+5},25)},
     "intl":"Russia warns against outside influence."},
    {"title":"Digital Justice & Procurement Reform",
     "options":{"A":("Delay reform", {"Governance":-5},0),
                "B":("Implement transparency tools", {"Governance":+10,"Risk":-5},15)},
     "intl":"EU praises Moldova’s rule of law improvement."},
    {"title":"Budget Allocation: Green Tech Factories",
     "options":{"A":("One per region", {"Economy":+5},20),
                "B":("Ignore sector", {"Economy":-5},0)},
     "intl":"UN welcomes clean tech expansion."},
    {"title":"Education: New Agricultural Universities",
     "options":{"A":("EU model in Taul, Karmanovo", {"Economy":+5,"Stability":+5},25),
                "B":("Keep colleges as-is", {"Economy":-5},0)},
     "intl":"Foreign students show interest in Moldova."},
]

BASE = {"Governance":50,"Economy":50,"Stability":50,"Risk":50}
def clamp(v): return max(0,min(100,v))

# ---------- UI ----------
st.title("Florești Metropole — CivicTech Simulator")
with st.sidebar:
    mode = st.radio("Mode", ["Democracy","Autocracy"], index=0)
    budget = st.slider("Starting Budget (units)", 0, 150, 100, 5)
    reset = st.button("Reset choices")

if reset:
    for i in range(len(SCENARIOS)):
        st.session_state.pop(f"sc{i+1}", None)

choices = []
with st.form("sim"):
    for i, s in enumerate(SCENARIOS, start=1):
        st.subheader(f"📘 Scenario {i}: {s['title']}")
        st.caption(s["intl"])
        # safer effect string (no weird nested quotes)
        def fmt_effects(eff): 
            return ", ".join([f"{kk} {('+' if vv>=0 else '')}{vv}" for kk,vv in eff.items()])
        opts = [f"{k}) {v[0]} — Cost {v[2]} | Effects: {fmt_effects(v[1])}"
                for k,v in s["options"].items()]
        pick = st.selectbox("Your Choice", ["(skip)"]+opts, key=f"sc{i}")
        choices.append(pick)
    run = st.form_submit_button("▶️ Run Simulation")

if run:
    scores = deepcopy(BASE); history=[]; logs=[]; last_intl=""
    start_budget_val = budget
    for s, label in zip(SCENARIOS, choices):
        if label == "(skip)":
            logs.append("Skipped (no choice)."); history.append(deepcopy(scores)); continue
        key = label.split(")")[0]
        if key not in s["options"]:
            logs.append("Invalid choice."); history.append(deepcopy(scores)); continue
        desc, effects, cost = s["options"][key]
        if budget < cost:
            logs.append(f"Not enough budget for {key}) {desc}. Skipped.")
            history.append(deepcopy(scores)); continue
        budget -= cost
        for k, dv in effects.items(): scores[k] = clamp(scores[k] + dv)
        last_intl = s["intl"]
        logs.append(f"{s['title']} | {key}) {desc} | Cost {cost} | Intl: {last_intl} | Scores {scores} | Budget {budget}")
        if mode=="Democracy":
            turnout = clamp(int(30 + 0.5 * scores["Stability"]))
            passed = (scores["Stability"] + scores["Governance"]) > 90
            logs.append(f"Vote: turnout {turnout}% → {'PASSED' if passed else 'FAILED'}")
        history.append(deepcopy(scores))

    df = pd.DataFrame(history, index=[f"S{i+1}" for i in range(len(history))])

    # Layout: left chart/log, right progress card
    left, right = st.columns([2,1], gap="large")

    with left:
        st.markdown(f"**Final Scores:** {scores}  |  **Budget Left:** {budget}")
        fig, ax = plt.subplots(figsize=(7,3))
        for col in df.columns: ax.plot(df.index, df[col], marker="o", label=col)
        ax.set_title("Score Evolution Over Scenarios"); ax.set_xlabel("Scenario"); ax.set_ylabel("Score (0–100)")
        ax.grid(True); ax.legend(); st.pyplot(fig)
        st.download_button("Download History CSV", df.to_csv().encode(), "history.csv", "text/csv")

        # JSON report
        report = {
            "mode": mode,
            "starting_budget": start_budget_val,
            "final_budget": budget,
            "final_scores": scores,
            "log": logs,
        }
        st.download_button("Download Report JSON", json.dumps(report, indent=2).encode(), "report.json", "application/json")

        st.text_area("Log", "\n".join(logs), height=220)

    # Citizen Progress Card (HTML)
    def risk_badge(val: int):
        if val <= 33:  return '<span style="padding:4px 10px;border-radius:999px;background:rgba(42,157,143,.1);border:1px solid rgba(42,157,143,.35);color:#156b5d;font-weight:700;font-size:12px;">LOW RISK</span>'
        if val <= 66:  return '<span style="padding:4px 10px;border-radius:999px;background:rgba(255,183,3,.1);border:1px solid rgba(255,183,3,.35);color:#7a5a00;font-weight:700;font-size:12px;">MEDIUM RISK</span>'
        return '<span style="padding:4px 10px;border-radius:999px;background:rgba(230,57,70,.1);border:1px solid rgba(230,57,70,.35);color:#8a1b23;font-weight:700;font-size:12px;">HIGH RISK</span>'

    def bar_html(value, color):
        return f'''
          <div style="height:10px;background:#e9eef5;border-radius:999px;overflow:hidden;">
            <div style="height:100%;width:{int(value)}%;background:{color};transition:width .35s ease;"></div>
          </div>
        '''

    with right:
        g,e,s,r = scores["Governance"], scores["Economy"], scores["Stability"], scores["Risk"]
        card_html = f"""
        <div style="background:linear-gradient(145deg,#0b1b2b 0%,#0a223a 100%);border:1px solid rgba(255,255,255,.08);border-radius:16px;padding:16px;color:#eaf4ff;box-shadow:0 8px 30px rgba(2,62,138,.18);">
          <h4 style="margin:0 0 8px 0;">Citizen Progress Card</h4>
          <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:6px;font-size:12px;">
            <div style="background:rgba(255,255,255,.06);padding:8px 10px;border-radius:10px;">Budget: <b>{budget}</b></div>
            <div style="background:rgba(255,255,255,.06);padding:8px 10px;border-radius:10px;">Governance: <b>{g}</b></div>
            <div style="background:rgba(255,255,255,.06);padding:8px 10px;border-radius:10px;">Economy: <b>{e}</b></div>
            <div style="background:rgba(255,255,255,.06);padding:8px 10px;border-radius:10px;">Stability: <b>{s}</b></div>
            <div style="background:rgba(255,255,255,.06);padding:8px 10px;border-radius:10px;">Risk: <b>{r}</b> {risk_badge(r)}</div>
          </div>
          <div style="margin-top:10px;font-size:12px;">Governance</div>
          {bar_html(g, '#4cc9f0')}
          <div style="margin-top:6px;font-size:12px;">Economy</div>
          {bar_html(e, '#48cae4')}
          <div style="margin-top:6px;font-size:12px;">Stability</div>
          {bar_html(s, '#90e0ef')}
          <div style="margin-top:6px;font-size:12px;">Risk</div>
          {bar_html(r, '#e63946')}
          <div style="margin-top:8px;font-size:12px;color:#bfd8ff;">🌐 Last Intl Reaction: {last_intl or '—'}</div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

