# AI Employee SAP Operations Center Dashboard

离线版 React + Vite + TypeScript SAP 运营中心看板，使用 **ECharts**、**纯 CSS**、本地 Mock 数据与本地图片占位资源，无 CDN / 外部依赖。

## Streamlit version (Databricks-ready)

The root-level Streamlit implementation is separate from the existing React app, so both can coexist.

### Start locally on Windows

Double-click `start_dashboard.bat`. It creates `.venv`, installs `requirements.txt`, starts Streamlit, and opens `http://localhost:8501`. The dashboard defaults to **Demo** data and refreshes every 60 seconds.

### Connect Databricks

1. Copy `.streamlit\secrets.toml.example` to `.streamlit\secrets.toml`.
2. Enter the SQL Warehouse hostname, HTTP path, access token, and query.
3. The query must return `event_time`, `operation_count`, `flow_name`, and `status`, with the aliases shown in the template.
4. Start the dashboard and select **Databricks** in the sidebar.

The sample query restricts data to the latest 24 hours. Keep a time predicate and query an aggregated or indexed source so the one-minute refresh remains fast.

### Move to another computer

Copy this project folder **without** `.venv` and without `.streamlit\secrets.toml`. Install Python 3.10+ on the destination machine, create its local `secrets.toml` from the template, and run `start_dashboard.bat`.

## 1. 运行 / Run

```bash
npm install
npm run dev
```

默认地址：`http://localhost:5173`

## 2. 构建 / Build

```bash
npm run build
```

构建产物输出到 `dist/`。

## 3. 主要目录 / Key Structure

```text
src/
  components/         UI 组件
  data/mockData.ts    全部 Mock 数据
  services/           API 形状的服务函数
  types/              严格 TypeScript 类型
  assets/             本地占位图资源
```

## 4. 图片替换 / AI Employee Image Replacement

组件会优先检测以下本地静态文件：

1. `public/ai-employee.gif`
2. `public/ai-employee.png`

若两者都不存在，则自动回退到 `src/assets/ai-employee-placeholder.svg`。

> 如需替换形象图，请仅放置本地资源，不要使用在线 URL。

## 5. Mock 数据替换 / Data Replacement

所有演示数据集中在：

`src/data/mockData.ts`

可替换内容包括：

- 7 / 14 / 30 天摘要卡片
- KPI
- ECharts 图表数据
- 流程状态
- AI 洞察
- 时间线
- 聊天快捷指令与回复

服务入口位于：

`src/services/dashboardService.ts`

如后续接真实 API，可直接替换这些函数的实现，保留组件层调用方式。

## 6. IIS / 静态部署说明

### 方式 A：纯静态站点

1. 执行 `npm run build`
2. 将 `dist` 目录内容发布到 IIS 站点根目录

### 方式 B：IIS 承载 SPA（推荐）

若使用前端路由回退（当前项目默认单页），建议在 IIS 配置 URL Rewrite，将所有非文件请求回退到 `index.html`。

示例 `web.config` 可按需加入到 `dist/`：

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="ReactRouter" stopProcessing="true">
          <match url=".*" />
          <conditions logicalGrouping="MatchAll">
            <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
            <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
          </conditions>
          <action type="Rewrite" url="/" />
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
</configuration>
```

## 7. 当前功能 / Included Features

- 全屏 1920×1080 风格布局，自适应桌面与缩小窗口
- 初始加载动画
- 7 / 14 / 30 天切换
- ECharts 业务量趋势图
- 流程卡片点击弹窗详情
- 分钟级自动刷新与手动刷新
- 快捷聊天指令与 Mock 回复
- 本地图片自动检测 PNG / GIF，缺失时回退占位图

## 8. 技术栈 / Stack

- React
- Vite
- TypeScript
- ECharts
- Pure CSS
