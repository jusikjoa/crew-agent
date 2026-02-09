"""
웹 검색 도구
DuckDuckGo를 사용하여 웹 검색을 수행하고,
상위 결과의 페이지 본문을 크롤링하여 상세 정보를 제공합니다.
"""
from typing import Optional
from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup


def _fetch_page_text(url: str, max_chars: int = 2000) -> str:
    """URL에서 본문 텍스트를 추출"""
    try:
        resp = requests.get(url, timeout=5, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        # 빈 줄 정리
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)[:max_chars]
    except Exception:
        return ""


class WebSearchTool(BaseTool):
    """DuckDuckGo를 사용한 웹 검색 도구"""

    name: str = "web_search"
    description: str = (
        "웹에서 정보를 검색할 때 유용합니다. "
        "검색어를 입력으로 받아서 관련된 웹 페이지 결과를 반환합니다. "
        "예: 'LangChain 최신 버전', '날씨 서울'"
    )

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """검색 실행"""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, region="kr-kr", max_results=10))

            if not results:
                return f"'{query}'에 대한 검색 결과가 없습니다."

            formatted = []
            for i, item in enumerate(results[:10], 1):
                title = item.get("title", "제목 없음")
                body = item.get("body", "설명 없음")
                link = item.get("href", "")
                formatted.append(f"{i}. {title}\n   {body}\n   링크: {link}")

            # 상위 3개 결과의 페이지 본문 크롤링
            detailed = []
            for item in results[:5]:
                url = item.get("href", "")
                if url:
                    page_text = _fetch_page_text(url)
                    if page_text:
                        detailed.append(
                            f"--- {item.get('title', '')} ({url}) ---\n{page_text}"
                        )

            output = "=== 검색 결과 ===\n" + "\n\n".join(formatted)
            if detailed:
                output += "\n\n=== 상세 내용 ===\n" + "\n\n".join(detailed)

            return output

        except Exception as e:
            return f"검색 중 오류 발생: {str(e)}"

    async def _arun(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """비동기 실행 (현재는 동기 버전 호출)"""
        return self._run(query, run_manager)
