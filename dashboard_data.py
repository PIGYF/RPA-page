from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from io import BytesIO
from typing import Any, Mapping
from urllib.parse import quote

import pandas as pd
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError


GRAPH_ROOT = "https://graph.microsoft.com/v1.0"


class DataSourceError(RuntimeError):
    """A dashboard data source is unavailable or incorrectly configured."""


@dataclass
class DashboardData:
    operations: pd.DataFrame
    flows: pd.DataFrame
    activities: pd.DataFrame
    source_label: str
    source_messages: tuple[str, ...] = ()


def _rename_columns(data: pd.DataFrame, aliases: Mapping[str, str]) -> pd.DataFrame:
    renamed: dict[Any, str] = {}
    for column in data.columns:
        normalized = str(column).strip().lower().replace(" ", "_")
        renamed[column] = aliases.get(normalized, normalized)
    return data.rename(columns=renamed).copy()


def _require_columns(data: pd.DataFrame, required: set[str], source: str) -> None:
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"{source} is missing required columns: {', '.join(sorted(missing))}")


def _parse_boolean(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y", "attention", "required"}


def validate_operations(data: pd.DataFrame) -> pd.DataFrame:
    result = _rename_columns(
        data,
        {
            "timestamp": "event_time",
            "datetime": "event_time",
            "date": "event_time",
            "operation_date": "event_time",
            "operations": "operation_count",
            "operation": "operation_count",
            "count": "operation_count",
        },
    )
    _require_columns(result, {"event_time", "operation_count"}, "Operations data")
    result["event_time"] = pd.to_datetime(result["event_time"], errors="coerce")
    result["operation_count"] = pd.to_numeric(result["operation_count"], errors="coerce").fillna(0)
    result = result.dropna(subset=["event_time"]).sort_values("event_time", ascending=False)
    if result.empty:
        raise ValueError("Operations data does not contain any valid timestamps.")
    return result


def validate_flow_status(data: pd.DataFrame) -> pd.DataFrame:
    result = _rename_columns(
        data,
        {
            "flow": "flow_name",
            "process": "flow_name",
            "workflow": "flow_name",
            "last_run_time": "last_run",
            "last_execution": "last_run",
            "operations": "operation_count",
            "operation": "operation_count",
            "needs_attention": "attention_required",
            "attention": "attention_required",
            "reason": "attention_reason",
        },
    )
    _require_columns(result, {"flow_name", "status", "last_run"}, "Flow status Excel")
    defaults: dict[str, Any] = {
        "operation_count": 0,
        "attention_required": False,
        "attention_reason": "",
    }
    for column, default in defaults.items():
        if column not in result.columns:
            result[column] = default
    result["last_run"] = pd.to_datetime(result["last_run"], errors="coerce")
    result["operation_count"] = pd.to_numeric(result["operation_count"], errors="coerce").fillna(0)
    result["flow_name"] = result["flow_name"].fillna("Unknown").astype(str)
    result["status"] = result["status"].fillna("Unknown").astype(str)
    result["attention_required"] = result["attention_required"].map(_parse_boolean)
    result["attention_reason"] = result["attention_reason"].fillna("").astype(str)
    result = result.dropna(subset=["last_run"]).sort_values("last_run", ascending=False)
    if result.empty:
        raise ValueError("Flow status Excel does not contain any valid last_run values.")
    return result


def validate_activity(data: pd.DataFrame) -> pd.DataFrame:
    result = _rename_columns(
        data,
        {
            "timestamp": "event_time",
            "datetime": "event_time",
            "flow": "flow_name",
            "process": "flow_name",
            "workflow": "flow_name",
            "event": "event_type",
            "action": "event_type",
            "operations": "operation_count",
            "operation": "operation_count",
            "details": "message",
            "description": "message",
        },
    )
    _require_columns(result, {"event_time", "flow_name", "status"}, "Activity logs")
    defaults: dict[str, Any] = {"event_type": "update", "operation_count": 0, "message": ""}
    for column, default in defaults.items():
        if column not in result.columns:
            result[column] = default
    result["event_time"] = pd.to_datetime(result["event_time"], errors="coerce")
    result["operation_count"] = pd.to_numeric(result["operation_count"], errors="coerce").fillna(0)
    for column in ["flow_name", "status", "event_type", "message"]:
        result[column] = result[column].fillna("").astype(str)
    result = result.dropna(subset=["event_time"]).sort_values("event_time", ascending=False)
    if result.empty:
        raise ValueError("Activity logs do not contain any valid timestamps.")
    return result


@st.cache_data(show_spinner=False)
def load_demo_operations() -> pd.DataFrame:
    now = datetime.now().replace(second=0, microsecond=0)
    totals = [253, 248, 124, 0, 271, 330, 51]
    rows = [
        {"event_time": now - timedelta(days=6 - index), "operation_count": total}
        for index, total in enumerate(totals)
    ]
    return validate_operations(pd.DataFrame(rows))


@st.cache_data(show_spinner=False)
def load_demo_flow_status() -> pd.DataFrame:
    now = datetime.now().replace(second=0, microsecond=0)
    return validate_flow_status(
        pd.DataFrame(
            [
                {"flow_name": "VA01_728", "status": "Completed", "last_run": now - timedelta(minutes=5), "operation_count": 8},
                {"flow_name": "MM02_452", "status": "Completed", "last_run": now - timedelta(minutes=74), "operation_count": 11},
                {"flow_name": "LB10_914", "status": "Running", "last_run": now - timedelta(minutes=143), "operation_count": 14},
                {"flow_name": "LU04_321", "status": "Running", "last_run": now - timedelta(minutes=212), "operation_count": 18},
            ]
        )
    )


@st.cache_data(show_spinner=False)
def load_demo_activity() -> pd.DataFrame:
    now = datetime.now().replace(second=0, microsecond=0)
    flows = ["VA01_728", "MM02_452", "LB10_914", "LU04_321", "VA01_728"]
    statuses = ["Completed", "Completed", "Running", "Running", "Completed"]
    counts = [8, 11, 14, 18, 53]
    rows = []
    for index, (flow, status, count) in enumerate(zip(flows, statuses, counts)):
        rows.append(
            {
                "event_time": now - timedelta(minutes=index * 31),
                "flow_name": flow,
                "event_type": "flow_completed" if status == "Completed" else "flow_started",
                "status": status,
                "operation_count": count,
                "message": f"{flow} {status.lower()}",
            }
        )
    return validate_activity(pd.DataFrame(rows))


@st.cache_data(ttl=55, show_spinner=False)
def load_databricks_operations() -> pd.DataFrame:
    try:
        from databricks import sql
    except ImportError as error:
        raise DataSourceError("Databricks connector is not installed.") from error

    try:
        config = st.secrets["databricks"]
        query = config["operations_query"]
        with sql.connect(
            server_hostname=config["server_hostname"],
            http_path=config["http_path"],
            access_token=config["access_token"],
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = pd.DataFrame(cursor.fetchall(), columns=columns)
    except KeyError as error:
        raise DataSourceError("Databricks secrets are incomplete.") from error
    except Exception as error:
        raise DataSourceError(f"Databricks query failed: {error}") from error
    return validate_operations(data)


def _sharepoint_config() -> Mapping[str, Any]:
    try:
        return st.secrets["sharepoint"]
    except (KeyError, StreamlitSecretNotFoundError) as error:
        raise DataSourceError("SharePoint secrets are not configured.") from error


def _graph_token(config: Mapping[str, Any]) -> str:
    try:
        import msal
    except ImportError as error:
        raise DataSourceError("MSAL is not installed.") from error
    required = ["tenant_id", "client_id", "client_secret"]
    missing = [name for name in required if not config.get(name)]
    if missing:
        raise DataSourceError("SharePoint credentials are incomplete: " + ", ".join(missing))
    app = msal.ConfidentialClientApplication(
        str(config["client_id"]),
        authority=f"https://login.microsoftonline.com/{config['tenant_id']}",
        client_credential=str(config["client_secret"]),
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    token = result.get("access_token")
    if not token:
        detail = result.get("error_description") or result.get("error") or "unknown authentication error"
        raise DataSourceError(f"SharePoint authentication failed: {detail}")
    return str(token)


def _graph_get(url: str, token: str, *, follow_redirects: bool = True) -> Any:
    try:
        import requests
    except ImportError as error:
        raise DataSourceError("Requests is not installed.") from error
    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
        timeout=35,
        allow_redirects=follow_redirects,
    )
    if response.status_code >= 400:
        raise DataSourceError(f"Microsoft Graph returned HTTP {response.status_code}: {response.text[:240]}")
    return response


def _drive_url(config: Mapping[str, Any]) -> str:
    drive_id = str(config.get("drive_id", "")).strip()
    if not drive_id:
        raise DataSourceError("SharePoint drive_id is not configured.")
    return f"{GRAPH_ROOT}/drives/{quote(drive_id, safe='')}"


def _download_drive_path(config: Mapping[str, Any], token: str, path: str) -> bytes:
    clean_path = quote(path.strip("/"), safe="/")
    response = _graph_get(f"{_drive_url(config)}/root:/{clean_path}:/content", token)
    return bytes(response.content)


@st.cache_data(ttl=30, show_spinner=False)
def load_sharepoint_flow_status() -> pd.DataFrame:
    config = _sharepoint_config()
    token = _graph_token(config)
    path = str(config.get("flow_excel_path", "")).strip()
    if not path:
        raise DataSourceError("SharePoint flow_excel_path is not configured.")
    content = _download_drive_path(config, token, path)
    sheet_name = config.get("flow_sheet_name", 0)
    try:
        data = pd.read_excel(BytesIO(content), sheet_name=sheet_name)
    except Exception as error:
        raise DataSourceError(f"Unable to read SharePoint flow Excel: {error}") from error
    return validate_flow_status(data)


def _parse_activity_file(name: str, content: bytes) -> pd.DataFrame:
    try:
        return pd.read_csv(BytesIO(content), sep=None, engine="python")
    except (UnicodeDecodeError, pd.errors.ParserError) as error:
        raise DataSourceError(f"Unable to parse activity file {name}: {error}") from error


@st.cache_data(ttl=20, show_spinner=False)
def load_sharepoint_activity() -> pd.DataFrame:
    config = _sharepoint_config()
    token = _graph_token(config)
    folder = str(config.get("activity_folder", "")).strip()
    if not folder:
        raise DataSourceError("SharePoint activity_folder is not configured.")
    max_files = max(1, min(int(config.get("activity_max_files", 20)), 100))
    clean_folder = quote(folder.strip("/"), safe="/")
    list_url = (
        f"{_drive_url(config)}/root:/{clean_folder}:/children"
        f"?$select=id,name,lastModifiedDateTime,file&$orderby=lastModifiedDateTime desc&$top={max_files}"
    )
    response = _graph_get(list_url, token)
    items = response.json().get("value", [])
    log_items = [
        item for item in items
        if str(item.get("name", "")).lower().endswith((".csv", ".txt")) and item.get("file") is not None
    ][:max_files]
    if not log_items:
        raise DataSourceError("No CSV or TXT activity files were found in the SharePoint folder.")
    frames: list[pd.DataFrame] = []
    for item in log_items:
        item_id = quote(str(item["id"]), safe="")
        content = bytes(_graph_get(f"{_drive_url(config)}/items/{item_id}/content", token).content)
        frame = _parse_activity_file(str(item["name"]), content)
        frame["source_file"] = str(item["name"])
        frames.append(frame)
    return validate_activity(pd.concat(frames, ignore_index=True))


def load_demo_dashboard() -> DashboardData:
    return DashboardData(
        operations=load_demo_operations(),
        flows=load_demo_flow_status(),
        activities=load_demo_activity(),
        source_label="Built-in demo",
    )


def load_connected_dashboard() -> DashboardData:
    messages: list[str] = []
    fallback_count = 0
    try:
        operations = load_databricks_operations()
    except (DataSourceError, ValueError) as error:
        fallback_count += 1
        messages.append(f"Databricks: {error}")
        operations = load_demo_operations()

    try:
        flows = load_sharepoint_flow_status()
    except (DataSourceError, ValueError) as error:
        fallback_count += 1
        messages.append(f"Flow status: {error}")
        flows = load_demo_flow_status()

    try:
        activities = load_sharepoint_activity()
    except (DataSourceError, ValueError) as error:
        fallback_count += 1
        messages.append(f"Live activity: {error}")
        activities = load_demo_activity()

    source_label = "Databricks + SharePoint" if fallback_count == 0 else f"Connected | {fallback_count} demo fallback"
    return DashboardData(
        operations=operations,
        flows=flows,
        activities=activities,
        source_label=source_label,
        source_messages=tuple(messages),
    )
