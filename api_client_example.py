"""
API 클라이언트 예제
"""
import requests

# API 엔드포인트
API_URL = "http://localhost:8000/simulate"

def main():
    print("졸업시뮬레이션 API 호출 중...")
    print("브라우저가 열리면 수동으로 로그인해주세요.\n")

    try:
        # POST 요청
        response = requests.post(API_URL)
        response.raise_for_status()

        # 결과 파싱
        data = response.json()

        if data["success"]:
            print("\n✅ 성공!")
            print("\n" + data["result"])
        else:
            print("\n❌ 실패!")
            print(data["error"])

    except requests.exceptions.ConnectionError:
        print("오류: API 서버에 연결할 수 없습니다.")
        print("먼저 'python api_server.py'로 서버를 실행해주세요.")
    except Exception as e:
        print(f"오류: {e}")


if __name__ == "__main__":
    main()
