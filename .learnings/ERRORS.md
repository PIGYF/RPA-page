## [ERR-20260715-001] imagegen_chroma_removal

**Logged**: 2026-07-15T00:00:00+08:00
**Priority**: low
**Status**: resolved
**Area**: frontend

### Summary
The system Python launcher did not have Pillow for the image-generation chroma-key helper.

### Error
```
Error: Pillow is required for chroma-key removal.
```

### Context
- Attempted to process `assets/ai-operator-chroma.png` with the installed imagegen helper.
- Windows system Python was available, but its environment did not include Pillow.

### Suggested Fix
Use the bundled Codex workspace Python runtime for image post-processing instead of modifying the user's system Python.

### Metadata
- Reproducible: yes
- Related Files: assets/ai-operator-chroma.png

### Resolution
- **Resolved**: 2026-07-15T00:00:00+08:00
- **Notes**: Switched to the bundled workspace Python runtime, which contains the required image libraries.

---

## [ERR-20260716-016] ffmpeg_not_available

**Logged**: 2026-07-16T18:10:00+08:00
**Priority**: low
**Status**: resolved
**Area**: tooling

### Summary
System `ffmpeg` and `ffprobe` were unavailable for the requested video conversion.

### Resolution
Used the workspace Python environment with OpenCV, Pillow, and imageio-ffmpeg for local media processing.

---

## [ERR-20260716-017] opencv_unicode_video_path

**Logged**: 2026-07-16T18:13:00+08:00
**Priority**: low
**Status**: resolved
**Area**: tooling

### Summary
OpenCV could not open the MP4 from its Unicode-heavy Windows source path.

### Resolution
Copied the input to a temporary ASCII-only path before decoding frames.

---

## [ERR-20260716-018] animated_webp_slow_encode

**Logged**: 2026-07-16T18:18:00+08:00
**Priority**: low
**Status**: resolved
**Area**: tooling

### Summary
The first full-frame high-effort animated WebP encode exceeded the practical processing window.

### Resolution
Encoded a 12 FPS, 61-frame optimized WebP with a lower compression effort; final size is about 1.55 MB.

---

## [ERR-20260715-004] browser_screenshot_api

**Logged**: 2026-07-15T21:24:00+08:00
**Priority**: low
**Status**: resolved
**Area**: tests

### Summary
Used the wrong screenshot method during the first in-app browser capture.

### Error
```
tab.playwright.screenshot is not a function
```

### Context
- Browser documentation exposes screenshots on `tab.screenshot`, not `tab.playwright`.

### Suggested Fix
Use `tab.screenshot({fullPage: ...})` and emit the returned bytes.

### Metadata
- Reproducible: yes
- Related Files: app.py

### Resolution
- **Resolved**: 2026-07-15T21:24:00+08:00
- **Notes**: Repeated capture successfully with `tab.screenshot`.

---

## [ERR-20260715-003] streamlit_first_run_prompt

**Logged**: 2026-07-15T21:22:26+08:00
**Priority**: high
**Status**: resolved
**Area**: config

### Summary
A fresh Streamlit installation paused for the onboarding email prompt instead of starting unattended.

### Error
```
Welcome to Streamlit! ... Email:
```

### Context
- Started the app from a new project-local virtual environment.
- This would block the destination computer's first launch.

### Suggested Fix
Ship `.streamlit/config.toml` with telemetry disabled and headless local-server settings.

### Metadata
- Reproducible: yes
- Related Files: .streamlit/config.toml, start_dashboard.bat

### Resolution
- **Resolved**: 2026-07-15T21:22:26+08:00
- **Notes**: Added committed Streamlit settings for unattended local startup.

---

## [ERR-20260715-002] streamlit_runtime_probe

**Logged**: 2026-07-15T00:00:00+08:00
**Priority**: low
**Status**: resolved
**Area**: tests

### Summary
The bundled workspace Python includes image tooling but does not include Streamlit.

### Error
```
ModuleNotFoundError: No module named 'streamlit'
```

### Context
- Probed the bundled runtime before browser verification.
- The application itself is intended to run from a project-local `.venv`.

### Suggested Fix
Create the same `.venv` used by `start_dashboard.bat` and test against it.

### Metadata
- Reproducible: yes
- Related Files: requirements.txt, start_dashboard.bat

### Resolution
- **Resolved**: 2026-07-15T00:00:00+08:00
- **Notes**: Verification moved to the project-local virtual environment.

---
## [ERR-20260715-005] browser_viewport_api

**Logged**: 2026-07-15T22:10:00+08:00
**Priority**: low
**Status**: resolved
**Area**: tests

### Summary
The browser tab viewport method was called on the Playwright helper instead of the tab binding.

### Error
```
dashboardTab.playwright.setViewportSize is not a function
dashboardTab.playwright.reload is not a function
```

### Context
- Attempted to set a 1536×864 viewport before visual QA of the Streamlit dashboard.
- DOM helpers are exposed on `tab.playwright`, while viewport sizing belongs to the tab binding.
- Page reload is also a tab-level method, not a `tab.playwright` helper.

### Suggested Fix
Use `await browser.capabilities.get("viewport")`, then call the capability's `set({ width, height })` method. Reload with `tab.reload()`.

### Metadata
- Reproducible: yes
- Related Files: app.py

### Resolution
- **Resolved**: 2026-07-15T22:10:00+08:00
- **Notes**: Continued verification with the browser viewport capability API.

---
## [ERR-20260715-006] image_forwarding_callback

**Logged**: 2026-07-15T22:36:00+08:00
**Priority**: low
**Status**: resolved
**Area**: tests

### Summary
Passing the image output helper directly to `Array.forEach` forwarded the array index as an invalid image detail argument.

### Error
```
image detail must be a string when provided
```

### Context
- Forwarded two local `view_image` results from an orchestration call.
- `forEach(image)` passes `(item, index)`, so the numeric index became the helper's second parameter.

### Suggested Fix
Forward results with `for (const item of results) image(item)` or `results.forEach(item => image(item))`.

### Metadata
- Reproducible: yes
- Related Files: app.py

### Resolution
- **Resolved**: 2026-07-15T22:36:00+08:00
- **Notes**: Repeated the visual comparison using an explicit one-argument loop.

---
## [ERR-20260715-007] stale_browser_tab_binding

**Logged**: 2026-07-15T22:48:00+08:00
**Priority**: low
**Status**: resolved
**Area**: tests

### Summary
A browser tab binding persisted across turns after the underlying tab had been reclaimed.

### Error
```
Tab not found: 4. Existing tabs: none
```

### Context
- Reused the prior dashboard tab binding for visual verification after a new UI change.
- The browser binding remained valid, but the tab binding was stale.

### Suggested Fix
Discard the stale tab binding, open or claim a fresh localhost tab from the existing browser binding, and continue without resetting the browser runtime.

### Metadata
- Reproducible: no
- Related Files: app.py

### Resolution
- **Resolved**: 2026-07-15T22:48:00+08:00
- **Notes**: Visual QA continued with a fresh tab binding.

---
## [ERR-20260715-008] browser_viewport_compositor_artifact

**Logged**: 2026-07-15T22:52:00+08:00
**Priority**: low
**Status**: resolved
**Area**: tests

### Summary
Capturing immediately after a browser viewport override produced black compositor regions in the screenshot.

### Error
```
Screenshot contained large black patches although DOM metrics and the previous viewport render were valid.
```

### Context
- Changed the local dashboard viewport from 1280×720 to 1536×864.
- Captured after a short delay without reloading the tab at the new size.

### Suggested Fix
Reload the tab after applying the viewport override, wait for the page and compositor to settle, then capture a fresh screenshot.

### Metadata
- Reproducible: unknown
- Related Files: app.py

### Resolution
- **Resolved**: 2026-07-15T22:52:00+08:00
- **Notes**: Repeated capture after reload and a longer render wait.

---
## [ERR-20260715-009] windows_python_app_alias

**Logged**: 2026-07-15T23:00:00+08:00
**Priority**: low
**Status**: resolved
**Area**: tests

### Summary
The bare `python` command resolved to the Windows Store app alias instead of the project runtime.

### Error
```
Python was not found; run without arguments to install from the Microsoft Store.
```

### Context
- Attempted to run `python -m py_compile app.py` after a dashboard layout update.
- The project already has a valid `.venv\Scripts\python.exe` runtime.

### Suggested Fix
Use the project-local virtual environment explicitly for Python verification commands.

### Metadata
- Reproducible: yes
- Related Files: app.py, .venv\Scripts\python.exe

### Resolution
- **Resolved**: 2026-07-15T23:00:00+08:00
- **Notes**: Switched the syntax check to `.venv\Scripts\python.exe`.

---
## [ERR-20260715-010] browser_load_state_and_capture_timeout

**Logged**: 2026-07-15T23:06:00+08:00
**Priority**: low
**Status**: resolved
**Area**: tests

### Summary
The in-app browser rejected `networkidle` and a later cosmetic screenshot capture timed out after DOM verification had completed.

### Error
```
playwright_wait_for_load_state does not support networkidle
js execution timed out; kernel reset
```

### Context
- Verified the updated local Streamlit dashboard after restarting the service.
- DOM checks had already confirmed LT01/LU04/LB10 consistency, five activity rows, three flow rows, and a 1440x900 no-scroll layout.

### Suggested Fix
Use the supported `domcontentloaded` state plus a targeted DOM assertion; avoid an additional screenshot-only wait after authoritative layout checks pass.

### Metadata
- Reproducible: unknown
- Related Files: app.py, dashboard_data.py

### Resolution
- **Resolved**: 2026-07-15T23:06:00+08:00
- **Notes**: Accepted the completed DOM verification and the prior clean visual render as sufficient evidence.

---
## [ERR-20260715-011] github_cli_missing

**Logged**: 2026-07-15T23:20:00+08:00
**Priority**: high
**Status**: resolved
**Area**: infra

### Summary
The GitHub publish workflow cannot verify authentication or create a pull request because GitHub CLI is not installed.

### Error
```
gh : The term 'gh' is not recognized as the name of a cmdlet, function, script file, or operable program.
```

### Context
- Attempted the requested complete project publish from `main` to `origin`.
- Remote repository: `https://github.com/PIGYF/RPA-page.git`.
- No files were staged, committed, or pushed after the prerequisite check failed.

### Suggested Fix
Install GitHub CLI, run `gh auth login`, and resume the publish workflow.

### Metadata
- Reproducible: yes
- Related Files: app.py, dashboard_data.py

### Resolution
- **Resolved**: 2026-07-16T00:10:00+08:00
- **Notes**: Confirmed the machine's established Git for Windows setup uses the system-level Git Credential Manager; remote access and push dry-run both succeeded. The connected GitHub app can create the PR.

---
## [ERR-20260716-001] powershell_repository_summary_pipeline

**Logged**: 2026-07-16T00:05:00+08:00
**Priority**: low
**Status**: resolved
**Area**: infra

### Summary
A PowerShell pipeline placed directly after a `foreach` block was rejected as an empty pipe element.

### Error
```
An empty pipe element is not allowed.
```

### Context
- Attempted to summarize Git settings from other local projects.
- The command was read-only and made no repository changes.

### Suggested Fix
Collect objects into an array inside the loop, then pipe the completed array to `Format-Table`.

### Metadata
- Reproducible: yes
- Related Files: .git/config

### Resolution
- **Resolved**: 2026-07-16T00:06:00+08:00
- **Notes**: Re-ran the repository search with an intermediate array.

---
## [ERR-20260716-002] placeholder_secret_scan_false_positive

**Logged**: 2026-07-16T00:12:00+08:00
**Priority**: low
**Status**: resolved
**Area**: infra

### Summary
The staged secret scan flagged explicit example placeholders as potential credentials.

### Error
```
potential-secret-found
```

### Context
- Scanned `.streamlit/secrets.toml.example` before commit.
- Values were documented placeholders such as `replace-with-a-databricks-access-token`.

### Suggested Fix
Allow known placeholder prefixes while continuing to block populated credentials.

### Metadata
- Reproducible: yes
- Related Files: .streamlit/secrets.toml.example

### Resolution
- **Resolved**: 2026-07-16T00:13:00+08:00
- **Notes**: Manually inspected the example file and confirmed no real secrets were present before committing.

---
## [ERR-20260716-003] github_pr_creation_unavailable

**Logged**: 2026-07-16T00:18:00+08:00
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
The branch push succeeded, but automated draft PR creation was unavailable.

### Error
```
GitHub API error 403: Resource not accessible by integration
Browser is not available: extension
```

### Context
- Git Credential Manager successfully pushed `codex/ai-warehouse-dashboard`.
- The GitHub connector lacked PR write permission.
- The in-app browser was not signed in and the Chrome extension browser was unavailable.

### Suggested Fix
Sign in to GitHub on the prepared comparison URL or install/authenticate GitHub CLI, then create the draft PR.

### Metadata
- Reproducible: unknown
- Related Files: .git/config

---
## [ERR-20260715-011] ripgrep_powershell_regex_escape

**Logged**: 2026-07-15T23:12:00+08:00
**Priority**: low
**Status**: resolved
**Area**: tests

### Summary
A combined ripgrep regular expression was truncated by PowerShell quoting and became an unclosed group.

### Error
```
regex parse error: unclosed group
```

### Context
- Checked for stale unified-data references after splitting dashboard data sources.
- The expression mixed escaped parentheses and quoted bracket syntax in one shell argument.

### Suggested Fix
Use multiple fixed-string `rg -F -e` patterns for mechanical stale-reference checks.

### Metadata
- Reproducible: yes
- Related Files: app.py, dashboard_data.py

### Resolution
- **Resolved**: 2026-07-15T23:12:00+08:00
- **Notes**: Repeated the check with fixed-string patterns.

---
## [ERR-20260715-012] browser_webview_attach_timeout

**Logged**: 2026-07-15T23:18:00+08:00
**Priority**: low
**Status**: resolved
**Area**: tests

### Summary
The browser role-based click timed out while the Browser webview was temporarily detached.

### Error
```
Timed out waiting for the Browser webview to attach for this browser-use page
TypeError: target.click is not a function
```

### Context
- Attempted to select the Streamlit `Connected sources` radio during fallback verification.
- The same tab had just completed DOM inspection and screenshot capture successfully.

### Suggested Fix
Retry the supported locator click after the tab settles. Browser evaluation DOM wrappers are inspection-oriented and do not expose native `Element.click()`.

### Metadata
- Reproducible: no
- Related Files: app.py

### Resolution
- **Resolved**: 2026-07-15T23:18:00+08:00
- **Notes**: Continued the fallback test with a fresh tab and the supported locator API.

---
## [ERR-20260715-013] streamlit_collapsed_sidebar_control_test

**Logged**: 2026-07-15T23:23:00+08:00
**Priority**: low
**Status**: resolved
**Area**: tests

### Summary
Browser automation could inspect but could not change a radio inside Streamlit's initially collapsed sidebar.

### Error
```
Click did not change checked state to true
No element matched selector [data-testid="stSidebarCollapsedControl"]
```

### Context
- Attempted to switch from Demo to Connected sources for fallback verification.
- Sidebar content was present in the accessibility snapshot but its visual control was not interactable.

### Suggested Fix
Keep browser verification for the rendered default mode and move connection/fallback orchestration into a pure callable data-layer function that can be tested directly.

### Metadata
- Reproducible: yes
- Related Files: app.py, dashboard_data.py

### Resolution
- **Resolved**: 2026-07-15T23:23:00+08:00
- **Notes**: Added a directly testable connected-dashboard loader with independent fallbacks.

---
## [ERR-20260715-014] streamlit_secrets_fallback_exception

**Logged**: 2026-07-15T23:26:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: backend

### Summary
The connected-source fallback test did not catch Streamlit's missing-secrets exception, and a cache spinner obscured it in bare-mode tests.

### Error
```
streamlit.errors.StreamlitSecretNotFoundError: No secrets found
streamlit.errors.NoSessionContext: Cursor is not set
```

### Context
- Called the connected-dashboard loader directly without a `.streamlit/secrets.toml` file.
- SharePoint configuration only caught `KeyError`; real Streamlit uses `StreamlitSecretNotFoundError` when no secrets file exists.
- Text spinners on cached loaders require a Streamlit session during exception handling.

### Suggested Fix
Catch `StreamlitSecretNotFoundError` in configuration access and disable cache spinners on data-layer functions that must be directly testable.

### Metadata
- Reproducible: yes
- Related Files: dashboard_data.py

### Resolution
- **Resolved**: 2026-07-15T23:26:00+08:00
- **Notes**: Missing credentials now produce a normal `DataSourceError` and per-source Demo fallback.

---
## [ERR-20260715-015] windows_status_label_unicode

**Logged**: 2026-07-15T23:29:00+08:00
**Priority**: low
**Status**: resolved
**Area**: frontend

### Summary
A middle-dot character in an internal source-status label was decoded inconsistently in the Windows test environment.

### Error
```
AssertionError: Connected бд 3 demo fallback
```

### Context
- Asserted the connected-dashboard fallback label in a PowerShell-launched Python process.
- Data fallback behavior itself completed correctly.

### Suggested Fix
Use ASCII separators for internal source-status labels that must be portable across Windows locale and console configurations.

### Metadata
- Reproducible: yes
- Related Files: dashboard_data.py

### Resolution
- **Resolved**: 2026-07-15T23:29:00+08:00
- **Notes**: Replaced middle-dot separators with ASCII text.

---
## [ERR-20260716-001] browser_plugin_cache_version

**Logged**: 2026-07-16T22:04:00+08:00
**Priority**: low
**Status**: resolved
**Area**: tests

### Summary
The cached Browser plugin version changed and invalidated a previously hardcoded skill path.

### Error
```
Cannot find path ...browser\26.707.72221\skills\control-in-app-browser\SKILL.md
```

### Context
- Prepared browser verification after connecting the dashboard to Databricks.
- The installed plugin cache had advanced to a newer version directory.

### Suggested Fix
Locate versioned plugin resources with `rg --files` instead of reusing a cached absolute version path across sessions.

### Metadata
- Reproducible: yes
- Related Files: app.py

### Resolution
- **Resolved**: 2026-07-16T22:04:00+08:00
- **Notes**: Located and loaded the current Browser plugin skill path.

---
## [ERR-20260716-B7Q] browser_tab_api_stale_binding

**Logged**: 2026-07-16T22:14:00+08:00
**Priority**: low
**Status**: resolved
**Area**: tests

### Summary
A stale browser binding exposed unsupported helper names during local UI verification.

### Error
```
browser.tabs.open is not a function
browser.fullDocumentation is not a function
```

### Context
- Attempted to reuse a browser global from an earlier session.
- The current Browser API uses `browser.tabs.new()` and `browser.documentation()`.

### Suggested Fix
Reselect the existing in-app browser with `agent.browsers.getForUrl(...)`, read its documentation, and claim an already-open matching tab.

### Metadata
- Reproducible: unknown
- Related Files: app.py
- See Also: ERR-20260716-001

### Resolution
- **Resolved**: 2026-07-16T22:14:00+08:00
- **Notes**: Reconnected to the in-app browser, claimed the localhost tab, and completed the 16:9 UI verification.

---
## [ERR-20260716-LTA] databricks_ltak_missing_qzeit

**Logged**: 2026-07-16T22:28:00+08:00
**Priority**: low
**Status**: resolved
**Area**: backend

### Summary
The project LTAK table contains `QDATU` but does not contain the expected `QZEIT` field.

### Error
```
[UNRESOLVED_COLUMN.WITH_SUGGESTION] QZEIT cannot be resolved.
```

### Context
- A two-row schema probe was used to identify the completion timestamp fields for Live Activity.
- Available time pairs include `BDATU/BZEIT`, `STDAT/STUZT`, and `ENDAT/ENUZT`.

### Suggested Fix
Build timestamps only from fields confirmed by `DESCRIBE TABLE`; use the confirmed completion pair after inspecting sample rows.

### Metadata
- Reproducible: yes
- Related Files: dashboard_data.py, .streamlit/secrets.toml

### Resolution
- **Resolved**: 2026-07-16T22:28:00+08:00
- **Notes**: Subsequent sampling was changed to actual LTAK date/time fields.

---
## [ERR-20260716-MOV] streamlit_databricks_screenshot_too_early

**Logged**: 2026-07-16T22:35:00+08:00
**Priority**: low
**Status**: resolved
**Area**: tests

### Summary
A 16:9 screenshot was captured before the two Databricks queries finished rendering.

### Error
```
Screenshot contained only the Streamlit background after a six-second wait.
```

### Context
- The connected dashboard now loads both operations and movement-detail queries.
- A viewport change plus reload invalidated the visible render while the queries were still running.

### Suggested Fix
Wait for the `Live Activity` DOM content rather than relying on a short fixed delay before capture.

### Metadata
- Reproducible: yes
- Related Files: app.py, dashboard_data.py
- See Also: ERR-20260715-010

### Resolution
- **Resolved**: 2026-07-16T22:35:00+08:00
- **Notes**: The final capture waits for the dashboard content after query completion.

---
## [ERR-20260716-IAB] browser_webview_attach_timeout

**Logged**: 2026-07-16T22:40:00+08:00
**Priority**: low
**Status**: resolved
**Area**: tests

### Summary
The claimed in-app browser tab briefly timed out while attaching after reload.

### Error
```
Timed out waiting for the Browser webview to attach for this browser-use page.
```

### Context
- Reloaded the localhost Streamlit dashboard before validating English copy.
- The tab was still present and the application process remained healthy.

### Suggested Fix
Reclaim the visible localhost tab and wait for its rendered content after the webview reconnects.

### Metadata
- Reproducible: unknown
- Related Files: app.py, dashboard_data.py
- See Also: ERR-20260716-B7Q

### Resolution
- **Resolved**: 2026-07-16T22:40:00+08:00
- **Notes**: Reconnected to the existing dashboard tab and completed visual verification.

---
## [ERR-20260716-ENG] databricks_refresh_browser_timeout

**Logged**: 2026-07-16T22:44:00+08:00
**Priority**: low
**Status**: resolved
**Area**: tests

### Summary
The browser verification cell exceeded its execution limit while a manual cache refresh ran Databricks queries.

### Error
```
js execution timed out; kernel reset
```

### Context
- Cleared Streamlit cache so translated movement labels would replace cached Chinese rows.
- A fixed wait plus page evaluation outlived the browser execution window.

### Suggested Fix
Reconnect after the reset and wait for the exact English record text to appear instead of sleeping for a fixed interval.

### Metadata
- Reproducible: unknown
- Related Files: app.py, dashboard_data.py
- See Also: ERR-20260716-MOV

### Resolution
- **Resolved**: 2026-07-16T22:44:00+08:00
- **Notes**: Switched final verification to a targeted English-copy condition.

---
## [ERR-20260716-GH] github_cli_not_installed

**Logged**: 2026-07-16T22:50:00+08:00
**Priority**: low
**Status**: resolved
**Area**: infra

### Summary
GitHub CLI was unavailable during a direct push-to-main request.

### Error
```
gh: The term 'gh' is not recognized.
```

### Context
- The user explicitly requested pushing all current changes directly to `main`.
- PR creation was not requested; the repository has a configured HTTPS origin.

### Suggested Fix
Use native Git for the direct commit and push workflow; install GitHub CLI only when PR or connector fallback operations are required.

### Metadata
- Reproducible: yes
- Related Files: .git/config

### Resolution
- **Resolved**: 2026-07-16T22:50:00+08:00
- **Notes**: Continued with native Git after verifying the remote and ignored secrets.

---
