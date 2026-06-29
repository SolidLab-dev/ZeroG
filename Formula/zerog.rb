class Zerog < Formula
  desc "Antigravity Discord Wrapper Bot (ZeroG)"
  homepage "https://github.com/SolidLab-dev/ZeroG"
  url "https://github.com/SolidLab-dev/ZeroG/archive/refs/heads/main.tar.gz"
  version "1.1.0"
  head "https://github.com/SolidLab-dev/ZeroG.git", branch: "main"

  depends_on "python@3.11"

  def install
    # Create a virtualenv in libexec
    system "python3", "-m", "venv", libexec
    system libexec/"bin/pip", "install", "-r", "requirements.txt"
    
    # Copy all project files to libexec
    libexec.install Dir["*"]

    (bin/"zerog").write <<~EOS
      #!/bin/bash
      
      ZEROG_DIR="$HOME/.zerog"
      ENV_FILE="$ZEROG_DIR/.env"
      LOG_FILE="$ZEROG_DIR/logs/zerog.log"
      
      if [ "$1" = "onboard" ] || [ "$1" = "setup" ]; then
          # ANSI Colors & Styles
          BLUE="\\033[1;34m"
          CYAN="\\033[1;36m"
          GREEN="\\033[1;32m"
          PURPLE="\\033[1;35m"
          YELLOW="\\033[1;33m"
          BOLD="\\033[1m"
          DIM="\\033[2m"
          RESET="\\033[0m"

          clear
          echo -e ""
          echo -e "${CYAN}${BOLD}  ███████╗███████╗██████╗  ██████╗  ██████╗ ${RESET}"
          echo -e "${CYAN}${BOLD}  ╚══███╔╝██╔════╝██╔══██╗██╔═══██╗██╔════╝ ${RESET}"
          echo -e "${CYAN}${BOLD}    ███╔╝ █████╗  ██████╔╝██║   ██║██║  ███╗${RESET}"
          echo -e "${BLUE}${BOLD}   ███╔╝  ██╔══╝  ██╔══██╗██║   ██║██║   ██║${RESET}"
          echo -e "${BLUE}${BOLD}  ███████╗███████╗██║  ██║╚██████╔╝╚██████╔╝${RESET}"
          echo -e "${BLUE}${BOLD}  ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ${RESET}"
          echo -e "  ${DIM}A N T I G R A V I T Y   A G E N T${RESET}"
          echo -e "  ${PURPLE}${BOLD}Engineered by SolidLab${RESET}"
          echo -e ""
          echo -e "${DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
          echo -e "${YELLOW}🚀 API 과금과 환경의 제약(중력)에서 벗어날 준비가 되셨나요?${RESET}"
          echo -e "ZeroG를 백그라운드 프라이빗 에이전트로 설정합니다."
          echo -e "설정 파일은 안전하게 ${BOLD}$ENV_FILE${RESET} 에 저장됩니다."
          echo -e "${DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
          echo -e ""
          
          echo -e "${PURPLE}❖${RESET} ${BOLD}[Step 1/3] Discord Bot Token${RESET}"
          echo -e "  ${DIM}Discord Developer Portal에서 발급받은 봇 토큰을 입력하세요.${RESET}"
          read -p "  ➜ " token
          echo -e ""
          
          echo -e "${PURPLE}❖${RESET} ${BOLD}[Step 2/3] Allowed User ID${RESET}"
          echo -e "  ${DIM}ZeroG를 조종할 권한을 가진 본인의 디스코드 유저 ID(숫자)입니다.${RESET}"
          read -p "  ➜ " uid
          echo -e ""
          
          echo -e "${PURPLE}❖${RESET} ${BOLD}[Step 3/3] Discord Webhook URL (Optional)${RESET}"
          echo -e "  ${DIM}ZeroG의 에러 및 경고 로그를 수신할 웹훅 주소를 입력하세요. (건너뛰려면 Enter)${RESET}"
          read -p "  ➜ " webhook
          echo -e ""
          
          mkdir -p "$ZEROG_DIR"
          echo "DISCORD_BOT_TOKEN=$token" > "$ENV_FILE"
          echo "ALLOWED_USER_ID=$uid" >> "$ENV_FILE"
          if [ -n "$webhook" ]; then
              echo "DISCORD_WEBHOOK_URL=$webhook" >> "$ENV_FILE"
          fi
          
          echo -e "${GREEN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
          echo -e "${GREEN}${BOLD}✅ Onboarding complete! ZeroG is ready to launch.${RESET}"
          echo -e "Run the following command to start the background agent:"
          echo -e "${CYAN}➜ brew services start zerog${RESET}"
          echo -e "${GREEN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
          echo -e ""
          exit 0
          
      elif [ "$1" = "logs" ]; then
          if [ -f "$LOG_FILE" ]; then
              echo "👀 Tailing ZeroG logs (Press Ctrl+C to exit)..."
              tail -f "$LOG_FILE"
          else
              echo "❌ Log file not found at $LOG_FILE"
          fi
          exit 0
          
      elif [ "$1" = "clear" ]; then
          echo "⚠️ This will delete all thread memory and states."
          read -p "Are you sure? (y/N): " confirm
          if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
              rm -rf "$ZEROG_DIR/threads"
              rm -f "$ZEROG_DIR/settings.json"
              echo "✅ Memory cleared successfully!"
          else
              echo "Aborted."
          fi
          exit 0
      fi

      # Default execution
      cd #{libexec}
      exec #{libexec}/bin/python3 main.py "$@"
    EOS
  end

  service do
    run [opt_bin/"zerog"]
    keep_alive true
    working_dir libexec
    log_path var/"log/zerog.log"
    error_log_path var/"log/zerog_error.log"
    environment_variables PATH: "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
  end

  def caveats
    <<~EOS
      🚀 ZeroG has been installed successfully!
      
      Before starting the service, you MUST configure your bot tokens.
      Run the interactive onboarding wizard:
        zerog onboard
      
      After onboarding, start ZeroG as a background service:
        brew services start zerog
        
      To stop the service:
        brew services stop zerog
        
      To view real-time logs:
        zerog logs
    EOS
  end
end
