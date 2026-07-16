from __future__ import annotations

import base64
import html
from datetime import datetime
from pathlib import Path
from textwrap import dedent

import pandas as pd
import streamlit as st

from dashboard_data import (
    DashboardData,
    load_connected_dashboard,
    load_demo_dashboard,
)


APP_DIR = Path(__file__).resolve().parent
ASSETS_DIR = APP_DIR / "assets"

st.set_page_config(
    page_title="AI Employee | SAP Operations",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def asset_data_url(path: Path) -> str:
    suffix = path.suffix.lower()
    mime = "image/gif" if suffix == ".gif" else "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def employee_asset() -> Path:
    gif_path = ASSETS_DIR / "ai-employee.gif"
    if gif_path.exists():
        return gif_path
    return ASSETS_DIR / "ai-operator.png"


def load_dashboard_sources() -> DashboardData:
    st.sidebar.markdown("## Data settings")
    mode = st.sidebar.radio("Data mode", ["Demo", "Connected sources"])
    st.sidebar.caption("Operations: Databricks")
    st.sidebar.caption("Flow status: SharePoint Excel")
    st.sidebar.caption("Live activity: SharePoint CSV/TXT")
    if st.sidebar.button("Refresh all sources", use_container_width=True):
        st.cache_data.clear()

    if mode == "Demo":
        return load_demo_dashboard()

    dashboard = load_connected_dashboard()
    for message in dashboard.source_messages:
        st.sidebar.warning(message)
    return dashboard


def daily_volume(data: pd.DataFrame, days: int = 7) -> pd.DataFrame:
    end = data["event_time"].max().normalize()
    dates = pd.date_range(end=end, periods=days, freq="D")
    return (
        data.assign(day=data["event_time"].dt.normalize())
        .groupby("day", as_index=False)["operation_count"]
        .sum()
        .set_index("day")
        .reindex(dates, fill_value=0)
        .rename_axis("day")
        .reset_index()
    )


def trend_svg(data: pd.DataFrame) -> str:
    trend = daily_volume(data)
    values = trend["operation_count"].astype(float).tolist()
    labels = [value.strftime("%b %d") for value in trend["day"]]
    width, height = 410, 150
    left, right, top, bottom = 18, 18, 24, 30
    plot_width = width - left - right
    plot_height = height - top - bottom
    maximum = max(values) or 1
    minimum = min(values)
    spread = max(maximum - minimum, maximum * 0.25, 1)
    points: list[tuple[float, float]] = []
    for index, value in enumerate(values):
        x = left + (plot_width * index / max(len(values) - 1, 1))
        y = top + plot_height - ((value - minimum) / spread * plot_height * 0.82)
        points.append((x, max(top, min(top + plot_height, y))))

    line_parts = [f"M {points[0][0]:.1f} {points[0][1]:.1f}"]
    for (previous_x, previous_y), (x, y) in zip(points, points[1:]):
        midpoint_x = (previous_x + x) / 2
        line_parts.append(
            f"C {midpoint_x:.1f} {previous_y:.1f}, "
            f"{midpoint_x:.1f} {y:.1f}, {x:.1f} {y:.1f}"
        )
    line_path = " ".join(line_parts)
    area_path = (
        line_path
        + f" L {points[-1][0]:.1f} {top + plot_height:.1f}"
        + f" L {points[0][0]:.1f} {top + plot_height:.1f} Z"
    )
    label_nodes = "".join(
        f'<text x="{x:.1f}" y="142" text-anchor="middle">{html.escape(label)}</text>'
        for (x, _), label in zip(points, labels)
    )
    return f"""
    <svg class="trend-chart" viewBox="0 0 {width} {height}" role="img" aria-label="Seven day SAP operation trend">
      <defs>
        <linearGradient id="trendArea" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#2b76f0" stop-opacity=".27"/>
          <stop offset="1" stop-color="#2b76f0" stop-opacity="0"/>
        </linearGradient>
      </defs>
      <line class="trend-grid" x1="18" y1="120" x2="392" y2="120"/>
      <line class="trend-grid" x1="18" y1="76" x2="392" y2="76"/>
      <path class="trend-area" d="{area_path}"/>
      <path class="trend-line" d="{line_path}"/>
      <g class="trend-labels">{label_nodes}</g>
    </svg>
    """


def flow_rows(data: pd.DataFrame) -> str:
    latest = (
        data.sort_values("last_run", ascending=False)
        .drop_duplicates("flow_name")
        .head(3)
    )
    output: list[str] = []
    for _, row in latest.iterrows():
        status = str(row["status"]).title()
        failed = bool(row.get("attention_required", False)) or status.lower() in {"failed", "error", "attention"}
        tone = "danger" if failed else "success"
        icon = "!" if failed else "✓"
        output.append(
            f'<div class="flow-row {tone}">'
            f'<span class="status-orb">{icon}</span>'
            f'<div class="flow-copy"><strong>{html.escape(str(row["flow_name"]))}</strong>'
            f'<b>{html.escape(status)}</b><small>Last run {row["last_run"]:%H:%M:%S}</small></div>'
            f'<div class="flow-volume"><strong>{int(row["operation_count"]):,}</strong><span>operations</span></div>'
            "</div>"
        )
    return "".join(output)


def activity_rows(data: pd.DataFrame) -> str:
    latest = data.sort_values("event_time", ascending=False).head(5)
    output: list[str] = []
    for _, row in latest.iterrows():
        status = str(row["status"]).title()
        failed = status.lower() in {"failed", "error", "attention"}
        tone = "danger" if failed else "success"
        output.append(
            f'<li><time>{row["event_time"]:%H:%M:%S}</time>'
            f'<span class="timeline-dot {tone}"></span>'
            f'<strong>{html.escape(str(row["flow_name"]))}</strong>'
            f'<span class="operation-pill">{int(row["operation_count"]):,} operations</span>'
            f'<em class="{tone}">{html.escape(status)}</em></li>'
        )
    return "".join(output)


def render_dashboard() -> None:
    dashboard = load_dashboard_sources()
    operations = dashboard.operations
    flows = dashboard.flows
    activities = dashboard.activities
    latest_day = operations["event_time"].max().date()
    today = operations[operations["event_time"].dt.date == latest_day]
    total_operations = int(operations["operation_count"].sum())
    today_operations = int(today["operation_count"].sum())
    running = int(flows[flows["status"].str.lower() == "running"]["flow_name"].nunique())
    exceptions = int(flows["attention_required"].sum())
    source_label = dashboard.source_label
    robot_url = asset_data_url(employee_asset())
    now = datetime.now()

    st.markdown(
        "".join(
            line.strip()
            for line in f"""
        <main class="dashboard-viewport">
          <header class="app-header">
            <div class="brand-mark" aria-hidden="true"><i></i><i></i></div>
            <strong class="brand-name" aria-label="AI Employee"><span>AI</span><span>EMPLOYEE</span></strong>
            <div class="brand-line"><span></span><p>People-led, AI powered</p><span></span></div>
            <div class="system-state"><i></i><span>SYSTEM ONLINE</span></div>
            <div class="refresh-state"><span>Last refreshed</span><strong>{now:%Y-%m-%d %H:%M:%S}</strong><small>{html.escape(source_label)}</small></div>
            <div class="profile"><span>AI</span><div><strong>Wally / 小库</strong><small>AI Digital Employee</small></div></div>
          </header>

          <section class="hero-row">
            <div class="robot-card">
              <img src="{robot_url}" alt="AI employee operating an SAP workstation">
            </div>

            <div class="speech-card">
              <div class="speaker"><span>AI</span><div><strong>Wally</strong><small>Operations assistant</small></div></div>
              <h2>Good morning!</h2>
              <p>Here is the status of SAP operations today.</p>
              <ul>
                <li><b>✓</b>{today_operations:,} operations processed today</li>
                <li><b>✓</b>{running} flows are running smoothly</li>
                <li><b class="green">✓</b>{exceptions} exceptions require attention</li>
              </ul>
            </div>

            <div class="glass-card total-card">
              <div class="total-metric">
                <span>Total SAP Operations</span>
                <strong>{total_operations:,}</strong>
                <div class="metric-divider"></div>
                <small>Today</small>
                <em>{today_operations:,}</em>
              </div>
              <div class="trend-panel">
                <div class="trend-heading"><div><strong>7-day operation trend</strong><span>Daily processed volume</span></div><small>LIVE</small></div>
                {trend_svg(operations)}
              </div>
            </div>
          </section>

          <section class="content-row">
            <div class="activity-column">
              <article class="glass-card capability-card">
                <div class="capability-heading">
                  <div><span class="card-icon ai-label">AI</span><div><h2>AI Warehouse Capabilities</h2><p>Authorized SAP workflows</p></div></div>
                  <strong>3 ENABLED</strong>
                </div>
                <div class="capability-list">
                  <div><b>LT01</b><span>Create Transfer Order</span><small><i></i>AI ready</small></div>
                  <div><b>LU04</b><span>Process Posting Change</span><small><i></i>AI ready</small></div>
                  <div><b>LB10</b><span>Process Transfer Requirement</span><small><i></i>AI ready</small></div>
                </div>
              </article>

              <article class="glass-card activity-card">
                <div class="card-heading"><span class="card-icon pulse-icon">⌁</span><div><h2>Live Activity</h2><p>Latest SAP automation events</p></div><small>Auto refresh · 60s</small></div>
              <ul class="activity-list">{activity_rows(activities)}</ul>
              </article>
            </div>

            <article class="glass-card flow-card">
              <div class="card-heading"><span class="card-icon">⌘</span><div><h2>Flow Status</h2><p>Current automation health</p></div><small>All flows ›</small></div>
              <div class="flow-list">{flow_rows(flows)}</div>
            </article>

            <article class="glass-card chat-card">
              <div class="chat-orbit"><span>AI</span></div>
              <div class="card-heading chat-heading"><span class="card-icon">✦</span><div><h2>Chat with Wally</h2><p>Your SAP operations assistant</p></div></div>
              <div class="assistant-message"><b>Wally</b><p>Ask me about operations, flows, execution status, or today's exceptions.</p></div>
              <div class="prompt-suggestions">
                <small>Suggested questions</small>
                <div class="prompt-card" role="button" aria-disabled="true">
                  <span class="prompt-icon control-icon" aria-hidden="true">
                    <svg viewBox="0 0 24 24"><path d="M8 6.5v11l8-5.5-8-5.5Z"/><path d="M18.5 7v10"/></svg>
                  </span>
                  <div><strong>Run or pause a flow</strong><p>Control a specific automation</p></div>
                  <svg class="prompt-arrow" viewBox="0 0 20 20" aria-hidden="true"><path d="m7.5 4.5 5.5 5.5-5.5 5.5"/></svg>
                </div>
                <div class="prompt-card attention-prompt" role="button" aria-disabled="true">
                  <span class="prompt-icon" aria-hidden="true">
                    <svg viewBox="0 0 24 24"><path d="M12 3.5 21 20H3L12 3.5Z"/><path d="M12 9v5M12 17.5h.01"/></svg>
                  </span>
                  <div><strong>Which flow needs attention?</strong><p>Review exceptions and health signals</p></div>
                  <svg class="prompt-arrow" viewBox="0 0 20 20" aria-hidden="true"><path d="m7.5 4.5 5.5 5.5-5.5 5.5"/></svg>
                </div>
              </div>
              <div class="chat-cta" role="link" aria-disabled="true"><span>Chat with me</span><b>→</b></div>
            </article>
          </section>
        </main>
            """.splitlines()
        ),
        unsafe_allow_html=True,
    )


st.markdown(
    dedent(
        """
    <style>
      :root {
        --navy: #071754;
        --ink: #0b1838;
        --muted: #536b91;
        --blue: #2168ef;
        --cyan: #25a8ef;
        --green: #0aad43;
        --red: #ef5a47;
        --line: rgba(128, 157, 202, .24);
        --glass: rgba(255, 255, 255, .58);
        --glass-strong: rgba(255, 255, 255, .72);
        --shadow: 0 18px 45px rgba(29, 67, 127, .14), inset 0 1px 0 rgba(255,255,255,.92);
      }
      * { box-sizing: border-box; }
      html, body, [data-testid="stAppViewContainer"], .stApp { height: 100%; overflow: hidden; }
      .stApp { background: #eaf4ff; color: var(--ink); font-family: Aptos, "Segoe UI Variable", "Segoe UI", sans-serif; }
      .stApp::before, .stApp::after { content: ""; position: fixed; pointer-events: none; border-radius: 50%; filter: blur(2px); }
      .stApp::before { width: 58vw; height: 58vw; left: -17vw; top: -24vw; background: radial-gradient(circle, rgba(47,137,255,.42), rgba(94,190,255,.13) 46%, transparent 69%); }
      .stApp::after { width: 48vw; height: 48vw; right: -16vw; bottom: -25vw; background: radial-gradient(circle, rgba(98,91,246,.2), rgba(62,151,255,.08) 48%, transparent 70%); }
      [data-testid="stHeader"] { display: none; }
      [data-testid="stMain"] { height: 100vh; overflow: hidden; }
      .block-container { width: 100%; max-width: none; height: 100vh; padding: 0 !important; }
      .block-container > [data-testid="stVerticalBlock"] { gap: 0 !important; }
      [data-testid="stSidebar"] { background: rgba(244,249,255,.92); backdrop-filter: blur(24px); border-right: 1px solid rgba(255,255,255,.8); }
      [data-testid="stSidebarCollapsedControl"] { opacity: .12; transition: opacity .18s ease; z-index: 100; }
      [data-testid="stSidebarCollapsedControl"]:hover { opacity: 1; }

      .dashboard-viewport { position: relative; z-index: 1; width: 100%; height: 100vh; display: grid; grid-template-rows: 8.4vh 37.2vh minmax(0, 1fr); gap: 1.5vh; padding: 0 1.15vw 1.4vh; overflow: hidden; }
      .glass-card, .speech-card { background: var(--glass); border: 1px solid rgba(255,255,255,.82); border-radius: clamp(16px, 1.35vw, 24px); box-shadow: var(--shadow); backdrop-filter: blur(24px) saturate(155%); -webkit-backdrop-filter: blur(24px) saturate(155%); }

      .app-header { margin: 0 -1.15vw; padding: 0 1.55vw; display: grid; grid-template-columns: auto auto 1fr auto auto auto; gap: 1vw; align-items: center; color: white; background: linear-gradient(100deg, #041044, #071957 56%, #10246f); border-bottom: 1px solid rgba(92,145,255,.5); box-shadow: 0 10px 30px rgba(4,18,74,.2); }
      .brand-mark { width: clamp(44px, 3.2vw, 58px); aspect-ratio: 1.22; display: grid; grid-template-columns: 1fr 1fr; place-items: center; padding: 0 9px; border: 2px solid #2998ff; border-radius: 14px; position: relative; }
      .brand-mark::before { content: ""; position: absolute; width: 2px; height: 9px; top: -10px; background: #2998ff; }
      .brand-mark i { width: 8px; height: 8px; border-radius: 50%; background: #2998ff; box-shadow: 0 0 10px rgba(41,152,255,.8); }
      .brand-name { display: inline-flex; align-items: center; gap: clamp(9px, .7vw, 13px); color: #f8fbff; font-family: "Bahnschrift SemiCondensed", "Bahnschrift", "Aptos Display", "Segoe UI Variable Display", sans-serif; font-size: clamp(1.45rem, 1.85vw, 2.15rem); font-weight: 600; white-space: nowrap; line-height: 1; text-rendering: geometricPrecision; }
      .brand-name span:first-child { letter-spacing: .035em; }
      .brand-name span:last-child { letter-spacing: .09em; }
      .brand-line { justify-self: center; display: flex; align-items: center; gap: 12px; color: #b7c9ff; font-size: clamp(.72rem, .95vw, 1.05rem); white-space: nowrap; }
      .brand-line p { margin: 0; } .brand-line span { width: 34px; height: 1px; background: #2a6ee8; }
      .system-state { display: flex; align-items: center; gap: 8px; font-size: clamp(.65rem, .75vw, .85rem); white-space: nowrap; }
      .system-state i { width: 11px; height: 11px; border-radius: 50%; background: #18d552; box-shadow: 0 0 14px rgba(24,213,82,.8); }
      .refresh-state { display: grid; grid-template-columns: auto auto; column-gap: 6px; align-items: baseline; padding-left: 1vw; border-left: 1px solid rgba(255,255,255,.22); font-size: clamp(.6rem, .7vw, .78rem); white-space: nowrap; }
      .refresh-state span { color: #aebce9; } .refresh-state strong { color: white; } .refresh-state small { grid-column: 1 / -1; text-align: right; color: #55b5ff; }
      .profile { display: flex; align-items: center; gap: 9px; white-space: nowrap; }
      .profile > span { width: clamp(36px, 2.8vw, 48px); aspect-ratio: 1; display: grid; place-items: center; border-radius: 50%; background: rgba(255,255,255,.94); border: 3px solid rgba(204,228,255,.9); color: #1765dc; font-weight: 800; }
      .profile div { display: flex; flex-direction: column; } .profile strong { font-size: clamp(.72rem,.85vw,.95rem); } .profile small { color: #aebce9; font-size: clamp(.58rem,.68vw,.76rem); }

      .hero-row { min-height: 0; display: grid; grid-template-columns: 1.4fr 1.15fr 2.35fr; gap: 1vw; }
      .robot-card { position: relative; z-index: 1; min-width: 0; display: flex; align-items: flex-end; justify-content: center; overflow: visible; }
      .robot-card img { position: relative; width: 148%; max-width: 600px; max-height: 140%; object-fit: contain; object-position: center bottom; margin-bottom: -10%; filter: drop-shadow(0 18px 20px rgba(15,53,111,.22)); }

      .speech-card { position: relative; z-index: 2; padding: clamp(14px, 1.2vw, 22px); background: var(--glass-strong); display: flex; flex-direction: column; justify-content: center; }
      .speech-card::before { content: ""; position: absolute; z-index: 2; left: -21px; top: 50%; width: 22px; height: 38px; background: rgba(247,251,255,.86); clip-path: polygon(0 50%, 100% 0, 100% 100%); transform: translateY(-50%); filter: drop-shadow(-1px 0 0 rgba(255,255,255,.82)); }
      .speaker { display: flex; align-items: center; gap: 8px; margin-bottom: .75vh; }
      .speaker > span { width: 30px; height: 30px; display: grid; place-items: center; border-radius: 50%; background: linear-gradient(145deg,#fff,#dcecff); color: var(--blue); font-size: .65rem; font-weight: 800; box-shadow: 0 5px 14px rgba(35,99,189,.15); }
      .speaker div { display: flex; flex-direction: column; line-height: 1.15; } .speaker strong { font-size: clamp(.7rem,.8vw,.92rem); } .speaker small { color: var(--muted); font-size: clamp(.52rem,.58vw,.66rem); }
      .speech-card h2 { margin: 0; color: #174ec3; font-size: clamp(1.05rem, 1.28vw, 1.5rem); }
      .speech-card p { margin: .6vh 0 1.2vh; color: #29436d; font-size: clamp(.62rem,.72vw,.8rem); line-height: 1.4; }
      .speech-card ul { list-style: none; padding: 0; margin: 0; display: grid; gap: .8vh; }
      .speech-card li { display: flex; align-items: center; gap: 8px; color: #19345e; font-size: clamp(.58rem,.68vw,.76rem); }
      .speech-card li b { flex: 0 0 auto; width: 17px; height: 17px; display: grid; place-items: center; border-radius: 50%; background: var(--blue); color: white; font-size: .6rem; }
      .speech-card li b.green { background: var(--green); }

      .total-card { min-width: 0; display: grid; grid-template-columns: .92fr 1.55fr; padding: clamp(15px, 1.35vw, 24px); }
      .total-metric { padding-right: 1.4vw; border-right: 1px solid var(--line); display: flex; flex-direction: column; justify-content: center; }
      .total-metric > span { font-size: clamp(.78rem,.9vw,1rem); font-weight: 700; }
      .total-metric > strong { margin-top: .7vh; color: #174bcb; font-size: clamp(2.8rem, 4.4vw, 5.1rem); line-height: 1; letter-spacing: .025em; }
      .metric-divider { width: 100%; height: 1px; margin: 1.4vh 0 1vh; background: var(--line); }
      .total-metric small { font-size: clamp(.62rem,.7vw,.78rem); font-weight: 700; } .total-metric em { color: var(--blue); font-style: normal; font-size: clamp(1.35rem,1.8vw,2.1rem); font-weight: 800; }
      .trend-panel { min-width: 0; padding-left: 1.4vw; display: flex; flex-direction: column; justify-content: center; }
      .trend-heading { display: flex; align-items: center; justify-content: space-between; }
      .trend-heading > div { display: flex; flex-direction: column; } .trend-heading strong { font-size: clamp(.7rem,.82vw,.92rem); } .trend-heading span { color: var(--muted); font-size: clamp(.52rem,.6vw,.68rem); }
      .trend-heading > small { padding: 4px 8px; border-radius: 99px; background: rgba(33,104,239,.08); color: var(--blue); font-size: .58rem; font-weight: 800; letter-spacing: .07em; }
      .trend-chart { width: 100%; height: min(20vh, 185px); overflow: visible; }
      .trend-grid { stroke: rgba(121,155,204,.24); stroke-width: 1; stroke-dasharray: 3 5; }
      .trend-area { fill: url(#trendArea); } .trend-line { fill: none; stroke: var(--blue); stroke-width: 4; stroke-linecap: round; stroke-linejoin: round; }
      .trend-labels { fill: #60769a; font-size: 10px; }

      .content-row { min-height: 0; display: grid; grid-template-columns: 1.55fr .82fr .92fr; gap: 1vw; }
      .activity-column { min-width: 0; min-height: 0; display: grid; grid-template-rows: minmax(148px, 17vh) minmax(0, 1fr); gap: 1.2vh; }
      .capability-card { min-width: 0; min-height: 0; padding: clamp(14px, 1.25vw, 22px); overflow: hidden; border-color: rgba(85,143,242,.28); background: linear-gradient(115deg, rgba(255,255,255,.74), rgba(229,241,255,.58)); }
      .capability-heading { min-height: 40px; display: flex; align-items: center; justify-content: space-between; gap: 12px; }
      .capability-heading > div { min-width: 0; display: flex; align-items: center; gap: 9px; }
      .ai-label { font-size: .62rem; letter-spacing: .03em; }
      .capability-heading h2 { margin: 0; color: #102d63; font-size: clamp(.78rem,.92vw,1.02rem); line-height: 1.08; }
      .capability-heading p { margin: 2px 0 0; color: var(--muted); font-size: clamp(.49rem,.56vw,.63rem); }
      .capability-heading > strong { flex: 0 0 auto; padding: 4px 8px; border-radius: 99px; color: #087f37; background: rgba(10,173,67,.1); font-size: clamp(.48rem,.54vw,.6rem); letter-spacing: .04em; }
      .capability-list { margin-top: .75vh; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: clamp(6px,.65vw,11px); }
      .capability-list > div { min-width: 0; display: grid; grid-template-columns: auto minmax(0,1fr); column-gap: 7px; align-items: center; padding: .55vh .55vw; border: 1px solid rgba(72,127,215,.17); border-radius: 10px; background: rgba(255,255,255,.56); }
      .capability-list b { grid-row: 1 / 3; color: #1558c8; font-size: clamp(.72rem,.85vw,.95rem); letter-spacing: .02em; }
      .capability-list span { min-width: 0; color: #173761; font-size: clamp(.48rem,.55vw,.62rem); font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
      .capability-list small { display: flex; align-items: center; gap: 4px; color: #168245; font-size: clamp(.44rem,.49vw,.55rem); }
      .capability-list small i { width: 6px; height: 6px; border-radius: 50%; background: var(--green); box-shadow: 0 0 0 3px rgba(10,173,67,.09); }
      .activity-card, .flow-card, .chat-card { min-width: 0; min-height: 0; padding: clamp(14px, 1.25vw, 22px); overflow: hidden; }
      .activity-column .activity-card { padding-bottom: clamp(11px, 1vw, 17px); }
      .card-heading { min-height: 40px; display: flex; align-items: center; gap: 9px; }
      .card-icon { flex: 0 0 31px; width: 31px; height: 31px; display: grid; place-items: center; border-radius: 10px; color: white; background: linear-gradient(145deg, #174fca, #2b8af4); box-shadow: 0 7px 16px rgba(33,104,239,.22); font-size: .88rem; font-weight: 800; line-height: 1; }
      .card-heading > div { display: flex; flex-direction: column; } .card-heading h2 { margin: 0; font-size: clamp(.88rem,1vw,1.12rem); line-height: 1.1; } .card-heading p { margin: 3px 0 0; color: var(--muted); font-size: clamp(.52rem,.6vw,.68rem); }
      .card-heading > small { margin-left: auto; color: var(--muted); font-size: clamp(.5rem,.58vw,.65rem); white-space: nowrap; }

      .activity-list { position: relative; list-style: none; margin: .7vh 0 0; padding: 0; display: grid; gap: min(.65vh, 7px); }
      .activity-list::before { content: ""; position: absolute; left: calc(clamp(58px,5vw,90px) + 4px); top: 8px; bottom: 8px; width: 1px; background: linear-gradient(#8ec0ff, #dce9f9); }
      .activity-list li { display: grid; grid-template-columns: clamp(58px,5vw,90px) 10px minmax(72px,1fr) auto auto; align-items: center; gap: clamp(6px,.65vw,12px); color: #20395f; font-size: clamp(.56rem,.66vw,.75rem); }
      .activity-list time { color: #314d78; font-variant-numeric: tabular-nums; }
      .timeline-dot { position: relative; z-index: 1; width: 10px; height: 10px; border-radius: 50%; background: var(--green); box-shadow: 0 0 0 4px rgba(10,173,67,.1); }
      .timeline-dot.danger { background: var(--red); box-shadow: 0 0 0 4px rgba(239,90,71,.1); }
      .operation-pill { padding: 5px 9px; border-radius: 99px; background: rgba(33,104,239,.08); color: #1554c4; white-space: nowrap; }
      .activity-list em { min-width: 58px; padding: 4px 7px; border-radius: 99px; background: rgba(10,173,67,.08); color: var(--green); text-align: center; font-style: normal; font-size: .9em; }
      .activity-list em.danger { background: rgba(239,90,71,.09); color: var(--red); }

      .flow-list { margin-top: 1vh; display: grid; gap: min(1.05vh, 10px); }
      .flow-row { min-height: clamp(62px, 8.5vh, 90px); display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: clamp(8px,.8vw,14px); padding: .75vh .8vw; border: 1px solid rgba(131,161,205,.24); border-left: 3px solid var(--green); border-radius: 14px; background: rgba(255,255,255,.46); box-shadow: 0 8px 18px rgba(36,75,137,.08), inset 0 1px 0 rgba(255,255,255,.88); }
      .flow-row.danger { border-left-color: var(--red); } .status-orb { width: clamp(28px,2.25vw,38px); aspect-ratio: 1; display: grid; place-items: center; border-radius: 50%; background: var(--green); color: white; font-weight: 800; }
      .flow-row.danger .status-orb { background: var(--red); }
      .flow-copy { min-width: 0; display: flex; flex-direction: column; } .flow-copy strong { font-size: clamp(.68rem,.78vw,.88rem); } .flow-copy b { color: var(--green); font-size: clamp(.56rem,.63vw,.72rem); } .flow-copy small { color: var(--muted); font-size: clamp(.48rem,.54vw,.61rem); white-space: nowrap; }
      .flow-row.danger .flow-copy b { color: var(--red); } .flow-volume { display: flex; flex-direction: column; align-items: flex-end; } .flow-volume strong { color: #174bcb; font-size: clamp(1rem,1.3vw,1.5rem); } .flow-volume span { color: var(--muted); font-size: clamp(.46rem,.52vw,.58rem); }

      .chat-card { position: relative; display: flex; flex-direction: column; }
      .chat-card::after { content: "AI"; position: absolute; right: -2vw; top: 10%; font-size: clamp(5rem,9vw,10rem); font-weight: 800; color: rgba(39,105,226,.035); }
      .chat-orbit { position: absolute; right: 1.2vw; top: 1.3vh; width: clamp(42px,3.5vw,64px); aspect-ratio: 1; display: grid; place-items: center; border-radius: 50%; border: 1px solid rgba(74,139,244,.22); background: radial-gradient(circle, rgba(255,255,255,.85), rgba(207,230,255,.55)); box-shadow: 0 12px 28px rgba(50,100,180,.13); }
      .chat-orbit span { color: var(--blue); font-weight: 800; font-size: clamp(.72rem,.9vw,1rem); }
      .chat-heading { padding-right: 4vw; }
      .assistant-message { position: relative; z-index: 1; margin-top: 1.4vh; padding: 1.15vh 1vw; border-radius: 14px 14px 14px 4px; background: rgba(255,255,255,.58); border: 1px solid rgba(255,255,255,.85); box-shadow: 0 7px 18px rgba(32,73,136,.08); }
      .assistant-message b { color: #1758c4; font-size: clamp(.58rem,.65vw,.74rem); } .assistant-message p { margin: .45vh 0 0; color: #24436f; font-size: clamp(.58rem,.68vw,.77rem); line-height: 1.45; }
      .prompt-suggestions { position: relative; z-index: 1; margin-top: 1.25vh; display: grid; gap: min(.8vh, 8px); }
      .prompt-suggestions > small { color: #6c82a5; font-size: clamp(.5rem,.57vw,.65rem); font-weight: 700; letter-spacing: .02em; }
      .prompt-card { min-height: clamp(48px, 6.2vh, 58px); display: grid; grid-template-columns: auto minmax(0,1fr) auto; align-items: center; gap: clamp(8px,.7vw,12px); padding: .7vh .7vw; border: 1px solid rgba(45,111,223,.13); border-radius: 13px; background: rgba(255,255,255,.5); box-shadow: inset 0 1px 0 rgba(255,255,255,.92), 0 6px 14px rgba(39,81,146,.06); }
      .prompt-icon { width: clamp(29px,2.1vw,36px); aspect-ratio: 1; display: grid; place-items: center; border-radius: 10px; color: #5c48e8; background: rgba(91,72,232,.1); }
      .prompt-icon.control-icon { color: var(--blue); background: rgba(33,104,239,.1); }
      .prompt-icon svg { width: 56%; fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
      .control-icon svg path:first-child { fill: currentColor; stroke: none; }
      .prompt-card > div { min-width: 0; display: flex; flex-direction: column; }
      .prompt-card strong { color: #183b70; font-size: clamp(.57rem,.65vw,.74rem); line-height: 1.2; }
      .prompt-card p { margin: 3px 0 0; color: var(--muted); font-size: clamp(.47rem,.53vw,.6rem); line-height: 1.2; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
      .prompt-arrow { width: 17px; fill: none; stroke: #6b86ae; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
      .chat-cta { position: relative; z-index: 1; min-height: 44px; margin-top: auto; padding: 0 14px; display: flex; align-items: center; justify-content: space-between; border-radius: 13px; color: white; background: linear-gradient(100deg, #185bd8, #2b78f2); box-shadow: 0 10px 22px rgba(33,104,239,.25), inset 0 1px 0 rgba(255,255,255,.2); font-size: clamp(.68rem,.78vw,.88rem); font-weight: 700; cursor: not-allowed; opacity: .9; }
      .chat-cta b { font-size: 1.25rem; }

      @media (max-width: 1180px), (max-aspect-ratio: 3/2) {
        html, body, [data-testid="stAppViewContainer"], .stApp, [data-testid="stMain"] { height: auto; min-height: 100%; overflow: auto; }
        .block-container { height: auto; min-height: 100vh; }
        .dashboard-viewport { height: auto; min-height: 100vh; grid-template-rows: auto; overflow: visible; padding-bottom: 16px; }
        .app-header { min-height: 72px; } .brand-line, .refresh-state { display: none; } .app-header { grid-template-columns: auto auto 1fr auto auto; }
        .hero-row { grid-template-columns: 1fr 1fr; min-height: 520px; } .total-card { grid-column: 1 / -1; min-height: 270px; }
        .content-row { grid-template-columns: 1fr 1fr; } .activity-column { min-height: 520px; grid-template-rows: auto minmax(360px,1fr); } .chat-card { grid-column: 1 / -1; min-height: 280px; }
      }
      @media (max-width: 700px) {
        .dashboard-viewport { padding-inline: 10px; gap: 10px; } .app-header { margin-inline: -10px; padding-inline: 12px; }
        .profile div, .system-state span { display: none; } .brand-name { font-size: 1.25rem; }
        .hero-row, .content-row { grid-template-columns: 1fr; } .total-card, .chat-card { grid-column: auto; }
        .activity-column { min-height: 620px; grid-template-rows: auto minmax(420px,1fr); } .capability-list { grid-template-columns: 1fr; }
        .robot-card { min-height: 300px; } .speech-card::before { left: 50%; top: -21px; width: 38px; height: 22px; clip-path: polygon(50% 0, 100% 100%, 0 100%); transform: translateX(-50%); }
        .total-card { grid-template-columns: 1fr; } .total-metric { border-right: 0; border-bottom: 1px solid var(--line); padding: 0 0 14px; } .trend-panel { padding: 14px 0 0; }
        .activity-list li { grid-template-columns: 62px 10px 1fr; } .operation-pill, .activity-list em { display: none; }
      }
      @media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation-duration: .01ms !important; transition-duration: .01ms !important; } }
    </style>
        """
    ),
    unsafe_allow_html=True,
)

try:
    @st.fragment(run_every="60s")
    def refreshing_dashboard() -> None:
        render_dashboard()

    refreshing_dashboard()
except AttributeError:
    render_dashboard()
