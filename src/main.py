"""
AI Agent 실행 진입점
"""
import sys
from agent import create_agent


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("Crew AI Agent 시작")
    print("=" * 60)
    print()

    # Agent 생성
    print("Agent를 초기화하는 중...")
    try:
        agent = create_agent(
            model_name="gpt-4-turbo-preview",
            temperature=0.7,
            verbose=True,
        )
        print("Agent 초기화 완료!")
        print()
    except Exception as e:
        print(f"Agent 초기화 실패: {e}")
        print("\n.env 파일에 OPENAI_API_KEY가 설정되어 있는지 확인하세요.")
        sys.exit(1)

    # 대화형 모드
    print("대화를 시작합니다. 종료하려면 'quit' 또는 'exit'을 입력하세요.")
    print("-" * 60)
    print()

    while True:
        try:
            # 사용자 입력 받기
            user_input = input("You: ").strip()

            # 종료 명령 확인
            if user_input.lower() in ["quit", "exit", "종료"]:
                print("\nAgent를 종료합니다. 안녕히 가세요!")
                break

            # 빈 입력 무시
            if not user_input:
                continue

            # Agent 실행
            print("\nAgent: ", end="", flush=True)
            response = agent.run(user_input)
            print(response)
            print()

        except KeyboardInterrupt:
            print("\n\nAgent를 종료합니다. 안녕히 가세요!")
            break
        except Exception as e:
            print(f"\n오류 발생: {e}")
            print()


if __name__ == "__main__":
    main()
