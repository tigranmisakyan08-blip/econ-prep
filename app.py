import streamlit as st

st.set_page_config(
    page_title="Economics Olympiad Prep",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

from openai import OpenAI
import os
import math
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
TEACHER_EMAIL = "tigran.misakyan08@gmail.com"

# --- Load CSS from file ---
css_path = Path(__file__).parent / "style.css"
st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# --- Questions ---
questions = [
    {"concept": "Supply and Demand", "question": "If the price of coffee increases, what happens to the demand for tea (a substitute)?", "options": ["Decreases", "Increases", "Stays the same", "Becomes zero"], "answer": "Increases"},
    {"concept": "Supply and Demand", "question": "A drought destroys wheat crops. What happens to the supply curve for bread?", "options": ["Shifts right", "Shifts left", "Stays the same", "Becomes elastic"], "answer": "Shifts left"},
    {"concept": "Elasticity", "question": "A 10% price increase causes a 5% drop in quantity demanded. This good is:", "options": ["Elastic", "Inelastic", "Unit elastic", "Perfectly elastic"], "answer": "Inelastic"},
    {"concept": "Elasticity", "question": "Which of the following goods is most likely to have elastic demand?", "options": ["Insulin", "Salt", "Luxury handbags", "Gasoline"], "answer": "Luxury handbags"},
    {"concept": "Market Structures", "question": "In a monopoly, the firm is a:", "options": ["Price taker", "Price maker", "Price follower", "Price competitor"], "answer": "Price maker"},
    {"concept": "Market Structures", "question": "Which market structure has the most firms and the least pricing power?", "options": ["Monopoly", "Oligopoly", "Perfect competition", "Monopolistic competition"], "answer": "Perfect competition"},
    {"concept": "Consumer Surplus", "question": "Consumer surplus is defined as:", "options": ["Price paid minus cost of production", "Willingness to pay minus price actually paid", "Total revenue minus total cost", "Marginal benefit minus marginal cost"], "answer": "Willingness to pay minus price actually paid"},
    {"concept": "Consumer Surplus", "question": "If the market price falls, consumer surplus:", "options": ["Decreases", "Increases", "Stays the same", "Becomes negative"], "answer": "Increases"},
    {"concept": "Fiscal Policy", "question": "An expansionary fiscal policy involves:", "options": ["Raising taxes and cutting spending", "Cutting taxes and increasing spending", "Raising interest rates", "Reducing money supply"], "answer": "Cutting taxes and increasing spending"},
    {"concept": "Fiscal Policy", "question": "Which of the following is an automatic stabilizer?", "options": ["A new infrastructure bill", "Unemployment benefits", "A tax reform law", "A military budget increase"], "answer": "Unemployment benefits"},
    {"concept": "Monetary Policy", "question": "When a central bank raises interest rates, borrowing becomes:", "options": ["Cheaper", "More expensive", "Free", "Unaffected"], "answer": "More expensive"},
    {"concept": "Monetary Policy", "question": "Quantitative easing is a tool used to:", "options": ["Increase interest rates", "Reduce inflation", "Increase money supply", "Reduce government debt"], "answer": "Increase money supply"},
    {"concept": "Comparative Advantage", "question": "Comparative advantage is based on:", "options": ["Absolute productivity", "Opportunity cost", "Total output", "Labor hours"], "answer": "Opportunity cost"},
    {"concept": "Comparative Advantage", "question": "If Country A can produce wine at lower opportunity cost than Country B, Country A should:", "options": ["Import wine", "Export wine", "Stop producing wine", "Tax wine imports"], "answer": "Export wine"},
    {"concept": "Market Failures", "question": "A negative externality occurs when:", "options": ["A firm earns too much profit", "Third parties bear costs not reflected in price", "Government intervenes in markets", "Consumers overpay for goods"], "answer": "Third parties bear costs not reflected in price"},
    {"concept": "Market Failures", "question": "Public goods are characterized by being:", "options": ["Excludable and rival", "Non-excludable and non-rival", "Excludable and non-rival", "Non-excludable and rival"], "answer": "Non-excludable and non-rival"},
    {"concept": "Game Theory", "question": "In a Prisoner's Dilemma, the Nash Equilibrium is:", "options": ["Both cooperate", "Both defect", "One cooperates one defects", "No equilibrium exists"], "answer": "Both defect"},
    {"concept": "Game Theory", "question": "A dominant strategy is one that:", "options": ["Depends on the opponent's move", "Is best regardless of opponent's move", "Always leads to cooperation", "Maximizes joint payoff"], "answer": "Is best regardless of opponent's move"},
    {"concept": "Behavioral Economics", "question": "Loss aversion means people:", "options": ["Prefer risk over safety", "Feel losses more strongly than equivalent gains", "Always make rational decisions", "Ignore sunk costs"], "answer": "Feel losses more strongly than equivalent gains"},
    {"concept": "Behavioral Economics", "question": "The anchoring effect occurs when people:", "options": ["Ignore initial information", "Rely too heavily on the first piece of information received", "Make decisions based on future expectations", "Prefer certain outcomes over uncertain ones"], "answer": "Rely too heavily on the first piece of information received"},
]


# --- Helpers ---
def send_email(subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_EMAIL
        msg["To"] = TEACHER_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception:
        return False


def build_diagnostic_report(name, grade, score, results):
    concept_errors = {}
    lines = ["DIAGNOSTIC TEST REPORT", "=" * 40, f"Student: {name}", f"Grade: {grade}", f"Score: {score}/20", "=" * 40, ""]
    for i, (q, correct) in enumerate(results):
        status = "Correct" if correct else "Wrong"
        lines.append(f"Q{i+1} ({q['concept']}): {q['question'][:70]}... - {status}")
        if not correct:
            concept_errors[q["concept"]] = concept_errors.get(q["concept"], 0) + 1
    lines += ["", "WEAK TOPICS RANKED BY ERROR COUNT:", "-" * 40]
    for rank, (concept, errors) in enumerate(sorted(concept_errors.items(), key=lambda x: x[1], reverse=True), 1):
        lines.append(f"{rank}. {concept} - {errors} error(s)")
    return "\n".join(lines)


def build_practice_report(name, practice_results):
    concept_errors = {}
    lines = ["PRACTICE SESSION REPORT", "=" * 40, f"Student: {name}", "=" * 40, ""]
    for i, (q, correct) in enumerate(practice_results):
        status = "Correct" if correct else "Wrong"
        lines.append(f"Q{i+1} ({q['concept']}): {q['question'][:70]}... - {status}")
        if not correct:
            concept_errors[q["concept"]] = concept_errors.get(q["concept"], 0) + 1
    if concept_errors:
        lines += ["", "TOPICS STILL NEEDING ATTENTION:", "-" * 40]
        for rank, (concept, errors) in enumerate(sorted(concept_errors.items(), key=lambda x: x[1], reverse=True), 1):
            lines.append(f"{rank}. {concept} - {errors} error(s)")
    else:
        lines += ["", "All practice problems answered correctly."]
    return "\n".join(lines)


def parse_practice_questions(raw_text):
    parsed = []
    current = {}
    for line in raw_text.split("\n"):
        line = line.strip()
        if not line:
            if current.get("question") and current.get("options") and current.get("answer"):
                parsed.append(current)
                current = {}
        elif line.startswith(("A)", "B)", "C)", "D)")):
            if "options" not in current:
                current["options"] = []
            current["options"].append(line[2:].strip())
        elif line.startswith("Answer:"):
            letter = line.replace("Answer:", "").strip()
            mapping = {"A": 0, "B": 1, "C": 2, "D": 3}
            if letter in mapping and "options" in current and len(current["options"]) > mapping[letter]:
                current["answer"] = current["options"][mapping[letter]]
        elif not current.get("question") and not line.startswith("Problem"):
            current["question"] = line
    if current.get("question") and current.get("options") and current.get("answer"):
        parsed.append(current)
    return parsed


def svg_score_ring(percentage, score_text, label="Score"):
    """Generate an SVG circular progress ring."""
    radius = 54
    circumference = 2 * math.pi * radius
    offset = circumference - (percentage / 100) * circumference
    if percentage >= 80:
        color = "#00C9A7"
    elif percentage >= 50:
        color = "#F59E0B"
    else:
        color = "#FC5A5A"
    return f"""
    <div class='score-ring-container'>
        <svg width="160" height="160" viewBox="0 0 120 120">
            <circle cx="60" cy="60" r="{radius}" fill="none" stroke="#E0E7EF" stroke-width="8"/>
            <circle cx="60" cy="60" r="{radius}" fill="none" stroke="{color}" stroke-width="8"
                    stroke-linecap="round" stroke-dasharray="{circumference}"
                    stroke-dashoffset="{offset}" transform="rotate(-90 60 60)"
                    style="transition: stroke-dashoffset 1.2s cubic-bezier(0.4, 0, 0.2, 1); animation: ringFill 1.2s cubic-bezier(0.4, 0, 0.2, 1) both;">
                <animate attributeName="stroke-dashoffset" from="{circumference}" to="{offset}" dur="1.2s"
                         calcMode="spline" keySplines="0.4 0 0.2 1" fill="freeze"/>
            </circle>
            <text x="60" y="54" text-anchor="middle" fill="#0F1B2D" font-family="Inter, sans-serif" font-size="22" font-weight="800">{score_text}</text>
            <text x="60" y="72" text-anchor="middle" fill="#6B7A8D" font-family="Inter, sans-serif" font-size="9" font-weight="500" letter-spacing="0.08em" text-transform="uppercase">{label}</text>
        </svg>
    </div>
    """


def confetti_html():
    """Generate CSS-only confetti animation."""
    colors = ["#00C9A7", "#00A88A", "#F59E0B", "#FC5A5A", "#6366F1", "#8B5CF6", "#EC4899", "#14B8A6"]
    pieces = ""
    for i in range(40):
        color = colors[i % len(colors)]
        left = (i * 2.5) % 100
        delay = (i * 0.08) % 2
        duration = 2.5 + (i % 3) * 0.5
        size = 6 + (i % 5) * 2
        shape = "border-radius: 50%;" if i % 3 == 0 else f"border-radius: 2px; width: {size}px; height: {size * 0.4}px;" if i % 3 == 1 else f"border-radius: 0; width: {size}px; height: {size}px;"
        pieces += f'<div class="confetti-piece" style="left:{left}%; background:{color}; {shape} animation-duration:{duration}s; animation-delay:{delay}s;"></div>'
    return f'<div class="confetti-container">{pieces}</div>'


# --- Session State ---
for key, default in [
    ("page", "login"), ("name", ""), ("grade", ""), ("answers", {}),
    ("results", []), ("score", 0), ("practice_questions", []),
    ("practice_index", 0), ("practice_checked", False),
    ("practice_answer", None), ("show_explanation", False),
    ("explanation_text", ""), ("practice_results", []),
    ("submitted", False), ("diagnostic_report_sent", False),
    ("practice_report_sent", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# =============================================
#  HERO BANNER (all pages)
# =============================================
st.markdown("""
<div class='hero'>
    <div class='hero-school'>PhysMath School &middot; Yerevan, Armenia</div>
    <div class='hero-title'>Economics Olympiad <span>Prep</span></div>
    <div class='hero-subtitle'>AI-powered adaptive learning &middot; Personalised to your weak areas</div>
    <div class='hero-badges'>
        <span class='nav-badge'>20 Questions</span>
        <span class='nav-badge'>10 Concepts</span>
        <span class='nav-badge'>AI Practice</span>
        <span class='nav-badge'>Live Reports</span>
    </div>
</div>
""", unsafe_allow_html=True)


# =============================================
#  PAGE: LOGIN
# =============================================
if st.session_state.page == "login":
    st.markdown("""
    <div class='content-card'>
        <div style='font-size:1.35rem; font-weight:700; color:#0F1B2D; margin-bottom:0.4em;'>Get Started</div>
        <div class='welcome-text'>This platform diagnoses your individual weaknesses across ten core economics concepts and generates AI-powered practice problems based on your results. Complete the diagnostic test honestly — the system works only if you do.</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        name = st.text_input("Full name", placeholder="Enter your full name")
    with col2:
        grade = st.selectbox("Grade", ["9", "10", "11", "12"])

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Begin Diagnostic Test  \u2192"):
        if name:
            st.session_state.name = name
            st.session_state.grade = grade
            st.session_state.page = "test"
            st.rerun()
        else:
            st.error("Please enter your full name before continuing.")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    st.markdown("""
    <div class='feature-grid'>
        <div class='feature-card'>
            <div class='feature-stat-value'>20</div>
            <div class='feature-stat-label'>Diagnostic Questions</div>
        </div>
        <div class='feature-card'>
            <div class='feature-stat-value'>10</div>
            <div class='feature-stat-label'>Core Concepts</div>
        </div>
        <div class='feature-card'>
            <div class='feature-stat-value'>AI</div>
            <div class='feature-stat-label'>Generated Practice</div>
        </div>
        <div class='feature-card'>
            <div class='feature-stat-value'>Live</div>
            <div class='feature-stat-label'>Teacher Reports</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# =============================================
#  PAGE: DIAGNOSTIC TEST
# =============================================
elif st.session_state.page == "test":
    answered_count = len(st.session_state.answers)

    st.markdown(f"""
    <div class='test-header'>
        <div class='test-header-left'>
            <h2>Diagnostic Test</h2>
            <p>Student: {st.session_state.name} &nbsp;&middot;&nbsp; Grade {st.session_state.grade}</p>
        </div>
        <div class='test-count-badge'>{answered_count} / 20 Answered</div>
    </div>
    """, unsafe_allow_html=True)

    st.progress(answered_count / 20)

    st.markdown("<p class='welcome-text'>Answer all 20 questions carefully. Your teacher will receive a full performance report upon submission.</p>", unsafe_allow_html=True)
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    for i, q in enumerate(questions):
        st.markdown(f"""
        <div class='question-card' style='animation-delay: {i * 0.03}s;'>
            <div class='concept-tag'>{q['concept']}</div>
            <div class='question-number'>Question {i+1} of 20</div>
            <div class='question-text'>{q['question']}</div>
        </div>
        """, unsafe_allow_html=True)
        answer = st.radio(f"Q{i+1}", q["options"], key=f"q{i}", index=None, label_visibility="collapsed")
        if answer is not None:
            st.session_state.answers[i] = answer
        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    unanswered = [i + 1 for i in range(len(questions)) if i not in st.session_state.answers]
    if unanswered:
        st.markdown(f"<div class='warning-box'>Please answer all questions before submitting. Unanswered: {', '.join(f'Q{n}' for n in unanswered)}</div>", unsafe_allow_html=True)

    if st.button("Submit Diagnostic Test  \u2192"):
        if unanswered:
            st.error("Please answer all questions before submitting.")
        else:
            results = []
            score = 0
            for i, q in enumerate(questions):
                correct = st.session_state.answers[i] == q["answer"]
                if correct:
                    score += 1
                results.append((q, correct))
            st.session_state.results = results
            st.session_state.score = score
            st.session_state.diagnostic_report_sent = False
            st.session_state.page = "results"
            st.rerun()


# =============================================
#  PAGE: RESULTS
# =============================================
elif st.session_state.page == "results":
    score = st.session_state.score
    wrong_count = 20 - score
    percentage = int((score / 20) * 100)

    # Send email once
    if not st.session_state.diagnostic_report_sent:
        report = build_diagnostic_report(st.session_state.name, st.session_state.grade, score, st.session_state.results)
        send_email(f"Diagnostic Report - {st.session_state.name} (Grade {st.session_state.grade})", report)
        st.session_state.diagnostic_report_sent = True

    # Confetti on perfect score
    if score == 20:
        st.markdown(confetti_html(), unsafe_allow_html=True)

    st.markdown(f"""
    <div style='font-size:1.4rem; font-weight:700; color:#0F1B2D; margin-bottom:0.3em; animation: fadeIn 0.4s ease-out;'>Your Results</div>
    <div style='font-size:0.88rem; color:#6B7A8D; margin-bottom:1em;'>Student: {st.session_state.name} &nbsp;&middot;&nbsp; Grade {st.session_state.grade}</div>
    """, unsafe_allow_html=True)

    # SVG Score Ring
    st.markdown(svg_score_ring(percentage, f"{score}/20", f"{percentage}% Accuracy"), unsafe_allow_html=True)

    st.markdown(f"""
    <div class='stat-row'>
        <div class='stat-card'><div class='stat-value' style='color:#00C9A7;'>{score}</div><div class='stat-label'>Correct</div></div>
        <div class='stat-card'><div class='stat-value' style='color:#FC5A5A;'>{wrong_count}</div><div class='stat-label'>Incorrect</div></div>
        <div class='stat-card'><div class='stat-value'>{percentage}%</div><div class='stat-label'>Accuracy</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>Question Breakdown</div>", unsafe_allow_html=True)

    wrong = []
    for i, (q, correct) in enumerate(st.session_state.results):
        if correct:
            st.success(f"Q{i+1} \u2014 {q['concept']}: Correct")
        else:
            st.error(f"Q{i+1} \u2014 {q['concept']}: Incorrect \u00b7 Correct answer: {q['answer']}")
            wrong.append(q)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    if wrong:
        concept_errors = {}
        for q in wrong:
            concept_errors[q["concept"]] = concept_errors.get(q["concept"], 0) + 1
        ranked = sorted(concept_errors.items(), key=lambda x: x[1], reverse=True)

        st.markdown("<div class='section-header'>Weak Areas Identified</div>", unsafe_allow_html=True)

        for rank, (concept, errors) in enumerate(ranked, 1):
            st.markdown(f"""
            <div class='weak-area-card' style='animation-delay: {rank * 0.1}s;'>
                <div class='weak-area-name'>{rank}. {concept}</div>
                <div class='weak-area-badge'>{errors} error(s)</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p class='welcome-text'>The AI will now generate personalised practice problems targeting each of your weak concepts.</p>", unsafe_allow_html=True)

        if st.button("Begin AI Practice Session  \u2192"):
            all_practice = []
            seen = []
            for q in wrong:
                if q["concept"] not in seen:
                    seen.append(q["concept"])
                    with st.spinner(f"Generating problems for {q['concept']}..."):
                        try:
                            message = client.chat.completions.create(
                                model="deepseek-chat",
                                max_tokens=1000,
                                messages=[{"role": "user", "content": f"Generate 2 multiple choice practice problems about {q['concept']} for an economics olympiad student. Format each as:\nProblem N\n[question text]\nA) option\nB) option\nC) option\nD) option\nAnswer: [letter]\n\nNo explanations. Separate with blank line."}],
                            )
                            parsed = parse_practice_questions(message.choices[0].message.content)
                            for p in parsed:
                                p["concept"] = q["concept"]
                            all_practice.extend(parsed)
                        except Exception as e:
                            st.error(f"Failed to generate problems for {q['concept']}. The AI service may be temporarily unavailable.")
            if all_practice:
                st.session_state.practice_questions = all_practice
                st.session_state.practice_index = 0
                st.session_state.practice_checked = False
                st.session_state.practice_answer = None
                st.session_state.show_explanation = False
                st.session_state.practice_results = []
                st.session_state.practice_report_sent = False
                st.session_state.page = "practice"
                st.rerun()
            else:
                st.error("Could not generate any practice problems. Please try again later.")
    else:
        st.success("Perfect score! No weak areas detected.")
        if st.button("Start New Session"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


# =============================================
#  PAGE: PRACTICE
# =============================================
elif st.session_state.page == "practice":
    pqs = st.session_state.practice_questions
    idx = st.session_state.practice_index

    if idx >= len(pqs):
        # --- Practice Complete ---
        correct_count = sum(1 for _, c in st.session_state.practice_results if c)
        total = len(pqs)
        pct = int((correct_count / total) * 100) if total > 0 else 0

        # Send email once
        if not st.session_state.practice_report_sent:
            report = build_practice_report(st.session_state.name, st.session_state.practice_results)
            send_email(f"Practice Report - {st.session_state.name} (Grade {st.session_state.grade})", report)
            st.session_state.practice_report_sent = True

        # Confetti on perfect practice
        if correct_count == total:
            st.markdown(confetti_html(), unsafe_allow_html=True)

        st.markdown("<div style='font-size:1.4rem; font-weight:700; color:#0F1B2D; margin-bottom:1em; animation: fadeIn 0.4s ease-out;'>Practice Complete</div>", unsafe_allow_html=True)

        # SVG Score Ring
        st.markdown(svg_score_ring(pct, f"{correct_count}/{total}", f"{pct}% Accuracy"), unsafe_allow_html=True)

        st.markdown(f"""
        <div class='stat-row'>
            <div class='stat-card'><div class='stat-value' style='color:#00C9A7;'>{correct_count}</div><div class='stat-label'>Correct</div></div>
            <div class='stat-card'><div class='stat-value' style='color:#FC5A5A;'>{total - correct_count}</div><div class='stat-label'>Incorrect</div></div>
            <div class='stat-card'><div class='stat-value'>{pct}%</div><div class='stat-label'>Accuracy</div></div>
        </div>
        """, unsafe_allow_html=True)

        st.success("Your teacher has received your full practice session report.")
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Start New Session"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    else:
        # --- Practice Question ---
        pq = pqs[idx]

        st.markdown(f"<p class='progress-label'>Problem {idx+1} of {len(pqs)}</p>", unsafe_allow_html=True)
        st.progress((idx + 1) / len(pqs))
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class='question-card'>
            <div class='concept-tag'>{pq['concept']}</div>
            <div class='question-text'>{pq['question']}</div>
        </div>
        """, unsafe_allow_html=True)

        selected = st.radio("Select your answer:", pq["options"], key=f"practice_{idx}", index=None)
        st.markdown("<br>", unsafe_allow_html=True)

        if not st.session_state.practice_checked:
            if st.button("Check Answer"):
                if selected is None:
                    st.error("Please select an answer before checking.")
                else:
                    st.session_state.practice_answer = selected
                    st.session_state.practice_checked = True
                    st.session_state.show_explanation = False
                    st.session_state.explanation_text = ""
                    correct = selected == pq["answer"]
                    st.session_state.practice_results.append((pq, correct))
                    st.rerun()

        if st.session_state.practice_checked:
            if st.session_state.practice_answer == pq["answer"]:
                st.success("Correct!")
            else:
                st.error(f"Incorrect. The correct answer is: {pq['answer']}")

            col1, col2 = st.columns(2)
            with col1:
                if not st.session_state.show_explanation:
                    if st.button("Show Explanation"):
                        with st.spinner("Generating explanation..."):
                            try:
                                msg = client.chat.completions.create(
                                    model="deepseek-chat",
                                    max_tokens=300,
                                    messages=[{"role": "user", "content": f"Explain in 3 clear sentences why the answer to this economics question is '{pq['answer']}':\n{pq['question']}"}],
                                )
                                st.session_state.explanation_text = msg.choices[0].message.content
                                st.session_state.show_explanation = True
                                st.rerun()
                            except Exception:
                                st.error("Could not generate explanation. The AI service may be temporarily unavailable.")
            with col2:
                if st.button("Next Problem  \u2192"):
                    st.session_state.practice_index += 1
                    st.session_state.practice_checked = False
                    st.session_state.practice_answer = None
                    st.session_state.show_explanation = False
                    st.session_state.explanation_text = ""
                    st.rerun()

            if st.session_state.show_explanation and st.session_state.explanation_text:
                st.info(st.session_state.explanation_text)


# =============================================
#  FOOTER (all pages)
# =============================================
st.markdown("""
<div class='app-footer'>
    Economics Olympiad Prep &nbsp;&middot;&nbsp; PhysMath School, Yerevan &nbsp;&middot;&nbsp; Powered by DeepSeek AI
</div>
""", unsafe_allow_html=True)
