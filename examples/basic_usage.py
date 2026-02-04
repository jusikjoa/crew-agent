"""
기본 사용 예제
"""
import sys
import os

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent import create_agent


def example_simple_query():
    """간단한 질문 예제"""
    print("\n" + "=" * 60)
    print("예제 1: 간단한 질문")
    print("=" * 60)

    agent = create_agent(verbose=False)
    response = agent.run("안녕하세요! 당신은 누구인가요?")
    print(f"응답: {response}")


def example_web_search():
    """웹 검색 예제"""
    print("\n" + "=" * 60)
    print("예제 2: 웹 검색 사용")
    print("=" * 60)

    agent = create_agent(verbose=True)
    response = agent.run("LangChain의 최신 버전은 무엇인가요? 웹에서 검색해주세요.")
    print(f"\n최종 응답: {response}")


def example_api_call():
    """API 호출 예제"""
    print("\n" + "=" * 60)
    print("예제 3: API 호출 사용")
    print("=" * 60)

    agent = create_agent(verbose=True)

    # JSONPlaceholder API 사용 (무료 테스트 API)
    query = """
    다음 API를 호출해주세요:
    URL: https://jsonplaceholder.typicode.com/posts/1
    Method: GET
    """

    response = agent.run(query)
    print(f"\n최종 응답: {response}")


def example_complex_task():
    """복잡한 작업 예제"""
    print("\n" + "=" * 60)
    print("예제 4: 복잡한 작업 (웹 검색 + 분석)")
    print("=" * 60)

    agent = create_agent(verbose=True)
    response = agent.run(
        "Python의 최신 트렌드를 웹에서 검색하고, "
        "가장 인기있는 3가지 주제를 요약해주세요."
    )
    print(f"\n최종 응답: {response}")


def main():
    """예제 실행"""
    print("Crew AI Agent 사용 예제")

    try:
        # 원하는 예제의 주석을 해제하여 실행하세요
        example_simple_query()
        # example_web_search()  # Google API 키가 필요합니다
        # example_api_call()
        # example_complex_task()

    except Exception as e:
        print(f"\n오류 발생: {e}")
        print("\n.env 파일에 필요한 API 키가 모두 설정되어 있는지 확인하세요.")


if __name__ == "__main__":
    main()
