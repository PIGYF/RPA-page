# AI Operations Report（Streamlit 本地版）

这是一个不依赖 Node.js 的本地 SAP / RPA 运营报告。目标电脑需要 64 位 Python 3.10 或更高版本。页面默认使用内置 Demo 数据，也可以分别连接 Databricks 和 SharePoint。

## 本机启动

双击 `start_dashboard.bat`。脚本会检查 Python、创建项目内的 `.venv`、安装依赖并打开 `http://localhost:8501`。

## 数据源架构

三个页面区域使用相互独立的数据源。任何一路连接失败时，只对对应区域使用 Demo 回退，不影响其他区域。

| 页面区域 | 数据源 | 缓存时间 |
| --- | --- | --- |
| Total SAP Operations 与 7 天趋势 | Databricks SQL | 55 秒 |
| Flow Status | SharePoint Excel | 30 秒 |
| Live Activity | SharePoint CSV / TXT | 20 秒 |

在侧边栏的 `Data mode` 中选择：

- `Demo`：三块区域都使用本地演示数据。
- `Connected sources`：分别连接 Databricks、SharePoint Excel 和 SharePoint 日志目录；未配置或失败的区域自动使用 Demo 回退。

## Databricks 数据格式

`.streamlit/secrets.toml` 中的 `operations_query` 至少返回：

| 字段 | 含义 |
| --- | --- |
| `event_time` | 操作发生时间或汇总日期 |
| `operation_count` | 对应时间的操作量 |

查询至少覆盖最近 7 天。页面中的 Total 是当前查询结果的总和，因此正式使用前需要确认它代表“累计总量”还是“所选时间范围总量”。

## SharePoint Flow Status Excel

Excel 工作表至少需要以下字段：

| 字段 | 是否必填 | 含义 |
| --- | --- | --- |
| `flow_name` | 是 | 流程名称 |
| `status` | 是 | Running、Paused、Completed、Failed 等 |
| `last_run` | 是 | 最后运行时间 |
| `operation_count` | 否 | 最近一次或当日处理量 |
| `attention_required` | 否 | 是否需要关注 |
| `attention_reason` | 否 | 需要关注的原因 |

支持常见别名，例如 `flow`、`process`、`last_run_time`、`needs_attention`。

## SharePoint Live Activity 日志

SharePoint 文件夹内可放置 CSV 或以分隔符组织的 TXT 文件。每个文件至少需要：

| 字段 | 是否必填 | 含义 |
| --- | --- | --- |
| `event_time` | 是 | 事件时间 |
| `flow_name` | 是 | 脚本或流程名称 |
| `status` | 是 | Running、Completed、Failed 等 |
| `event_type` | 否 | flow_started、flow_completed 等 |
| `operation_count` | 否 | 此次处理数量 |
| `message` | 否 | 日志说明 |

推荐目录结构：

```text
/AI-Operations/Activity/
  LU04_321-2026-07-15.csv
  LB10_914-2026-07-15.csv
```

页面只读取最近修改的若干个文件，数量由 `activity_max_files` 控制。TXT 必须是逗号、制表符或其他统一分隔符格式；不建议使用完全无结构的自然语言日志。

## 连接配置

复制 `.streamlit/secrets.toml.example` 为 `.streamlit/secrets.toml`，填写 Databricks 和 Microsoft Entra / SharePoint 配置。真实密钥不得提交到 Git。

当前 SharePoint 连接使用 Microsoft Graph 的应用身份认证，适合无人值守的本地展示电脑。管理员需要为应用授予所需的最小只读权限。

## 部署到另一台电脑

### 目标电脑可以联网

1. 复制整个项目，但不要复制 `.venv`。
2. 安装 Python 3.10+，安装时勾选 `Add Python to PATH`。
3. 配置 `.streamlit/secrets.toml`。
4. 双击 `start_dashboard.bat`。

### 目标电脑不能访问 Python 包源

1. 在 Windows/Python 架构一致且可联网的电脑上运行 `prepare_offline_package.bat`。
2. 将生成的 `offline_packages` 与项目一起复制到目标电脑。
3. 配置 `.streamlit/secrets.toml`。
4. 双击 `start_dashboard.bat`。

目标电脑即使使用离线依赖包，仍必须能够通过公司网络访问 Databricks、Microsoft 登录服务和 SharePoint，才能显示实时数据。

## Chat with Wally

首页目前只展示建议问题和 `Chat with me` 入口，尚未绑定跳转链接。未来可以让对话页同时使用三路数据：Databricks 回答历史操作问题，SharePoint Excel 回答流程状态，SharePoint 日志回答最新活动。

## 替换机器人 GIF

将动态图命名为 `ai-employee.gif` 并放入 `assets` 文件夹。页面会优先加载 GIF；文件不存在时自动回退到 `assets/ai-operator.png`。

## 主要文件

- `app.py`：Streamlit 页面、数据源选择和逐区域降级。
- `dashboard_data.py`：三类数据校验器、Demo 数据和真实连接器。
- `.streamlit/secrets.toml.example`：Databricks 与 SharePoint 配置模板。
- `start_dashboard.bat`：本机启动脚本。
- `prepare_offline_package.bat`：离线依赖包制作脚本。
