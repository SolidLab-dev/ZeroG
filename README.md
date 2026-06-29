# 🚀 ZeroG (Antigravity Discord Agent)

**ZeroG**는 로컬 맥북 환경에 설치된 `agy` (Antigravity CLI)를 외부(모바일 디스코드 등)에서 원격으로 제어하기 위해 구축된 파이썬 기반의 Discord Wrapper Bot입니다.

기존 상용 에이전트 툴(OpenClaw 등)이 가지는 API 우회 밴(Ban) 리스크와 과금 문제를 원천적으로 피하기 위해 고안되었습니다. `agy`를 파이썬 로컬 프로세스(Subprocess)로 직접 호출하여 **비용 제로의 안전한 프라이빗 자율형 에이전트 인프라**를 제공합니다.

## ✨ 핵심 기능

- **🧠 완벽한 맥락 유지 (무제한 컨텍스트)**
  - 스레드(Thread)별로 대화 기록을 `~/.zerog/threads/`에 영구적으로 안전하게 저장합니다.
  - 봇이 재시작되더라도 대화 내역이 증발하지 않으며, LLM의 무제한 컨텍스트 윈도우를 활용하여 이전 대화를 완벽히 기억합니다.
- **📎 멀티모달 & 파일 첨부 인식**
  - 디스코드에 이미지(스크린샷 등)나 코드 파일(.py, .txt 등)을 업로드하면 봇이 이를 다운로드하여 `agy`에게 전달합니다.
- **📂 프로젝트 폴더 바인딩 (`/bind`)**
  - 특정 디스코드 스레드의 작업 디렉토리를 사용자가 원하는 맥북의 로컬 경로로 고정(Lock)할 수 있습니다.
- **🛑 백그라운드 프로세스 관리 (`/kill`)**
  - 빌드(npm install 등)나 로컬 서버 실행 등으로 인해 봇이 무한 루프에 빠졌을 때, 프로세스를 디스코드에서 강제로 종료할 수 있습니다.
- **💻 Raw 쉘(Shell) 명령어 지원 (`/sh`)**
  - LLM을 거치지 않고 즉각적으로 맥북의 터미널 명령어(ls, pwd 등)를 실행하여 0.1초 만에 폴더 상태를 확인할 수 있습니다.

## 📁 프로젝트 구조

ZeroG는 모듈화된 Cogs 아키텍처를 따릅니다.

```
ZeroG/
├── .env                  # 디스코드 봇 토큰 및 권한 사용자 ID 설정
├── config.py             # 환경 변수 및 글로벌 경로 설정
├── main.py               # 봇 진입점 (Entry Point)
├── core/
│   ├── state.py          # 스레드 히스토리 및 모델 설정 JSON I/O 관리
│   └── runner.py         # agy 서브프로세스 실행 및 실시간 스트리밍 로직
└── cogs/
    ├── chat.py           # on_message 처리 (파일 첨부 및 대화 프롬프팅)
    └── commands.py       # 슬래시 커맨드 처리 (/create, /model, /bind 등)
```

## ⚙️ 설치 및 설정 (Setup)

1. **저장소 클론 및 가상환경 세팅**
   ```bash
   git clone <repository_url> ZeroG
   cd ZeroG
   python3 -m venv .venv
   source .venv/bin/activate
   pip install discord.py python-dotenv
   ```

2. **환경 변수 설정 (`.env`)**
   프로젝트 루트에 `.env` 파일을 생성하고 아래 값을 입력하세요.
   ```env
   DISCORD_BOT_TOKEN=당신의_디스코드_봇_토큰
   ALLOWED_USER_ID=당신의_디스코드_유저_고유_ID
   ```

3. **데이터 저장소 확인**
   - 봇을 실행하면 유저의 홈 디렉토리에 `~/.zerog/` 폴더가 자동 생성되며, 모든 대화 기록(JSON) 및 로그가 여기에 안전하게 저장됩니다.

## 🚀 실행 방법 (Usage)

### 방법 A: Homebrew를 통한 설치 및 백그라운드 구동 (추천)
맥북 사용자라면 Homebrew를 통해 가장 깔끔하게 설치하고 백그라운드 서비스로 굴릴 수 있습니다.
```bash
# 1. ZeroG 저장소를 Homebrew Tap으로 등록
brew tap SolidLab-dev/ZeroG https://github.com/SolidLab-dev/ZeroG

# 2. 패키지 설치
brew install zerog

# 3. 환경 변수 설정 (설치 후 출력되는 경로 안내 참조)
nano /usr/local/opt/zerog/libexec/.env 
# (애플 실리콘 맥은 /opt/homebrew/opt/zerog/libexec/.env)

# 4. 백그라운드 서비스 시작 (재부팅 시 자동 실행)
brew services start zerog
```

### 방법 B: 로컬에서 직접 실행
터미널에서 가상환경이 활성화된 상태로 `main.py`를 직접 실행합니다.
```bash
python3 main.py
```
디스코드 서버에 봇이 온라인으로 표시되면 준비 완료입니다!

## 🛠️ 슬래시 커맨드 목록

- `/create [태스크명]`: 새로운 개발 태스크용 스레드를 생성합니다.
- `/model [모델명]`: 해당 스레드에서 사용할 `agy` 모델을 동적으로 검색하고 변경합니다.
- `/bind [절대경로]`: 스레드의 `agy` 작업 공간을 해당 로컬 폴더로 고정합니다.
- `/kill`: 현재 스레드에서 백그라운드로 실행 중인 작업(서브프로세스)을 강제 종료합니다.
- `/sh [명령어]`: AI를 거치지 않고 순수 쉘 명령어를 실행합니다.
