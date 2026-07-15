from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="AI Employee | SAP Operations",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def _demo_operations() -> pd.DataFrame:
    """Create deterministic-looking demo data for local development."""
    now = datetime.now().replace(second=0, microsecond=0)
    rows: list[dict[str, Any]] = []
    flow_names = ["LU04_321", "LB10_914", "MM02_452", "VA01_728"]
    statuses = ["Running", "Completed", "Completed", "Completed", "Failed"]
    for offset in range(48):
        event_time = now - timedelta(minutes=30 * offset)
        rows.append(
            {
                "event_time": event_time,
                "operation_count": 120 + ((offset * 37) % 165),
                "flow_name": flow_names[offset % len(flow_names)],
                "status": statuses[offset % len(statuses)],
            }
        )
    return pd.DataFrame(rows)


def _validate_columns(data: pd.DataFrame) -> pd.DataFrame:
    expected = {"event_time", "operation_count", "flow_name", "status"}
    missing = expected - set(data.columns)
    if missing:
        raise ValueError(
            "Databricks query is missing required columns: "
            + ", ".join(sorted(missing))
            + "."
        )
    result = data.copy()
    result["event_time"] = pd.to_datetime(result["event_time"], errors="coerce")
    result["operation_count"] = pd.to_numeric(
        result["operation_count"], errors="coerce"
    ).fillna(0)
    result["flow_name"] = result["flow_name"].fillna("Unknown").astype(str)
    result["status"] = result["status"].fillna("Unknown").astype(str)
    return result.dropna(subset=["event_time"]).sort_values(
        "event_time", ascending=False
    )


@st.cache_data(ttl=55, show_spinner="Loading dashboard data...")
def load_operations(source: str) -> pd.DataFrame:
    if source == "Demo":
        return _demo_operations()

    try:
        from databricks import sql
    except ImportError as error:
        raise RuntimeError(
            "The Databricks connector is not installed. Run start_dashboard.bat "
            "again to install the dependencies."
        ) from error

    config = st.secrets["databricks"]
    query = config["dashboard_query"]
    with sql.connect(
        server_hostname=config["server_hostname"],
        http_path=config["http_path"],
        access_token=config["access_token"],
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            data = pd.DataFrame(cursor.fetchall(), columns=columns)
    return _validate_columns(data)


def _chart(data: pd.DataFrame) -> go.Figure:
    trend = (
        data.assign(hour=data["event_time"].dt.floor("h"))
        .groupby("hour", as_index=False)["operation_count"]
        .sum()
        .sort_values("hour")
    )
    figure = go.Figure(
        go.Scatter(
            x=trend["hour"],
            y=trend["operation_count"],
            mode="lines",
            line={"color": "#0f67bd", "width": 3, "shape": "spline"},
            fill="tozeroy",
            fillcolor="rgba(15, 103, 189, 0.12)",
            hovertemplate="%{x|%d %b, %H:%M}<br>%{y:,.0f} operations<extra></extra>",
        )
    )
    figure.update_layout(
        height=280,
        margin={"l": 0, "r": 0, "t": 12, "b": 0},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis={"showgrid": False, "title": None, "tickformat": "%H:%M"},
        yaxis={"showgrid": True, "gridcolor": "#e4eef9", "title": None},
        font={"family": "Arial, sans-serif", "color": "#31506f"},
        showlegend=False,
    )
    return figure


def _status_icon(status: str) -> str:
    normalized = status.lower()
    if normalized == "running":
        return "🟢"
    if normalized in {"completed", "success"}:
        return "✅"
    if normalized in {"failed", "error"}:
        return "🔴"
    return "⚪"


def render_dashboard() -> None:
    source = st.sidebar.radio("Data source", ["Demo", "Databricks"], horizontal=True)
    if st.sidebar.button("Refresh now", use_container_width=True):
        load_operations.clear()

    try:
        data = load_operations(source)
    except (KeyError, RuntimeError, ValueError) as error:
        st.error(f"Unable to load dashboard data: {error}")
        st.info("Switch to Demo in the sidebar or complete .streamlit/secrets.toml.")
        return

    now = pd.Timestamp.now()
    today = data[data["event_time"].dt.date == now.date()]
    total_operations = int(data["operation_count"].sum())
    today_operations = int(today["operation_count"].sum())
    completed = data["status"].str.lower().isin(["completed", "success"]).sum()
    success_rate = completed / len(data) * 100 if len(data) else 0
    running = data[data["status"].str.lower() == "running"]

    st.markdown(
        """
        <div class="hero">
          <div>
            <span class="eyebrow">PHILIPS WAREHOUSE</span>
            <h1>AI EMPLOYEE</h1>
            <p>Real-time SAP Operations Center</p>
          </div>
          <div class="refresh-label">Auto-refresh every 60 seconds<br>
            <strong>Updated: %s</strong></div>
        </div>
        """
        % datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        unsafe_allow_html=True,
    )

    metric_columns = st.columns(4)
    metrics = [
        ("Total SAP Operation", f"{total_operations:,}", "Last 24 hours"),
        ("Today", f"{today_operations:,}", "Operations completed"),
        ("Success Rate", f"{success_rate:.1f}%", "Completed / total events"),
        ("Flows Running", str(len(running)), "Active automations"),
    ]
    for column, (label, value, caption) in zip(metric_columns, metrics):
        with column:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">{label}</div>'
                f'<div class="metric-value">{value}</div>'
                f'<div class="metric-caption">{caption}</div></div>',
                unsafe_allow_html=True,
            )

    main_column, side_column = st.columns([1.8, 1], gap="large")
    with main_column:
        st.markdown("### SAP Operation Trend")
        st.plotly_chart(_chart(data), use_container_width=True, config={"displayModeBar": False})
        st.markdown("### Activity")
        activity = data.loc[:, ["event_time", "operation_count", "flow_name", "status"]].head(12)
        activity = activity.rename(
            columns={
                "event_time": "DateTime",
                "operation_count": "Operation",
                "flow_name": "Flow",
                "status": "Status",
            }
        )
        st.dataframe(
            activity,
            hide_index=True,
            use_container_width=True,
            column_config={
                "DateTime": st.column_config.DatetimeColumn(format="YYYY-MM-DD HH:mm:ss"),
                "Operation": st.column_config.NumberColumn(format="%d"),
            },
        )

    with side_column:
        st.markdown("### 🤖 AI Assistant")
        st.info(
            f"**Here is today's status.**  \n"
            f"{len(running)} flows are running and {today_operations:,} operations "
            "have been processed today."
        )
        st.caption("Connect an LLM later to answer operation questions from Databricks.")
        st.markdown("### Flow Status")
        latest_flows = data.drop_duplicates("flow_name").head(6)
        for _, flow in latest_flows.iterrows():
            st.markdown(
                f'<div class="flow-card"><span>{_status_icon(flow["status"])}</span>'
                f'<div><strong>{flow["flow_name"]}</strong><br>'
                f'<span>{flow["status"]}</span></div>'
                f'<small>{flow["event_time"].strftime("%H:%M")}</small></div>',
                unsafe_allow_html=True,
            )


st.markdown(
    """
    <style>
      .stApp { background: linear-gradient(135deg, #f4fbff 0%, #e6f2ff 55%, #d9ecff 100%); }
      .block-container { max-width: 1450px; padding-top: 1.2rem; padding-bottom: 2rem; }
      .hero { min-height: 150px; border-radius: 22px; padding: 26px 34px; margin-bottom: 22px;
              color: white; display: flex; align-items: center; justify-content: space-between;
              background: linear-gradient(115deg, #033b88 0%, #075fbd 57%, #45a6ec 100%);
              box-shadow: 0 12px 26px rgba(20, 88, 158, 0.24); }
      .hero h1 { margin: 1px 0; font-size: 2.6rem; letter-spacing: .05em; }
      .hero p, .refresh-label { margin: 0; opacity: .9; }
      .eyebrow { font-size: .75rem; font-weight: 700; letter-spacing: .14em; }
      .refresh-label { text-align: right; font-size: .82rem; }
      .metric-card, .flow-card { background: rgba(255,255,255,.83); border: 1px solid #d6e5f2;
               border-radius: 16px; box-shadow: 0 5px 16px rgba(34, 93, 139, .08); }
      .metric-card { padding: 18px 20px; min-height: 120px; }
      .metric-label { font-weight: 700; color: #4a6079; }
      .metric-value { color: #0a5aa7; font-size: 2rem; font-weight: 800; margin: 6px 0; }
      .metric-caption { color: #73889d; font-size: .78rem; }
      .flow-card { display: flex; align-items: center; gap: 12px; padding: 12px; margin-bottom: 10px; }
      .flow-card span { color: #4f759d; font-size: .82rem; }
      .flow-card small { margin-left: auto; color: #6483a3; }
      div[data-testid="stSidebar"] { background: #f7fbff; }
    </style>
    """,
    unsafe_allow_html=True,
)

try:
    @st.fragment(run_every="60s")
    def refreshing_dashboard() -> None:
        render_dashboard()

    refreshing_dashboard()
except AttributeError:
    st.warning("Please upgrade Streamlit to enable automatic refreshing.")
    render_dashboard()
