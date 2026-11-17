"""main.py: Điểm khởi chạy chính của Dự án Kiểm thử Tự động (Page Object Model).

Báo cáo cuối kỳ: Kiểm thử tự động tính năng Xác thực (Đăng nhập / Đăng xuất)
Sử dụng mô hình Page Object Model (POM) kết hợp Selenium WebDriver.

Cách chạy:
    python main.py                                  # Chạy toàn bộ 19 test case
    python main.py --only LOGIN_001,LOGIN_004       # Chạy test case chỉ định
    python main.py --headless                       # Chạy chế độ ẩn trình duyệt
    python main.py --browser chrome                 # Chọn trình duyệt (chrome | edge | firefox)
"""
import argparse
import html
import os
import sys
from datetime import datetime
import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill

# Đảm bảo đường dẫn gốc được nạp vào sys.path
_BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)

from src.base.base_setup import BaseSetup, load_config, wake_server
from src.pages.home_page import HomePage
from src.testcases.test_signin import SignInTest


FILL_PASS = PatternFill("solid", fgColor="C6EFCE")
FILL_FAIL = PatternFill("solid", fgColor="FFC7CE")
FILL_BLOCKED = PatternFill("solid", fgColor="FFEB9C")
FONT_NAME = "Arial"


class TestCaseResult:
    def __init__(self, test_id: str, title: str, status: str, detail: str = "", screenshot: str = ""):
        self.id = test_id
        self.title = title
        self.status = status
        self.detail = detail
        self.screenshot = screenshot


def export_excel_report(src_excel_path: str, output_excel_path: str, results: list, meta: dict):
    """Cập nhật trạng thái và xuất báo cáo kết quả chi tiết ra file Excel."""
    if not os.path.exists(src_excel_path):
        return

    wb = openpyxl.load_workbook(src_excel_path)
    if "TestCases" in wb.sheetnames:
        ws = wb["TestCases"]
        id_col = 1
        status_col = 7
        actual_col = 8

        for c in ws[1]:
            val = str(c.value or "").strip().lower()
            if val == "test case id":
                id_col = c.column
            elif val == "status":
                status_col = c.column
            elif val == "actual result":
                actual_col = c.column

        by_id = {r.id: r for r in results}
        for row in range(2, ws.max_row + 1):
            tc_id = str(ws.cell(row, id_col).value or "").strip()
            if tc_id in by_id:
                res = by_id[tc_id]
                cell_status = ws.cell(row, status_col, res.status)
                cell_actual = ws.cell(row, actual_col, res.detail)

                cell_status.font = Font(name=FONT_NAME, bold=True)
                if res.status == "Pass":
                    cell_status.fill = FILL_PASS
                elif res.status == "Fail":
                    cell_status.fill = FILL_FAIL
                else:
                    cell_status.fill = FILL_BLOCKED

                cell_actual.font = Font(name=FONT_NAME)
                cell_actual.alignment = Alignment(wrap_text=True, vertical="top")

    # Tạo sheet Summary thống kê
    total = len(results)
    passed = sum(1 for r in results if r.status == "Pass")
    failed = sum(1 for r in results if r.status == "Fail")
    blocked = sum(1 for r in results if r.status == "Blocked")
    pass_rate = round(passed * 100 / total, 1) if total else 0.0

    if "Summary" in wb.sheetnames:
        del wb["Summary"]
    ws_sum = wb.create_sheet("Summary")
    summary_rows = [
        ("Project", "Automation Testing - Final Report"),
        ("Architecture", "Page Object Model (POM)"),
        ("Execution Time", meta["time"]),
        ("Target Website", meta["base_url"]),
        ("Browser", meta["browser"]),
        ("Total Test Cases", total),
        ("Pass", passed),
        ("Fail", failed),
        ("Blocked", blocked),
        ("Pass Rate (%)", pass_rate),
    ]
    for row in summary_rows:
        ws_sum.append(list(row))
    for r in ws_sum.iter_rows():
        r[0].font = Font(name=FONT_NAME, bold=True)
        r[1].font = Font(name=FONT_NAME)
    ws_sum.column_dimensions["A"].width = 24
    ws_sum.column_dimensions["B"].width = 50

    os.makedirs(os.path.dirname(output_excel_path), exist_ok=True)
    wb.save(output_excel_path)


def export_html_report(output_html_path: str, results: list, meta: dict):
    """Xuất báo cáo trực quan dạng trang web HTML chuyên nghiệp."""
    total = len(results)
    passed = sum(1 for r in results if r.status == "Pass")
    failed = sum(1 for r in results if r.status == "Fail")
    blocked = sum(1 for r in results if r.status == "Blocked")
    pass_rate = round(passed * 100 / total, 1) if total else 0.0

    rows = []
    for r in results:
        shot_html = (
            f"<a href='../screenshots/{os.path.basename(r.screenshot)}' target='_blank'>view</a>"
            if r.screenshot
            else "-"
        )
        rows.append(
            f"<tr class='{r.status}'>"
            f"<td><b>{html.escape(r.id)}</b></td>"
            f"<td>{html.escape(r.title)}</td>"
            f"<td><span class='badge badge-{r.status.lower()}'>{r.status}</span></td>"
            f"<td>{html.escape(r.detail)}</td>"
            f"<td style='text-align:center'>{shot_html}</td>"
            f"</tr>"
        )

    doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Final Automation Testing Report - Page Object Model</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 24px; background: #f8fafc; color: #1e293b; }}
    .container {{ max-width: 1200px; margin: auto; background: #ffffff; padding: 32px; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.06); }}
    .header {{ border-bottom: 2px solid #e2e8f0; padding-bottom: 16px; margin-bottom: 24px; }}
    .header h1 {{ margin: 0 0 8px 0; color: #0f172a; font-size: 26px; }}
    .header p {{ margin: 0; color: #64748b; font-size: 14px; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 28px; }}
    .card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; text-align: center; }}
    .card .title {{ font-size: 13px; color: #64748b; text-transform: uppercase; font-weight: 600; margin-bottom: 6px; }}
    .card .value {{ font-size: 26px; font-weight: 700; color: #0f172a; }}
    .card.pass .value {{ color: #16a34a; }}
    .card.fail .value {{ color: #dc2626; }}
    .card.blocked .value {{ color: #d97706; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
    th, td {{ padding: 12px 14px; font-size: 14px; text-align: left; border-bottom: 1px solid #e2e8f0; }}
    th {{ background: #f1f5f9; color: #475569; font-weight: 600; text-transform: uppercase; font-size: 12px; letter-spacing: 0.5px; }}
    tr:hover {{ background: #f8fafc; }}
    .badge {{ display: inline-block; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600; }}
    .badge-pass {{ background: #dcfce7; color: #15803d; }}
    .badge-fail {{ background: #fee2e2; color: #b91c1c; }}
    .badge-blocked {{ background: #fef3c7; color: #b45309; }}
    a {{ color: #2563eb; text-decoration: none; font-weight: 500; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Final Project: Automated Testing Report</h1>
      <p>Architecture: <b>Page Object Model (POM)</b> &middot; Target: <b>{html.escape(meta['base_url'])}</b> &middot; Browser: <b>{html.escape(meta['browser'])}</b> &middot; Execution: <b>{html.escape(meta['time'])}</b></p>
    </div>

    <div class="cards">
      <div class="card"><div class="title">Total Cases</div><div class="value">{total}</div></div>
      <div class="card pass"><div class="title">Passed</div><div class="value">{passed}</div></div>
      <div class="card fail"><div class="title">Failed</div><div class="value">{failed}</div></div>
      <div class="card blocked"><div class="title">Blocked</div><div class="value">{blocked}</div></div>
      <div class="card"><div class="title">Pass Rate</div><div class="value">{pass_rate}%</div></div>
    </div>

    <h2>Test Execution Details</h2>
    <table>
      <thead>
        <tr>
          <th style="width: 120px;">Test ID</th>
          <th style="width: 260px;">Title</th>
          <th style="width: 100px;">Status</th>
          <th>Actual Result / Details</th>
          <th style="width: 90px; text-align: center;">Evidence</th>
        </tr>
      </thead>
      <tbody>
        {''.join(rows)}
      </tbody>
    </table>
  </div>
</body>
</html>"""

    os.makedirs(os.path.dirname(output_html_path), exist_ok=True)
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(doc)


def main():
    parser = argparse.ArgumentParser(description="Final Project - Automated Testing System (Page Object Model)")
    parser.add_argument("--browser", choices=["chrome", "firefox", "edge"], help="Select browser")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--only", help="Run specific test case IDs, comma-separated (e.g. LOGIN_001,LOGIN_004)")
    args = parser.parse_args()

    cfg = load_config()
    base_url = cfg.get("base_url", "https://e-commerce-for-testing.onrender.com")
    browser = args.browser or cfg.get("browser", "chrome")
    headless = args.headless or cfg.get("headless", False)
    tmo = cfg.get("timeouts", {})

    # Đánh thức server Render trước khi chạy test
    wake_server(base_url, tmo.get("page_load", 90))

    base_setup = BaseSetup(browser=browser, headless=headless)
    driver = base_setup.init_driver()

    # Thu thập tất cả phương thức test từ class SignInTest
    test_methods = [m for m in dir(SignInTest) if m.startswith("test_LOGIN_")]
    test_methods.sort()

    if args.only:
        wanted = {x.strip().upper() for x in args.only.split(",")}
        test_methods = [
            m for m in test_methods
            if any(w in m.upper() for w in wanted)
        ]

    if not test_methods:
        print("No matching test cases found to run.")
        base_setup.quit_driver()
        return 1

    screenshots_dir = os.path.join(_BASE_DIR, "test-output", "screenshots")
    reports_dir = os.path.join(_BASE_DIR, "test-output", "reports")
    os.makedirs(screenshots_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)

    results = []
    print(f"\n=======================================================")
    print(f" FINAL AUTOMATION TESTING - PAGE OBJECT MODEL (POM)")
    print(f" Target  : {base_url}")
    print(f" Browser : {browser} (Headless: {headless})")
    print(f" Total   : {len(test_methods)} test cases")
    print(f"=======================================================\n")

    try:
        for i, method_name in enumerate(test_methods, 1):
            parts = method_name.split("_", 2)
            tc_id = f"{parts[1]}_{parts[2].split('_')[0]}" if len(parts) >= 3 else method_name
            raw_title = parts[2].replace("_", " ").title() if len(parts) >= 3 else method_name

            base_setup.reset_session()
            home_page = HomePage(driver, base_url)
            home_page.open_home_page()
            signin_page = home_page.click_header_login()

            test_instance = SignInTest()
            test_instance.driver = driver
            test_instance.base_setup = base_setup
            test_instance.home_page = home_page
            test_instance.signin_page = signin_page
            test_instance.admin_email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
            test_instance.admin_pass = os.environ.get("ADMIN_PASS", "Admin@12345")

            status = "Pass"
            detail = f"Passed successfully | Final URL: {driver.current_url}"
            shot_file = os.path.join(screenshots_dir, f"{tc_id}.png")

            try:
                getattr(test_instance, method_name)()
            except AssertionError as e:
                status = "Fail"
                detail = f"Assertion failed: {e}"
            except Exception as e:
                status = "Blocked"
                detail = f"{type(e).__name__}: {str(e).splitlines()[0] if str(e) else ''}"

            try:
                driver.save_screenshot(shot_file)
            except Exception:
                shot_file = ""

            results.append(TestCaseResult(tc_id, raw_title, status, detail, shot_file))
            print(f"[{i:02d}/{len(test_methods)}] {tc_id}: {status} - {detail}")

    finally:
        base_setup.quit_driver()

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    meta = {"time": now_str, "base_url": base_url, "browser": browser}

    # Xuất báo cáo hoàn chỉnh vào test-output/
    src_excel = os.path.join(_BASE_DIR, "resources", "testdata", "login_keywords.xlsx")
    out_excel = os.path.join(reports_dir, "results.xlsx")
    out_html = os.path.join(reports_dir, "report.html")

    export_excel_report(src_excel, out_excel, results, meta)
    export_html_report(out_html, results, meta)

    total = len(results)
    passed = sum(1 for r in results if r.status == "Pass")
    failed = sum(1 for r in results if r.status == "Fail")
    blocked = sum(1 for r in results if r.status == "Blocked")
    pass_rate = round(passed * 100 / total, 1) if total else 0.0

    print(f"\n==================== EXECUTION SUMMARY ====================")
    print(f"Total: {total} | Passed: {passed} | Failed: {failed} | Blocked: {blocked} | Pass Rate: {pass_rate}%")
    print(f"HTML Report : {out_html}")
    print(f"Excel Report: {out_excel}")
    print(f"Screenshots : {screenshots_dir}")
    print("===========================================================")

    return 0 if (failed == 0 and blocked == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
