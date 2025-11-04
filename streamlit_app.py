"""
MetaCheck - Educational AI Literacy Tool
Streamlit Web Interface 

A fact-checking tool with educational transparency, designed to teach students how AI evaluates information.
"""

import streamlit as st
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
import plotly.graph_objects as go
import plotly.express as px

# Import MetaCheck core functionality
from MetaCheck import verify_claims, VerificationResult, FinalAssessment

# Page configuration
st.set_page_config(
    page_title="MetaCheck - AI Literacy Tool",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 4rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    .sub-header {
        font-size: 1.3rem;
        color: #666;
        margin-bottom: 2rem;
        text-align: center;
    }
    .source-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: #f9f9f9;
    }
    .verdict-box {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .supported {
        background-color: #d4edda;
        border: 2px solid #28a745;
    }
    .refuted {
        background-color: #f8d7da;
        border: 2px solid #dc3545;
    }
    .insufficient {
        background-color: #fff3cd;
        border: 2px solid #ffc107;
    }
    .conflicting {
        background-color: #d1ecf1;
        border: 2px solid #17a2b8;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'ai_result' not in st.session_state:
        st.session_state.ai_result = None
    if 'student_assessment' not in st.session_state:
        st.session_state.student_assessment = None
    if 'analysis_running' not in st.session_state:
        st.session_state.analysis_running = False
    if 'current_claim' not in st.session_state:
        st.session_state.current_claim = ""


def render_sidebar():
    """Render sidebar with settings and information"""
    with st.sidebar:
        st.markdown("## ⚙️ Display Settings")
        st.caption("Toggle visibility of educational transparency steps")

        # Display toggles for all 6 steps
        show_search = st.checkbox("🔍 STEP 0: Search Strategy", value=True, key="show_search")
        show_sources = st.checkbox("📚 STEP 1: Source Details", value=True, key="show_sources")
        show_craap = st.checkbox("🎯 STEP 1: CRAAP Test Breakdown", value=True, key="show_craap")
        show_contradictions = st.checkbox("⚔️ STEP 2: Contradictions", value=True, key="show_contradictions")
        show_sensitivity = st.checkbox("🔴 STEP 3: Sensitivity Detection", value=True, key="show_sensitivity")
        show_verdict = st.checkbox("🤔 STEP 3.5: Verdict Reasoning", value=True, key="show_verdict")
        show_confidence = st.checkbox("📊 STEP 4: Confidence Assessment", value=True, key="show_confidence")
        show_escalation = st.checkbox("🚨 STEP 5: Escalation Decision", value=True, key="show_escalation")
        show_limitations = st.checkbox("🔬 STEP 6: AI Limitations", value=True, key="show_limitations")

        st.divider()

        st.markdown("## 📚 About MetaCheck")
        st.markdown("""
        **MetaCheck v1.0** is an educational tool designed to teach AI literacy
        and critical thinking by showing students HOW AI evaluates information.

        **Learning Objectives:**
        - Source evaluation (CRAAP test)
        - Evidence weighting
        - AI decision-making
        - Critical thinking

        **Version:** 1.0 (Educational Transparency)
        """)

        st.divider()

        # Quick tips
        with st.expander("💡 Quick Tips"):
            st.markdown("""
            1. **Optional:** Make your own assessment first in the "Your Assessment" tab
            2. Enter a claim and run AI analysis
            3. Explore each step of the AI's reasoning
            4. Compare your assessment with the AI's (if you made one)
            5. Export and share your analysis
            """)


def render_student_assessment_tab():
    """Render the student assessment tab (B.2 - Comparative Learning - OPTIONAL)"""
    st.markdown("### 👨‍🎓 Make Your Own Assessment (Optional)")
    st.info("📌 **This step is optional.** You can skip directly to 'AI Analysis' if you prefer to see the AI's assessment first.")

    with st.expander("🧠 Why make your own assessment?", expanded=False):
        st.markdown("""
        Making your own assessment before seeing the AI's helps you:
        - Practice critical thinking skills
        - Identify gaps in your reasoning
        - Learn from comparing different approaches
        - Understand your own biases
        """)

    st.divider()

    # Student assessment form
    st.markdown("#### Your Verdict")

    col1, col2 = st.columns(2)

    with col1:
        student_verdict = st.selectbox(
            "What is your verdict?",
            ["SUPPORTED", "REFUTED", "INSUFFICIENT", "CONFLICTING", "NEEDS_INSTRUCTOR"],
            help="Choose the verdict that best matches the evidence you found"
        )

        student_confidence = st.slider(
            "How confident are you?",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.05,
            help="0.0 = No confidence, 1.0 = Completely certain"
        )

    with col2:
        student_sources_count = st.number_input(
            "How many sources did you check?",
            min_value=0,
            max_value=50,
            value=0,
            help="Number of sources you consulted"
        )

        student_time = st.number_input(
            "How long did you spend? (minutes)",
            min_value=0,
            max_value=120,
            value=5,
            help="Time spent on your assessment"
        )

    student_reasoning = st.text_area(
        "Explain your reasoning:",
        placeholder="Why did you reach this verdict? What evidence did you find? What sources did you use?",
        height=150,
        help="Be specific about your reasoning process"
    )

    student_key_sources = st.text_area(
        "Key sources you used (optional):",
        placeholder="List the main sources you consulted (one per line)",
        height=100
    )

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("💾 Save Assessment", type="primary", use_container_width=True):
            if student_reasoning.strip():
                st.session_state.student_assessment = {
                    'verdict': student_verdict,
                    'confidence': student_confidence,
                    'reasoning': student_reasoning,
                    'sources_count': student_sources_count,
                    'time_spent': student_time,
                    'key_sources': student_key_sources.split('\n') if student_key_sources else [],
                    'timestamp': datetime.now()
                }
                st.success("✅ Assessment saved! You can now run the AI analysis.")
            else:
                st.error("⚠️ Please provide your reasoning before saving.")

    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.student_assessment = None
            st.rerun()

    # Show saved assessment if exists
    if st.session_state.student_assessment:
        st.divider()
        st.markdown("#### ✅ Your Saved Assessment")
        assessment = st.session_state.student_assessment

        col1, col2, col3 = st.columns(3)
        col1.metric("Verdict", assessment['verdict'])
        col2.metric("Confidence", f"{assessment['confidence']:.2f}")
        col3.metric("Sources", assessment['sources_count'])

        with st.expander("View your reasoning", expanded=False):
            st.write(assessment['reasoning'])
            if assessment['key_sources']:
                st.markdown("**Sources:**")
                for source in assessment['key_sources']:
                    if source.strip():
                        st.write(f"- {source}")


def create_evidence_weight_chart(verdict_reasoning):
    """Create Plotly bar chart for evidence weights (B.3)"""
    fig = go.Figure()

    # Supporting evidence
    fig.add_trace(go.Bar(
        name='Supporting',
        x=['Evidence Weight'],
        y=[verdict_reasoning.supporting_weight],
        text=[f"{verdict_reasoning.supporting_weight:.2f}"],
        textposition='auto',
        marker_color='#28a745',
        hovertemplate='<b>Supporting Evidence</b><br>Weight: %{y:.2f}<br>Sources: ' +
                      str(verdict_reasoning.supporting_sources_count) + '<extra></extra>'
    ))

    # Refuting evidence
    fig.add_trace(go.Bar(
        name='Refuting',
        x=['Evidence Weight'],
        y=[verdict_reasoning.refuting_weight],
        text=[f"{verdict_reasoning.refuting_weight:.2f}"],
        textposition='auto',
        marker_color='#dc3545',
        hovertemplate='<b>Refuting Evidence</b><br>Weight: %{y:.2f}<br>Sources: ' +
                      str(verdict_reasoning.refuting_sources_count) + '<extra></extra>'
    ))

    # Neutral evidence
    if verdict_reasoning.neutral_weight > 0:
        fig.add_trace(go.Bar(
            name='Neutral',
            x=['Evidence Weight'],
            y=[verdict_reasoning.neutral_weight],
            text=[f"{verdict_reasoning.neutral_weight:.2f}"],
            textposition='auto',
            marker_color='#ffc107',
            hovertemplate='<b>Neutral Evidence</b><br>Weight: %{y:.2f}<br>Sources: ' +
                          str(verdict_reasoning.neutral_sources_count) + '<extra></extra>'
        ))

    fig.update_layout(
        title="Evidence Weight Comparison",
        xaxis_title="",
        yaxis_title="Total Credibility Score",
        barmode='group',
        height=350,
        showlegend=True,
        hovermode='x unified'
    )

    return fig


def create_craap_radar_chart(craap_assessment):
    """Create radar chart for CRAAP scores (B.3)"""
    categories = ['Currency', 'Relevance', 'Authority', 'Accuracy', 'Purpose']
    scores = [
        craap_assessment.currency_score,
        craap_assessment.relevance_score,
        craap_assessment.authority_score,
        craap_assessment.accuracy_score,
        craap_assessment.purpose_score
    ]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=categories,
        fill='toself',
        name='CRAAP Scores',
        marker_color='#1f77b4'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=False,
        height=350,
        title="CRAAP Test Profile"
    )

    return fig


def render_search_strategy(metacog_detail):
    """Render Step 0: Search Strategy (B.1)"""
    if not metacog_detail or not metacog_detail.search_queries:
        return

    with st.expander("🔍 STEP 0: Search Strategy", expanded=st.session_state.get('show_search', True)):
        st.markdown("The AI generated the following search queries:")

        for idx, query in enumerate(metacog_detail.search_queries, 1):
            with st.container():
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"**📌 Query {idx}:** `{query.query_text}`")
                    st.markdown(f"**Reasoning:** {query.query_reasoning}")
                    st.markdown(f"**Strategy:** {query.search_strategy}")

                with col2:
                    st.metric("Tool", query.source_tool.replace("_", " ").title())
                    st.metric("Results", f"{query.results_used}/{query.results_count}")

                if idx < len(metacog_detail.search_queries):
                    st.divider()

        if metacog_detail.search_strategy_summary:
            st.info(f"💡 **Strategy Summary:** {metacog_detail.search_strategy_summary}")


def render_source_assessment(metacog_detail):
    """Render Step 1: Source-by-Source Assessment (B.1, B.3)"""
    if not metacog_detail or not metacog_detail.sources_assessed:
        return

    with st.expander("📚 STEP 1: Source-by-Source Assessment", expanded=st.session_state.get('show_sources', True)):
        st.markdown(f"**Total sources assessed:** {len(metacog_detail.sources_assessed)}")

        # Source selector (B.1 - Interactive)
        source_names = [f"{i+1}. {s.source_name}" for i, s in enumerate(metacog_detail.sources_assessed)]
        selected_idx = st.selectbox(
            "Select a source to view details:",
            range(len(source_names)),
            format_func=lambda i: source_names[i]
        )

        source = metacog_detail.sources_assessed[selected_idx]

        st.divider()

        # Source header
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.markdown(f"### {source.source_name}")
            st.markdown(f"**Type:** {source.source_type.replace('_', ' ').title()}")
            if source.url:
                st.markdown(f"**URL:** [{source.url}]({source.url})")

        with col2:
            # Stance indicator
            stance_colors = {
                "supports": "🟢",
                "refutes": "🔴",
                "neutral": "🟡",
                "unclear": "⚪"
            }
            st.metric("Stance", f"{stance_colors.get(source.stance, '⚪')} {source.stance.upper()}")

        with col3:
            st.metric("Credibility", f"{source.credibility_score:.2f}")
            st.metric("Relevance", f"{source.relevance_score:.2f}")

        st.divider()

        # Two-column layout for details
        col1, col2 = st.columns([1, 1])

        with col1:
            # CRAAP Test (B.3 - Visual)
            if st.session_state.get('show_craap', True) and source.craap_assessment:
                st.markdown("#### 🎯 CRAAP Test Assessment")

                craap = source.craap_assessment

                # Radar chart
                fig_radar = create_craap_radar_chart(craap)
                st.plotly_chart(fig_radar, use_container_width=True)

                # Detailed breakdown
                with st.expander("View CRAAP Details", expanded=False):
                    st.markdown("**C - Currency**")
                    st.progress(craap.currency_score, text=f"{craap.currency_score:.2f}")
                    st.caption(craap.currency_notes)

                    st.markdown("**R - Relevance**")
                    st.progress(craap.relevance_score, text=f"{craap.relevance_score:.2f}")
                    st.caption(craap.relevance_notes)

                    st.markdown("**A - Authority**")
                    st.progress(craap.authority_score, text=f"{craap.authority_score:.2f}")
                    st.caption(craap.authority_notes)

                    st.markdown("**A - Accuracy**")
                    st.progress(craap.accuracy_score, text=f"{craap.accuracy_score:.2f}")
                    st.caption(craap.accuracy_notes)

                    st.markdown("**P - Purpose**")
                    st.progress(craap.purpose_score, text=f"{craap.purpose_score:.2f}")
                    st.caption(craap.purpose_notes)

                    st.metric("**Overall CRAAP Score**", f"{craap.overall_craap_score:.2f}")

        with col2:
            # Stance reasoning
            st.markdown("#### 📍 Stance Analysis")
            st.markdown(f"**Why {source.stance.upper()}:**")
            st.write(source.stance_reasoning)

            # Key quotes
            if source.key_quotes:
                st.markdown("**Key Quotes:**")
                for quote in source.key_quotes:
                    st.info(f"💬 \"{quote}\"")

            # Credibility reasoning
            st.markdown("#### 💯 Credibility Analysis")
            st.write(source.credibility_reasoning)

            if source.credibility_factors:
                st.markdown("**Factors:**")
                for factor in source.credibility_factors:
                    st.write(f"• {factor}")

        # Snippet
        if source.snippet:
            with st.expander("📄 Source Snippet", expanded=False):
                st.markdown(source.snippet)

        # Navigation buttons
        st.divider()
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if selected_idx > 0:
                if st.button("⬅️ Previous Source", use_container_width=True):
                    st.rerun()

        with col3:
            if selected_idx < len(metacog_detail.sources_assessed) - 1:
                if st.button("Next Source ➡️", use_container_width=True):
                    st.rerun()


def render_verdict_reasoning(metacog_detail):
    """Render Step 3.5: Verdict Decision Process (B.1, B.3)"""
    if not metacog_detail or not metacog_detail.verdict_reasoning:
        return

    with st.expander("🤔 STEP 3.5: Verdict Decision Process", expanded=st.session_state.get('show_verdict', True)):
        vr = metacog_detail.verdict_reasoning

        # Evidence weight chart (B.3)
        st.markdown("### 📊 Evidence Weighting Calculation")

        fig = create_evidence_weight_chart(vr)
        st.plotly_chart(fig, use_container_width=True)

        # Summary metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Supporting Sources", vr.supporting_sources_count,
                    help=f"Total weight: {vr.supporting_weight:.2f}")
        col2.metric("Refuting Sources", vr.refuting_sources_count,
                    help=f"Total weight: {vr.refuting_weight:.2f}")
        col3.metric("Neutral Sources", vr.neutral_sources_count,
                    help=f"Total weight: {vr.neutral_weight:.2f}")

        st.divider()

        # Decision process
        st.markdown("### 🔍 Verdict Alternatives Considered")

        all_verdicts = ["SUPPORTED", "REFUTED", "INSUFFICIENT", "CONFLICTING", "NEEDS_INSTRUCTOR"]

        for verdict in all_verdicts:
            if verdict == vr.final_verdict:
                st.success(f"✅ **{verdict}** - SELECTED")
            else:
                st.error(f"❌ **{verdict}** - Rejected")

        st.divider()

        # Reasoning details
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 💡 Primary Reason")
            st.info(vr.primary_reason)

            st.markdown("#### 📋 Decision Rule Applied")
            st.write(vr.decision_rule_applied)

        with col2:
            st.markdown("#### 🎯 Decisive Factor")
            st.info(vr.decisive_factor)

            if vr.decisive_sources:
                st.markdown("**Decisive Sources:**")
                for source in vr.decisive_sources:
                    st.write(f"• {source}")

        st.divider()

        # Confidence analysis
        st.markdown("### 🔒 Confidence Analysis")

        col1, col2 = st.columns([1, 2])

        with col1:
            st.metric("Final Confidence", f"{vr.confidence:.2f}")

        with col2:
            st.markdown("**Confidence Reasoning:**")
            st.write(vr.confidence_reasoning)

            if vr.confidence_factors:
                st.markdown("**Factors:**")
                for factor in vr.confidence_factors:
                    st.write(f"• {factor}")

        # Why not alternatives
        if vr.why_not_alternatives:
            with st.expander("❓ Why Not Other Verdicts?", expanded=False):
                st.write(vr.why_not_alternatives)


def render_ai_limitations(metacog_detail):
    """Render Step 6: AI Limitations (B.1)"""
    if not metacog_detail:
        return

    with st.expander("🔬 STEP 6: AI Limitations & Uncertainties", expanded=st.session_state.get('show_limitations', True)):
        st.markdown("""
        Understanding the AI's limitations is crucial for developing critical thinking skills.
        Always question and verify AI outputs.
        """)

        col1, col2 = st.columns(2)

        with col1:
            if metacog_detail.ai_uncertainties:
                st.markdown("#### ❓ What the AI Couldn't Determine")
                for idx, uncertainty in enumerate(metacog_detail.ai_uncertainties, 1):
                    st.warning(f"{idx}. {uncertainty}")

            if metacog_detail.assumptions_made:
                st.markdown("#### 🤔 Assumptions Made")
                for idx, assumption in enumerate(metacog_detail.assumptions_made, 1):
                    st.info(f"{idx}. {assumption}")

        with col2:
            if metacog_detail.potential_weaknesses:
                st.markdown("#### ⚠️ Potential Weaknesses")
                for idx, weakness in enumerate(metacog_detail.potential_weaknesses, 1):
                    st.error(f"{idx}. {weakness}")

        # Metacognitive summary
        if metacog_detail.metacognitive_summary:
            st.divider()
            st.markdown("#### 💡 Metacognitive Summary for Students")
            st.success(metacog_detail.metacognitive_summary)


def render_claim_card(claim_result, claim_idx):
    """Render a summary card for a single claim"""
    verdict_emojis = {
        "SUPPORTED": "✅",
        "REFUTED": "❌",
        "INSUFFICIENT": "❓",
        "CONFLICTING": "⚔️",
        "NEEDS_INSTRUCTOR": "🚨"
    }

    verdict_colors = {
        "SUPPORTED": "#d4edda",
        "REFUTED": "#f8d7da",
        "INSUFFICIENT": "#fff3cd",
        "CONFLICTING": "#d1ecf1",
        "NEEDS_INSTRUCTOR": "#f8d7da"
    }

    emoji = verdict_emojis.get(claim_result.verdict, "📋")
    bg_color = verdict_colors.get(claim_result.verdict, "#f9f9f9")

    # Truncate claim if too long
    display_claim = claim_result.claim if len(claim_result.claim) <= 150 else claim_result.claim[:147] + "..."

    with st.container():
        st.markdown(f"""
        <div style="
            background-color: {bg_color};
            border-left: 5px solid {verdict_colors.get(claim_result.verdict, '#ddd')};
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
        ">
            <h4 style="margin: 0 0 10px 0;">{emoji} Claim {claim_idx}</h4>
            <p style="margin: 5px 0;"><strong>"{display_claim}"</strong></p>
            <div style="display: flex; gap: 20px; margin-top: 10px;">
                <span>📋 <strong>Verdict:</strong> {claim_result.verdict}</span>
                <span>🎯 <strong>Confidence:</strong> {claim_result.confidence:.2f}</span>
                <span>📚 <strong>Sources:</strong> {len(claim_result.evidence_list)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_detailed_claim_analysis(claim_result, claim_idx):
    """Render detailed analysis for a selected claim"""
    metacog = claim_result.metacognitive_detail

    st.markdown(f"## 📋 Claim {claim_idx}: Detailed Analysis")
    st.markdown(f"**\"{claim_result.claim}\"**")

    st.divider()

    # Verdict summary box
    verdict_class = claim_result.verdict.lower()
    st.markdown(f"""
    <div class="verdict-box {verdict_class}">
        <h3>📋 Final Verdict: {claim_result.verdict}</h3>
        <p><strong>Confidence:</strong> {claim_result.confidence:.2f}</p>
        <p><strong>Justification:</strong> {claim_result.justification}</p>
    </div>
    """, unsafe_allow_html=True)

    # Key metrics
    st.markdown("### 📊 Quick Overview")
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Sources", len(claim_result.evidence_list))

    supporting = len([e for e in claim_result.evidence_list if e.stance == "supports"])
    col2.metric("Supporting", supporting)

    refuting = len([e for e in claim_result.evidence_list if e.stance == "refutes"])
    col3.metric("Refuting", refuting)

    if claim_result.evidence_list:
        avg_cred = sum(e.credibility_score for e in claim_result.evidence_list) / len(claim_result.evidence_list)
        col4.metric("Avg Credibility", f"{avg_cred:.2f}")
    else:
        col4.metric("Avg Credibility", "N/A")

    st.divider()

    # Render educational transparency steps
    render_search_strategy(metacog)
    render_source_assessment(metacog)

    # STEP 2: Contradiction Analysis (always show)
    with st.expander("⚔️ STEP 2: Contradiction Analysis", expanded=st.session_state.get('show_contradictions', False)):
        if metacog and metacog.contradiction_detection and metacog.contradiction_detection.detected:
            cd = metacog.contradiction_detection
            st.warning(f"**Contradictions Detected - Severity:** {cd.severity.upper()}")
            st.write(cd.description)
            if cd.contradicting_sources:
                st.markdown("**Conflicting Sources:**")
                for source in cd.contradicting_sources:
                    st.write(f"• {source}")
        else:
            st.success("✓ No contradictions detected among sources")
            st.info("All sources provide consistent information about the claim.")

    # STEP 3: Sensitivity Detection (always show)
    with st.expander("🔴 STEP 3: Sensitivity Detection", expanded=st.session_state.get('show_sensitivity', False)):
        if metacog and metacog.sensitivity_analysis and metacog.sensitivity_analysis.is_sensitive:
            sa = metacog.sensitivity_analysis
            st.warning("**This is a sensitive topic**")
            if sa.sensitive_categories:
                st.write(f"**Categories:** {', '.join(sa.sensitive_categories)}")
            st.write(f"**Reasoning:** {sa.reasoning}")
        else:
            st.success("✓ Not classified as a sensitive topic")
            st.info("This claim does not involve highly controversial political, safety, or security issues requiring special handling.")

    render_verdict_reasoning(metacog)

    # STEP 4: Confidence Assessment (always show)
    with st.expander("📊 STEP 4: Confidence Assessment", expanded=st.session_state.get('show_confidence', False)):
        st.markdown("### Confidence Score Breakdown")
        st.metric("Final Confidence", f"{claim_result.confidence:.2f}",
                  help="0.0 = No confidence, 1.0 = Absolute certainty")

        st.divider()

        if metacog and metacog.verdict_reasoning:
            vr = metacog.verdict_reasoning

            st.markdown("#### Confidence Factors:")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Evidence Quality:**")
                st.write(f"• Supporting weight: {vr.supporting_weight:.2f}")
                st.write(f"• Refuting weight: {vr.refuting_weight:.2f}")
                st.write(f"• Neutral weight: {vr.neutral_weight:.2f}")

            with col2:
                st.markdown("**Source Quality:**")
                st.write(f"• Total sources: {len(claim_result.evidence_list)}")
                if claim_result.evidence_list:
                    avg_cred = sum(e.credibility_score for e in claim_result.evidence_list) / len(claim_result.evidence_list)
                    st.write(f"• Average credibility: {avg_cred:.2f}")

            st.divider()

            st.markdown("#### Reasoning:")
            if hasattr(vr, 'confidence_reasoning') and vr.confidence_reasoning:
                st.write(vr.confidence_reasoning)
            else:
                st.write(f"Confidence of {claim_result.confidence:.2f} based on {len(claim_result.evidence_list)} sources with average credibility of {avg_cred:.2f}.")

    # STEP 5: Escalation Decision (always show)
    with st.expander("🚨 STEP 5: Escalation Decision", expanded=st.session_state.get('show_escalation', False)):
        if metacog and metacog.escalation_decision and metacog.escalation_decision.should_escalate:
            ed = metacog.escalation_decision
            st.error("**⚠️ Instructor review recommended**")
            st.write("This claim requires human expert review before reaching a final conclusion.")

            if ed.reasons:
                st.markdown("**Reasons for Escalation:**")
                for reason in ed.reasons:
                    st.write(f"• {reason}")

            if ed.suggested_actions:
                st.markdown("**Suggested Actions:**")
                for action in ed.suggested_actions:
                    st.write(f"• {action}")
        else:
            st.success("✓ No escalation needed")
            st.info("The AI has sufficient confidence and clarity to provide a verdict without human expert review.")

    render_ai_limitations(metacog)

    # Key sources
    st.divider()
    st.markdown("### 📎 Key Sources")
    for idx, source in enumerate(claim_result.key_sources, 1):
        st.write(f"{idx}. {source}")


def render_ai_analysis_tab():
    """Render the AI analysis tab - restructured for multiple claims"""
    st.markdown("### 🤖 AI Fact-Check Analysis")

    # Claim input
    claim_input = st.text_area(
        "Enter text to fact-check (can contain multiple claims):",
        value=st.session_state.current_claim,
        placeholder="e.g., Donald Trump increased military recruitment in 2025. COVID-19 vaccines are safe.",
        height=100,
        key="claim_input_ai",
        help="Enter any text. The AI will automatically extract and verify all factual claims."
    )

    # Run analysis button
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        run_button = st.button(
            "🔍 Run AI Analysis",
            type="primary",
            disabled=not claim_input.strip() or st.session_state.analysis_running,
            use_container_width=True
        )

    with col2:
        if st.button("🗑️ Clear Results", use_container_width=True):
            st.session_state.ai_result = None
            st.session_state.current_claim = ""
            if 'selected_claim_idx' in st.session_state:
                del st.session_state.selected_claim_idx
            st.rerun()

    # Run analysis
    if run_button:
        st.session_state.current_claim = claim_input
        st.session_state.analysis_running = True

        # Show detailed progress
        progress_placeholder = st.empty()
        status_placeholder = st.empty()

        try:
            with progress_placeholder.container():
                st.info("🔄 **Analysis in progress...**")
                st.markdown("""
                The AI is performing comprehensive fact-checking. This involves:
                - 📝 Extracting factual claims from your text
                - 🔍 Searching multiple sources (web, Wikipedia, fact-checkers)
                - 🎯 Evaluating source credibility using CRAAP test
                - 🤔 Synthesizing evidence and reaching verdicts
                - 📊 Generating complete transparency documentation

                **Expected time:** 30-90 seconds depending on text complexity
                """)

                # Progress bar
                progress_bar = st.progress(0)

                # Show time elapsed
                import time
                start_time = time.time()
                status_text = st.empty()

                # Run analysis in background with periodic updates
                status_text.text("⏳ Starting analysis...")
                progress_bar.progress(10)

                # Run the fact-check
                result = asyncio.run(verify_claims(claim_input, verbose=False))

                # Update final progress
                elapsed = time.time() - start_time
                progress_bar.progress(100)
                status_text.text(f"✅ Completed in {elapsed:.1f} seconds")

            st.session_state.ai_result = result
            st.session_state.analysis_running = False

            # Clear progress indicators
            progress_placeholder.empty()
            status_placeholder.empty()

            st.success(f"✅ Analysis complete! Found {len(result.claim_results)} claim(s) in {elapsed:.1f} seconds.")
            st.rerun()

        except Exception as e:
            progress_placeholder.empty()
            status_placeholder.empty()
            st.error(f"❌ Error during analysis: {str(e)}")
            st.exception(e)  # Show full traceback for debugging
            st.session_state.analysis_running = False

    # Display results - RESTRUCTURED FOR MULTIPLE CLAIMS
    if st.session_state.ai_result:
        result = st.session_state.ai_result

        if not result.claim_results:
            st.warning("No verifiable factual claims found in the input text.")
            st.info("💡 Tip: Make sure your text contains factual assertions that can be verified, not just opinions or questions.")
            return

        st.divider()

        # LEVEL 1: Show all claims in summary cards
        st.markdown("## 📋 Claims Found and Verified")
        st.markdown(f"**{len(result.claim_results)} claim(s) extracted from your text**")

        # Display all claim cards
        for idx, claim_result in enumerate(result.claim_results, 1):
            render_claim_card(claim_result, idx)

        st.divider()

        # LEVEL 2: Detailed analysis for selected claim
        if len(result.claim_results) > 1:
            st.markdown("## 🔬 Detailed Analysis")
            st.markdown("Select a claim to view its complete analysis:")

            # Claim selector
            claim_options = [f"Claim {i+1}: {cr.claim[:80]}..." if len(cr.claim) > 80 else f"Claim {i+1}: {cr.claim}"
                           for i, cr in enumerate(result.claim_results)]

            selected_idx = st.selectbox(
                "Choose a claim:",
                range(len(result.claim_results)),
                format_func=lambda i: claim_options[i],
                key="selected_claim_idx"
            )

            st.divider()

            # Show detailed analysis for selected claim
            render_detailed_claim_analysis(result.claim_results[selected_idx], selected_idx + 1)

        else:
            # Only one claim - show detailed analysis directly
            st.markdown("## 🔬 Detailed Analysis")
            render_detailed_claim_analysis(result.claim_results[0], 1)


def render_comparison_tab():
    """Render the comparison tab (B.2)"""
    st.markdown("### ⚖️ Compare Your Assessment with AI")

    # Check if both assessments exist
    has_student = st.session_state.student_assessment is not None
    has_ai = st.session_state.ai_result is not None

    if not has_student and not has_ai:
        st.info("""
        📌 **To see a comparison:**
        1. Make your own assessment in the "Your Assessment" tab (optional)
        2. Run the AI analysis in the "AI Analysis" tab
        3. Come back here to compare

        💡 **Tip:** You can also skip your own assessment and just view the AI's analysis.
        """)
        return

    if not has_ai:
        st.warning("⚠️ Please run the AI analysis first in the 'AI Analysis' tab.")
        return

    if not has_student:
        st.info("""
        💡 You haven't made your own assessment. That's okay!

        You can view the AI's analysis in the 'AI Analysis' tab, or go back to
        'Your Assessment' tab to make your own assessment and then compare.
        """)
        return

    # Both exist - show comparison
    student = st.session_state.student_assessment
    ai_result = st.session_state.ai_result.claim_results[0]

    st.success("✅ Comparison ready! Let's see how your assessment compares with the AI's.")

    st.divider()

    # Side-by-side comparison
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 👨‍🎓 Your Assessment")

        st.metric("Verdict", student['verdict'])
        st.metric("Confidence", f"{student['confidence']:.2f}")
        st.metric("Sources Checked", student['sources_count'])
        st.metric("Time Spent", f"{student['time_spent']} min")

        st.markdown("**Your Reasoning:**")
        st.info(student['reasoning'])

        if student['key_sources']:
            with st.expander("Your Sources", expanded=False):
                for source in student['key_sources']:
                    if source.strip():
                        st.write(f"• {source}")

    with col2:
        st.markdown("### 🤖 AI Assessment")

        st.metric("Verdict", ai_result.verdict)
        st.metric("Confidence", f"{ai_result.confidence:.2f}")
        st.metric("Sources Found", len(ai_result.evidence_list))
        st.metric("Avg Source Credibility",
                  f"{sum(e.credibility_score for e in ai_result.evidence_list) / len(ai_result.evidence_list):.2f}")

        st.markdown("**AI Justification:**")
        st.info(ai_result.justification)

        with st.expander("AI's Key Sources", expanded=False):
            for source in ai_result.key_sources:
                st.write(f"• {source}")

    st.divider()

    # Comparison analysis
    st.markdown("### 📊 Comparison Analysis")

    # Verdict comparison
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📋 Verdict Match")
        if student['verdict'] == ai_result.verdict:
            st.success(f"✅ **Perfect Match!** Both chose: {student['verdict']}")
            st.balloons()
        else:
            st.warning(f"⚠️ **Different Verdicts**")
            st.write(f"• You: {student['verdict']}")
            st.write(f"• AI: {ai_result.verdict}")

    with col2:
        st.markdown("#### 🎯 Confidence Comparison")
        confidence_diff = abs(student['confidence'] - ai_result.confidence)

        if confidence_diff < 0.15:
            st.success(f"✅ **Similar Confidence** (diff: {confidence_diff:.2f})")
        elif confidence_diff < 0.30:
            st.info(f"📊 **Moderate Difference** (diff: {confidence_diff:.2f})")
        else:
            st.warning(f"⚠️ **Large Difference** (diff: {confidence_diff:.2f})")

        # Confidence comparison chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Your Confidence', 'AI Confidence'],
            y=[student['confidence'], ai_result.confidence],
            text=[f"{student['confidence']:.2f}", f"{ai_result.confidence:.2f}"],
            textposition='auto',
            marker_color=['#1f77b4', '#ff7f0e']
        ))
        fig.update_layout(
            title="Confidence Comparison",
            yaxis_title="Confidence Score",
            yaxis_range=[0, 1],
            height=300,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Reflection questions
    st.markdown("### 🎓 Reflection Questions")

    with st.expander("💭 Think About These Questions", expanded=True):
        st.markdown("""
        1. **Why did you reach your verdict?** What evidence influenced you most?

        2. **If you disagreed with the AI**, what sources did you consider that the AI didn't find?
           Or what factors did the AI consider that you missed?

        3. **Source Quality**: How did your sources compare to the AI's in terms of credibility?
           Did you apply something like the CRAAP test?

        4. **Confidence Levels**: Why was your confidence higher or lower than the AI's?
           What would increase your confidence?

        5. **What did you learn** from seeing the AI's reasoning process? Would you change
           your assessment after seeing the AI's sources and reasoning?

        6. **AI Limitations**: What did the AI identify as its limitations? Do you think
           there are other weaknesses the AI missed?
        """)

    # Learning insights
    st.divider()
    st.markdown("### 💡 Learning Insights")

    # Generate insights based on comparison
    insights = []

    if student['verdict'] == ai_result.verdict:
        insights.append("✅ You and the AI reached the same verdict - great job!")
    else:
        insights.append("🤔 You and the AI reached different verdicts. This is a great learning opportunity!")

    if student['sources_count'] < len(ai_result.evidence_list):
        insights.append(f"📚 The AI checked more sources ({len(ai_result.evidence_list)}) than you ({student['sources_count']}). More sources can provide better coverage.")
    elif student['sources_count'] > len(ai_result.evidence_list):
        insights.append(f"📚 You checked more sources ({student['sources_count']}) than the AI ({len(ai_result.evidence_list)}). Thorough research!")

    if confidence_diff > 0.3:
        if student['confidence'] > ai_result.confidence:
            insights.append("🎯 You were more confident than the AI. Consider whether you might have confirmation bias.")
        else:
            insights.append("🎯 The AI was more confident than you. Review the evidence to see why.")

    for insight in insights:
        st.info(insight)


def generate_export_text(result: FinalAssessment) -> str:
    """Generate text export of the analysis (B.4)"""
    lines = []
    lines.append("=" * 70)
    lines.append("MetaCheck v1.0 - Educational Fact-Check Analysis")
    lines.append("=" * 70)
    lines.append(f"Generated: {result.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Total Claims: {result.total_claims}")
    lines.append("")

    for idx, claim_result in enumerate(result.claim_results, 1):
        lines.append("-" * 70)
        lines.append(f"CLAIM {idx}: {claim_result.claim}")
        lines.append("-" * 70)
        lines.append(f"Verdict: {claim_result.verdict}")
        lines.append(f"Confidence: {claim_result.confidence:.2f}")
        lines.append("")
        lines.append(f"Justification: {claim_result.justification}")
        lines.append("")
        lines.append("Key Sources:")
        for source in claim_result.key_sources:
            lines.append(f"  • {source}")
        lines.append("")

        # Add metacognitive details if available
        if claim_result.metacognitive_detail:
            metacog = claim_result.metacognitive_detail

            if metacog.search_queries:
                lines.append("Search Queries:")
                for query in metacog.search_queries:
                    lines.append(f"  • {query.query_text}")
                    lines.append(f"    Reasoning: {query.query_reasoning}")
                lines.append("")

            if metacog.verdict_reasoning:
                vr = metacog.verdict_reasoning
                lines.append("Evidence Weighting:")
                lines.append(f"  Supporting: {vr.supporting_weight:.2f} ({vr.supporting_sources_count} sources)")
                lines.append(f"  Refuting: {vr.refuting_weight:.2f} ({vr.refuting_sources_count} sources)")
                lines.append("")

            if metacog.ai_uncertainties:
                lines.append("AI Uncertainties:")
                for u in metacog.ai_uncertainties:
                    lines.append(f"  • {u}")
                lines.append("")

    lines.append("=" * 70)
    lines.append("Generated by MetaCheck v1.0 - Educational Transparency")
    lines.append("=" * 70)

    return "\n".join(lines)


def render_export_section():
    """Render export functionality (B.4)"""
    if not st.session_state.ai_result:
        return

    st.divider()
    st.markdown("### 📥 Export Analysis")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Text export
        export_text = generate_export_text(st.session_state.ai_result)
        st.download_button(
            label="📄 Download as TXT",
            data=export_text,
            file_name=f"metacheck_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    with col2:
        # JSON export
        import json
        json_data = st.session_state.ai_result.model_dump_json(indent=2)
        st.download_button(
            label="📋 Download as JSON",
            data=json_data,
            file_name=f"metacheck_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

    with col3:
        # Share link placeholder
        st.button(
            label="🔗 Share Link",
            help="Feature coming soon! Deploy to Streamlit Cloud to enable sharing.",
            disabled=True,
            use_container_width=True
        )


def main():
    """Main application"""
    # Initialize
    initialize_session_state()

    # Header
    st.markdown('<p class="main-header">🔍 MetaCheck</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Educational AI Literacy Tool with Complete Transparency</p>', unsafe_allow_html=True)

    # Render sidebar
    render_sidebar()

    # Main tabs
    tab1, tab2, tab3 = st.tabs([
        "👨‍🎓 Your Assessment (Optional)",
        "🤖 AI Analysis",
        "⚖️ Compare"
    ])

    with tab1:
        render_student_assessment_tab()

    with tab2:
        render_ai_analysis_tab()
        render_export_section()

    with tab3:
        render_comparison_tab()

    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
        MetaCheck v1.0 (Educational Transparency) |
        Designed for teaching AI literacy and critical thinking |
        <a href='https://github.com/anthropics/claude-code' target='_blank'>Documentation</a>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
