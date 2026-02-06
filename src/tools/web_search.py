"""
웹 검색 도구
Google Custom Search API를 사용하여 웹 검색을 수행합니다.
"""
from typing import Optional
from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
import requests
import os


class WebSearchTool(BaseTool):
    """Google Custom Search를 사용한 웹 검색 도구"""

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
            api_key = os.getenv("GOOGLE_API_KEY")
            cse_id = os.getenv("GOOGLE_CSE_ID")

            if not api_key or not cse_id:
                return "오류: GOOGLE_API_KEY와 GOOGLE_CSE_ID를 .env 파일에 설정해주세요."

            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": api_key,
                "cx": cse_id,
                "q": query,
                "num": 5  # 상위 5개 결과
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            if "items" not in data:
                return f"'{query}'에 대한 검색 결과가 없습니다."

            results = []
            for i, item in enumerate(data["items"][:5], 1):
                title = item.get("title", "제목 없음")
                snippet = item.get("snippet", "설명 없음")
                link = item.get("link", "")
                results.append(f"{i}. {title}\n   {snippet}\n   링크: {link}")

            return "\n\n".join(results)

        except Exception as e:
            return f"검색 중 오류 발생: {str(e)}"

    async def _arun(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """비동기 실행 (현재는 동기 버전 호출)"""
        return self._run(query, run_manager)
