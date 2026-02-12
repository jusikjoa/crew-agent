"""
KAIST 졸업시뮬레이션 도구
"""
import json
import time
from typing import Optional
from pathlib import Path

from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

COOKIE_PATH = Path(__file__).parent / ".kaist_cookies.json"
SSO_URL = "https://sso.kaist.ac.kr/auth/kaist/user/login/view?agt_id=kaist-prod-portal&agt_url=https://portal.kaist.ac.kr&user_id="
ERP_URL = "https://erp.kaist.ac.kr/com/lgin/SsoCtr/initPageWork.do?&menuId=M110571&requestTimeStr=1770868448360"


class GraduationSimTool(BaseTool):
    """KAIST 졸업시뮬레이션 실행 도구"""

    name: str = "graduation_simulation"
    description: str = (
        "KAIST 학사시스템에 접속하여 졸업시뮬레이션을 실행합니다. "
        "졸업에 필요한 학점, 이수/미이수 과목, 졸업 가능 여부 등을 확인할 수 있습니다."
    )

    def _run(
        self,
        query: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False, channel="chrome")
                context = browser.new_context()
                page = context.new_page()

                # ── Step 1: 카이스트 포탈 SSO 로그인 ──
                print("\n[Step 1] SSO 로그인 페이지 열기...")
                page.goto(SSO_URL, timeout=30000)
                print("[Step 1] 브라우저에서 로그인해주세요 (ID/PW + 2FA)")
                print("[Step 1] 최대 3분 대기...\n")

                # 로그인 완료 대기: SSO 페이지를 벗어나면 성공
                self._wait_for_url_not_contains(page, "sso.kaist.ac.kr", timeout=180)
                print("[Step 1] 로그인 성공!\n")

                # ── Step 2: 카이스트 학사사이트(ERP) 접속 ──
                print("[Step 2] 학사사이트 접속 중...")
                page.goto(ERP_URL, timeout=30000)
                # ERP 페이지 로딩 대기
                self._wait_for_url_contains(page, "erp.kaist.ac.kr", timeout=30)
                page.wait_for_timeout(5000)
                print(f"[Step 2] 학사사이트 접속 완료! URL: {page.url}\n")

                # 쿠키 저장
                cookies = context.cookies()
                with open(COOKIE_PATH, "w") as f:
                    json.dump(cookies, f)

                # ── Step 3: "학사" 메뉴 클릭 ──
                print("[Step 3] '학사' 메뉴 클릭...")
                self._click(page, "학사")
                page.wait_for_timeout(2000)

                # ── Step 4: "졸업" 메뉴 클릭 ──
                print("[Step 4] '졸업' 메뉴 클릭...")
                self._click(page, "졸업")
                page.wait_for_timeout(2000)

                # ── Step 5: "졸업시뮬레이션" 선택 ──
                print("[Step 5] '졸업시뮬레이션' 메뉴 클릭...")
                self._click(page, "졸업시뮬레이션")
                page.wait_for_timeout(3000)

                # ── Step 6~8: 다이얼로그 자동 수락 + 실행 버튼 클릭 ──
                # "모의졸업사정을 실행하시겠습니까?" → 확인
                # "처리되었습니다" → 확인
                page.on("dialog", lambda d: d.accept())

                print("[Step 6] '졸업시뮬레이션 실행' 버튼 클릭...")
                self._click(page, "졸업시뮬레이션 실행")
                page.wait_for_timeout(10000)

                # ── Step 9: 결과 스크래핑 ──
                print("[Step 9] 결과 수집 중...\n")
                result = self._scrape(page)

                browser.close()
                return result

        except PlaywrightTimeout:
            return "오류: 시간이 초과되었습니다."
        except Exception as e:
            return f"오류: {str(e)}"

    def _wait_for_url_contains(self, page, keyword: str, timeout: int = 60):
        """URL에 keyword가 포함될 때까지 폴링 대기"""
        start = time.time()
        while time.time() - start < timeout:
            if keyword in page.url:
                return
            page.wait_for_timeout(1000)
        raise PlaywrightTimeout(f"{timeout}초 내에 '{keyword}' URL에 도달하지 못했습니다.")

    def _wait_for_url_not_contains(self, page, keyword: str, timeout: int = 60):
        """URL에서 keyword가 사라질 때까지 폴링 대기"""
        start = time.time()
        while time.time() - start < timeout:
            if keyword not in page.url:
                return
            page.wait_for_timeout(1000)
        raise PlaywrightTimeout(f"{timeout}초 내에 '{keyword}' URL을 벗어나지 못했습니다.")

    def _click(self, page, text: str):
        """모든 프레임에서 텍스트가 포함된 요소를 찾아 클릭"""
        for frame in page.frames:
            for tag in ["a", "button", "span", "input", "li", "div"]:
                try:
                    el = frame.locator(f'{tag}:has-text("{text}")').first
                    if el.is_visible(timeout=1000):
                        el.click()
                        print(f"  → '{text}' 클릭 완료 (frame: {frame.name or 'main'})")
                        return
                except Exception:
                    continue
        print(f"  → '{text}' 요소를 찾지 못했습니다.")

    def _scrape(self, page) -> str:
        """모든 프레임에서 테이블 데이터 수집"""
        results = ["=== KAIST 졸업시뮬레이션 결과 ===\n"]

        for frame in page.frames:
            try:
                tables = frame.locator("table")
                count = tables.count()
            except Exception:
                continue

            for i in range(count):
                try:
                    rows = tables.nth(i).locator("tr")
                    row_count = rows.count()
                    if row_count == 0:
                        continue

                    table_data = []
                    for j in range(row_count):
                        cells = rows.nth(j).locator("th, td")
                        texts = []
                        for k in range(cells.count()):
                            t = cells.nth(k).inner_text().strip()
                            if t:
                                texts.append(t)
                        if texts:
                            table_data.append(" | ".join(texts))

                    if table_data:
                        results.append("---")
                        results.append("\n".join(table_data))
                        results.append("")
                except Exception:
                    continue

        if len(results) <= 1:
            for frame in page.frames:
                try:
                    text = frame.locator("body").inner_text(timeout=3000).strip()
                    if text:
                        lines = [l.strip() for l in text.splitlines() if l.strip()]
                        results.append("\n".join(lines[:100]))
                        break
                except Exception:
                    continue

        return "\n".join(results)

    async def _arun(self, query: str = "", run_manager=None) -> str:
        return self._run(query, run_manager)
