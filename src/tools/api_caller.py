"""
API 호출 도구
외부 REST API를 호출하는 도구입니다.
"""
from typing import Optional, Dict, Any
from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
import requests
import json


class APICallerTool(BaseTool):
    """REST API 호출 도구"""

    name: str = "api_caller"
    description: str = (
        "외부 REST API를 호출할 때 사용합니다. "
        "JSON 형식의 요청을 받아서 API를 호출하고 결과를 반환합니다. "
        "입력 형식: {'url': 'API URL', 'method': 'GET/POST/PUT/DELETE', "
        "'headers': {}, 'data': {}}"
    )

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """API 호출 실행"""
        try:
            # 입력 파싱
            request_data = json.loads(query)

            url = request_data.get("url")
            method = request_data.get("method", "GET").upper()
            headers = request_data.get("headers", {})
            data = request_data.get("data", {})
            params = request_data.get("params", {})

            if not url:
                return "오류: URL이 필요합니다."

            # API 호출
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                return f"지원하지 않는 HTTP 메서드: {method}"

            # 응답 처리
            response.raise_for_status()

            try:
                result = response.json()
                return json.dumps(result, ensure_ascii=False, indent=2)
            except:
                return response.text

        except json.JSONDecodeError:
            return "오류: 잘못된 JSON 형식입니다."
        except requests.exceptions.RequestException as e:
            return f"API 호출 중 오류 발생: {str(e)}"
        except Exception as e:
            return f"처리 중 오류 발생: {str(e)}"

    async def _arun(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """비동기 실행 (현재는 동기 버전 호출)"""
        return self._run(query, run_manager)
