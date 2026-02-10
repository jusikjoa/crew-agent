"""
KAIST 졸업시뮬레이션 도구
Playwright를 사용하여 KAIST 학사시스템에 접속하고
졸업시뮬레이션을 실행하여 결과를 반환합니다.
"""
import json
from typing import Optional
from pathlib import Path

from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# 쿠키 저장 경로
COOKIE_PATH = Path(__file__).parent / ".kaist_cookies.json"

# KAIST SSO 및 학사시스템 URL
SSO_LOGIN_URL = "https://sso.kaist.ac.kr/auth/kaist/user/login/view?agt_id=kaist-prod-portal&agt_url=https://portal.kaist.ac.kr&user_id="
ACADEMIC_MAIN_URL = "https://erp.kaist.ac.kr"
ERP_MAIN_URL = "https://erp.kaist.ac.kr/com/lgin/SsoCtr/initPageWork.do"


class GraduationSimTool(BaseTool):
    """KAIST 졸업시뮬레이션 실행 도구"""

    name: str = "graduation_simulation"
    description: str = (
        "KAIST 학사시스템에 접속하여 졸업시뮬레이션을 실행합니다. "
        "졸업에 필요한 학점, 이수/미이수 과목, 졸업 가능 여부 등을 확인할 수 있습니다. "
        "예: '졸업시뮬레이션 돌려줘', '졸업요건 확인해줘'"
    )

    def _run(
        self,
        query: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """졸업시뮬레이션 실행"""
        try:
            with sync_playwright() as p:
                # 브라우저 실행 (visible 모드)
                browser = p.chromium.launch(headless=False, channel="chrome")
                context = browser.new_context()

                # 저장된 쿠키가 있으면 로드
                if self._load_cookies(context):
                    page = context.new_page()
                    result = self._try_with_session(page)
                    if result:
                        browser.close()
                        return result
                    page.close()
                    context.clear_cookies()

                # 로그인 페이지 열기 - 사용자가 직접 로그인
                page = context.new_page()
                login_success = self._login(page)

                if not login_success:
                    browser.close()
                    return "오류: 로그인 시간이 초과되었습니다 (3분). 다시 시도해주세요."

                # 쿠키 저장
                self._save_cookies(context)

                # 졸업시뮬레이션 실행
                result = self._navigate_and_simulate(page)

                browser.close()
                return result

        except PlaywrightTimeout:
            return "오류: 페이지 로딩 시간이 초과되었습니다. 네트워크 상태를 확인해주세요."
        except Exception as e:
            return f"오류: 졸업시뮬레이션 실행 중 문제가 발생했습니다: {str(e)}"

    def _login(self, page) -> bool:
        """KAIST SSO 로그인 (사용자가 브라우저에서 직접 완료)"""
        try:
            print(f"\n[졸업시뮬레이션] SSO 페이지로 이동 중: {SSO_LOGIN_URL}")
            page.goto(SSO_LOGIN_URL, timeout=30000)
            page.wait_for_load_state("domcontentloaded", timeout=15000)
            print(f"[졸업시뮬레이션] 현재 URL: {page.url}")

            print("[졸업시뮬레이션] 브라우저에서 직접 로그인해주세요 (ID/PW + 2FA)")
            print("[졸업시뮬레이션] 로그인 완료 대기 중 (최대 3분)...\n")

            # 로그인 완료 대기 - SSO 페이지에서 벗어나면 성공
            page.wait_for_url(
                lambda url: "sso.kaist.ac.kr" not in url,
                timeout=180000  # 3분 대기
            )

            print("[졸업시뮬레이션] 로그인 성공!\n")
            return True

        except PlaywrightTimeout:
            print("[졸업시뮬레이션] 시간 초과")
            return False
        except Exception as e:
            print(f"[졸업시뮬레이션] 로그인 오류: {str(e)}")
            return False

    def _try_with_session(self, page) -> Optional[str]:
        """저장된 세션으로 직접 접근 시도"""
        try:
            page.goto(ERP_MAIN_URL, timeout=15000)
            page.wait_for_load_state("domcontentloaded", timeout=10000)

            # SSO 로그인 페이지로 리다이렉트되면 세션 만료
            if "sso.kaist.ac.kr" in page.url:
                return None

            return self._navigate_and_simulate(page)
        except Exception:
            return None

    def _navigate_and_simulate(self, page) -> str:
        """졸업시뮬레이션 페이지로 이동 및 실행"""
        try:
            # 졸업시뮬레이션 페이지로 이동
            print(f"[졸업시뮬레이션] 페이지 이동 중: {ERP_MAIN_URL}")
            page.goto(ERP_MAIN_URL, timeout=30000)
            page.wait_for_load_state("domcontentloaded", timeout=15000)
            print(f"[졸업시뮬레이션] 현재 URL: {page.url}")

            # SSO 로그인 페이지로 리다이렉트되었으면 세션 만료
            if "sso.kaist.ac.kr" in page.url:
                return None

            page.wait_for_timeout(3000)

            # Step 1: "졸업" 메뉴 클릭 - 모든 프레임에서 탐색
            print("[졸업시뮬레이션] '졸업' 메뉴 클릭 중...")
            grad_selectors = [
                'a:has-text("졸업")',
                'span:has-text("졸업")',
                'li:has-text("졸업")',
            ]
            grad_menu = self._click_in_any_frame(page, grad_selectors)
            if not grad_menu:
                return self._dump_all_frames(page, "'졸업' 메뉴를 찾지 못했습니다.")

            page.wait_for_timeout(2000)

            # Step 2: "졸업시뮬레이션" 하위 메뉴 클릭
            print("[졸업시뮬레이션] '졸업시뮬레이션' 메뉴 클릭 중...")
            sim_selectors = [
                'a:has-text("졸업시뮬레이션")',
                'span:has-text("졸업시뮬레이션")',
            ]
            sim_menu = self._click_in_any_frame(page, sim_selectors)
            if not sim_menu:
                return self._dump_all_frames(page, "'졸업시뮬레이션' 메뉴를 찾지 못했습니다.")

            page.wait_for_timeout(3000)

            # Step 3: confirm 다이얼로그 자동 수락 등록
            page.on("dialog", lambda dialog: dialog.accept())

            # Step 4: "졸업시뮬레이션 실행" 버튼 클릭
            print("[졸업시뮬레이션] '졸업시뮬레이션 실행' 버튼 클릭 중...")
            run_selectors = [
                'button:has-text("졸업시뮬레이션 실행")',
                'a:has-text("졸업시뮬레이션 실행")',
                'input[value*="졸업시뮬레이션 실행"]',
                'button:has-text("시뮬레이션 실행")',
                'button:has-text("실행")',
            ]
            run_btn = self._click_in_any_frame(page, run_selectors)
            if not run_btn:
                return self._dump_all_frames(page, "'졸업시뮬레이션 실행' 버튼을 찾지 못했습니다.")

            # Step 5: 시뮬레이션 결과 대기
            print("[졸업시뮬레이션] 시뮬레이션 실행 중... 결과 대기")
            page.wait_for_timeout(10000)

            # 결과 스크래핑 - 모든 프레임에서 테이블 탐색
            return self._scrape_results(page)

        except Exception as e:
            return f"졸업시뮬레이션 페이지 탐색 중 오류: {str(e)}"

    def _find_target_frame(self, page):
        """메인 페이지 또는 iframe 중 콘텐츠가 있는 프레임 반환"""
        frames = page.frames
        if len(frames) > 1:
            # 메인 프레임 외의 프레임 중 콘텐츠가 가장 많은 프레임 선택
            for frame in frames:
                if frame == page.main_frame:
                    continue
                try:
                    text = frame.locator("body").inner_text(timeout=2000)
                    if len(text.strip()) > 100:
                        return frame
                except Exception:
                    continue
        return page

    def _click_in_any_frame(self, page, selectors) -> bool:
        """메인 페이지 및 모든 iframe에서 셀렉터를 시도하여 요소 클릭"""
        for frame in page.frames:
            for sel in selectors:
                try:
                    el = frame.locator(sel).first
                    if el.is_visible(timeout=1000):
                        print(f"  → 클릭 (frame: {frame.name or 'main'}): {sel}")
                        el.click()
                        return True
                except Exception:
                    continue
        return False

    def _dump_all_frames(self, page, error_msg) -> str:
        """디버깅용: 모든 프레임의 내용을 출력"""
        result = [error_msg, f"현재 URL: {page.url}", f"프레임 수: {len(page.frames)}", ""]
        for i, frame in enumerate(page.frames):
            try:
                text = frame.locator("body").inner_text(timeout=3000)
                text = text.strip()[:1500]
                result.append(f"--- 프레임 {i} (name: {frame.name or 'main'}, url: {frame.url}) ---")
                result.append(text)
                result.append("")
            except Exception:
                result.append(f"--- 프레임 {i} (name: {frame.name or 'main'}) - 내용 읽기 실패 ---")
        return "\n".join(result)

    def _scrape_results(self, page, target=None) -> str:
        """시뮬레이션 결과 페이지 스크래핑"""
        try:
            if target is None:
                target = self._find_target_frame(page)

            page.wait_for_timeout(2000)

            # 테이블 데이터 추출
            tables = target.locator("table")
            table_count = tables.count()

            results = []
            results.append(f"=== KAIST 졸업시뮬레이션 결과 ===")
            results.append(f"페이지 URL: {page.url}\n")

            if table_count > 0:
                for i in range(table_count):
                    table = tables.nth(i)
                    try:
                        rows = table.locator("tr")
                        row_count = rows.count()

                        if row_count == 0:
                            continue

                        table_data = []
                        for j in range(row_count):
                            row = rows.nth(j)
                            cells = row.locator("th, td")
                            cell_count = cells.count()
                            cell_texts = []
                            for k in range(cell_count):
                                text = cells.nth(k).inner_text().strip()
                                if text:
                                    cell_texts.append(text)
                            if cell_texts:
                                table_data.append(" | ".join(cell_texts))

                        if table_data:
                            results.append(f"--- 테이블 {i+1} ---")
                            results.append("\n".join(table_data))
                            results.append("")
                    except Exception:
                        continue
            else:
                # 테이블이 없으면 전체 텍스트 추출
                body_text = target.locator("body").inner_text() if target != page else page.inner_text("body")
                # 불필요한 공백 정리
                lines = [line.strip() for line in body_text.splitlines() if line.strip()]
                results.append("\n".join(lines[:100]))

            return "\n".join(results)

        except Exception as e:
            return f"결과 스크래핑 중 오류: {str(e)}"

    def _save_cookies(self, context) -> None:
        """브라우저 쿠키 저장"""
        try:
            cookies = context.cookies()
            with open(COOKIE_PATH, "w") as f:
                json.dump(cookies, f)
        except Exception:
            pass

    def _load_cookies(self, context) -> bool:
        """저장된 쿠키 로드"""
        try:
            if not COOKIE_PATH.exists():
                return False
            with open(COOKIE_PATH, "r") as f:
                cookies = json.load(f)
            context.add_cookies(cookies)
            return True
        except Exception:
            return False

    async def _arun(
        self,
        query: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """비동기 실행 (현재는 동기 버전 호출)"""
        return self._run(query, run_manager)
