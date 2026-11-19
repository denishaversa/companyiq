"""Show a CompanyIQ report on screen: snapshot on top, sections below."""

from html import escape

import streamlit as st

from research.layout import SNAPSHOT_FACTS, split_focus, split_report

NOT_STATED = {"", "not stated", "n/a", "unknown"}

STYLE = """
<style>
.ciq-label {font-size: 0.75rem; font-weight: 700; letter-spacing: 0.06em;
  text-transform: uppercase; color: #0F766E; margin-bottom: 0.25rem;}
.ciq-facts {display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 0.75rem; margin: 0.25rem 0 0.5rem;}
.ciq-fact {background: #EFEDE8; border-radius: 10px; padding: 0.7rem 0.9rem;}
.ciq-fact .k {font-size: 0.75rem; color: #6B7280; text-transform: uppercase;
  letter-spacing: 0.05em;}
.ciq-fact .v {font-size: 1.1rem; font-weight: 700; line-height: 1.3;}
.ciq-steps {display: flex; gap: 0.4rem; overflow-x: auto; padding-bottom: 0.25rem;
  margin-bottom: 0.5rem;}
.ciq-step {flex: 1 0 130px; background: #E3F1EF; color: #0F766E; border-radius: 8px;
  padding: 0.5rem 0.7rem; font-size: 0.9rem; font-weight: 600;}
.ciq-step small {display: block; font-weight: 400; color: #1F2937; opacity: 0.8;}
.ciq-chips {display: flex; flex-wrap: wrap; gap: 0.4rem; margin-bottom: 0.75rem;}
.ciq-chip {font-size: 0.85rem; padding: 0.15rem 0.7rem; border-radius: 999px;
  background: #EFEDE8;}
.ciq-risk {display: flex; gap: 0.6rem; align-items: baseline; margin-bottom: 0.4rem;}
.ciq-sev {font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.05em; padding: 0.05rem 0.55rem; border-radius: 999px; flex: none;}
.ciq-sev.high {background: #FBE7E5; color: #B42318;}
.ciq-sev.medium {background: #FBEFD9; color: #B45309;}
.ciq-sev.low {background: #E3F1EF; color: #0F766E;}
.ciq-focus-title {font-size: 1.25rem; font-weight: 700; margin-bottom: 0.25rem;}
</style>
"""


def _stated(value) -> bool:
    return isinstance(value, str) and value.strip().lower() not in NOT_STATED


def _html(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


def _show_snapshot(snapshot: dict) -> None:
    if _stated(snapshot.get("summary")):
        with st.container(border=True):
            _html('<div class="ciq-label">In short</div>')
            st.write(snapshot["summary"])

    facts = [
        (label, snapshot.get(key))
        for key, label in SNAPSHOT_FACTS
        if _stated(snapshot.get(key))
    ]
    if facts:
        _html(
            '<div class="ciq-facts">'
            + "".join(
                f'<div class="ciq-fact"><div class="k">{escape(label)}</div>'
                f'<div class="v">{escape(value)}</div></div>'
                for label, value in facts
            )
            + "</div>"
        )

    steps = [
        step for step in snapshot.get("process_steps") or []
        if _stated(step.get("step"))
    ]
    if steps:
        _html('<div class="ciq-label">How the business runs</div>')
        _html(
            '<div class="ciq-steps">'
            + "".join(
                f'<div class="ciq-step">{n} · {escape(step["step"])}'
                f'<small>{escape(step.get("detail") or "")}</small></div>'
                for n, step in enumerate(steps, start=1)
            )
            + "</div>"
        )


def _show_extras(title: str, snapshot: dict | None) -> None:
    """Add competitor chips or risk badges at the top of matching sections."""

    if not snapshot:
        return

    lowered = title.lower()

    if "compet" in lowered:
        names = [n for n in snapshot.get("competitors") or [] if _stated(n)]
        if names:
            _html(
                '<div class="ciq-chips">'
                + "".join(f'<span class="ciq-chip">{escape(n)}</span>' for n in names)
                + "</div>"
            )

    if "risk" in lowered:
        risks = [r for r in snapshot.get("risks") or [] if _stated(r.get("risk"))]
        if risks:
            _html("".join(
                f'<div class="ciq-risk"><span class="ciq-sev {escape(r.get("level", "").lower())}">'
                f'{escape(r.get("level", ""))}</span><span>{escape(r["risk"])}</span></div>'
                for r in risks
            ))


def _show_focus(section, focus_team: str) -> None:
    """Show the team focus section in its own highlighted box."""

    title = section.title if section else f"Team Focus: {focus_team}"

    with st.container(border=True):
        _html('<div class="ciq-label">Your team focus</div>')
        _html(f'<div class="ciq-focus-title">{escape(title)}</div>')
        if section:
            st.markdown(section.body or "_No details in this section._")
        else:
            st.caption(
                "The report didn't include a separate section on this team. "
                "Try running the research again."
            )


def show_report(
    report: str, snapshot: dict | None, focus_team: str | None = None
) -> None:
    """Render the snapshot, the team focus (if any), then each report
    section in its own expander."""

    _html(STYLE)

    if snapshot:
        _show_snapshot(snapshot)

    if focus_team:
        focus, report = split_focus(report)
        _show_focus(focus, focus_team)

    parts = split_report(report)

    if parts.intro:
        st.markdown(parts.intro)

    if not parts.sections:
        # The report had no clear sections, so show it as it is.
        if not parts.intro:
            st.markdown(report)
        return

    open_all = st.toggle("Open all sections", key="open_all_sections")

    for index, section in enumerate(parts.sections):
        with st.expander(section.title, expanded=open_all or index == 0):
            _show_extras(section.title, snapshot)
            st.markdown(section.body or "_No details in this section._")
