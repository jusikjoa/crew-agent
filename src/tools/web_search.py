"""
웹 검색 도구
DuckDuckGo를 사용하여 웹 검색을 수행합니다.
"""
from typing import Optional
from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from duckduckgo_search import DDGS


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
                results = list(ddgs.text(query, max_results=5))

            if not results:
                return f"'{query}'에 대한 검색 결과가 없습니다."

            formatted = []
            for i, item in enumerate(results, 1):
                title = item.get("title", "제목 없음")
                body = item.get("body", "설명 없음")
                link = item.get("href", "")
                formatted.append(f"{i}. {title}\n   {body}\n   링크: {link}")

            return "\n\n".join(formatted)

        except Exception as e:
            return f"검색 중 오류 발생: {str(e)}"

    async def _arun(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """비동기 실행 (현재는 동기 버전 호출)"""
        return self._run(query, run_manager)
