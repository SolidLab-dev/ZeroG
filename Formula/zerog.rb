class Zerog < Formula
  desc "Antigravity Discord Wrapper Bot (ZeroG)"
  homepage "https://github.com/SolidLab-dev/ZeroG"
  url "https://github.com/SolidLab-dev/ZeroG.git", branch: "main"
  version "0.1.9"
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
          
      elif [ "$1" = "status" ]; then
          BLUE="\\033[1;34m"
          BOLD="\\033[1m"
          RESET="\\033[0m"
          echo -e "${BLUE}${BOLD}🔍 Checking ZeroG Service Status...${RESET}"
          brew services info zerog
          exit 0
          
      elif [ "$1" = "doctor" ]; then
          BLUE="\\033[1;34m"
          CYAN="\\033[1;36m"
          GREEN="\\033[1;32m"
          YELLOW="\\033[1;33m"
          DIM="\\033[2m"
          BOLD="\\033[1m"
          RESET="\\033[0m"
          
          echo -e "${BLUE}${BOLD}🩺 ZeroG System Doctor${RESET}"
          echo -e "${DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
          
          if [ -f "$ENV_FILE" ]; then
              echo -e "${GREEN}✅ Settings file found: $ENV_FILE${RESET}"
              echo -e ""
              
              BOT_TOKEN=$(grep DISCORD_BOT_TOKEN "$ENV_FILE" | cut -d '=' -f2)
              if [ -n "$BOT_TOKEN" ]; then
                  echo -e "${GREEN}✅ Bot Token: ${BOT_TOKEN:0:15}*******************${RESET}"
              else
                  echo -e "${YELLOW}⚠️ Bot Token: Missing!${RESET}"
              fi
              
              USER_ID=$(grep ALLOWED_USER_ID "$ENV_FILE" | cut -d '=' -f2)
              if [ -n "$USER_ID" ]; then
                  echo -e "${GREEN}✅ Allowed User ID: $USER_ID${RESET}"
              else
                  echo -e "${YELLOW}⚠️ Allowed User ID: Missing!${RESET}"
              fi
              
              WEBHOOK=$(grep DISCORD_WEBHOOK_URL "$ENV_FILE" | cut -d '=' -f2)
              if [ -n "$WEBHOOK" ]; then
                  echo -e "${GREEN}✅ Webhook URL: Configured${RESET}"
              else
                  echo -e "${DIM}ℹ️ Webhook URL: Not configured (Optional)${RESET}"
              fi
          else
              echo -e "${YELLOW}❌ Settings file NOT FOUND at $ENV_FILE${RESET}"
              echo -e "Please run '${CYAN}zerog onboard${RESET}' to configure."
          fi
          
          echo -e "${DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
          if [ -d "$ZEROG_DIR/logs" ]; then
              echo -e "${GREEN}✅ Logs directory exists.${RESET}"
          else
              echo -e "${YELLOW}⚠️ Logs directory missing. Will be created on start.${RESET}"
          fi
          exit 0
          
      elif [ "$1" = "start" ]; then
          echo -e "\\033[1;32m🚀 Starting ZeroG background service...\\033[0m"
          if brew services start zerog 2>&1 | grep -q "Bootstrap failed: 5"; then
              echo -e "\\033[1;33m⚠️ Service already registered. Forcing restart instead...\\033[0m"
              brew services restart zerog
          fi
          exit 0
          
      elif [ "$1" = "stop" ]; then
          echo -e "\\033[1;33m🛑 Stopping ZeroG background service...\\033[0m"
          brew services stop zerog
          exit 0
          
      elif [ "$1" = "restart" ]; then
          echo -e "\\033[1;36m🔄 Restarting ZeroG background service...\\033[0m"
          brew services restart zerog
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
          
      elif [ "$1" = "run" ]; then
          echo -e "\\033[1;33m⚠️ Starting ZeroG in foreground mode...\\033[0m"
          echo -e "\\033[2m(To run in background instead, use: zerog start)\\033[0m"
          cd #{libexec}
          exec #{libexec}/bin/python3 main.py
          
      elif [ -z "$1" ] || [ "$1" = "help" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ] || [ "$1" = "manual" ]; then
          BLUE="\\033[1;34m"
          CYAN="\\033[1;36m"
          GREEN="\\033[1;32m"
          PURPLE="\\033[1;35m"
          YELLOW="\\033[1;33m"
          BOLD="\\033[1m"
          DIM="\\033[2m"
          RESET="\\033[0m"

          echo -e ""
          echo -e "${CYAN}${BOLD}  ███████╗███████╗██████╗  ██████╗  ██████╗ ${RESET}"
          echo -e "${CYAN}${BOLD}  ╚══███╔╝██╔════╝██╔══██╗██╔═══██╗██╔════╝ ${RESET}"
          echo -e "${CYAN}${BOLD}    ███╔╝ █████╗  ██████╔╝██║   ██║██║  ███╗${RESET}"
          echo -e "${BLUE}${BOLD}   ███╔╝  ██╔══╝  ██╔══██╗██║   ██║██║   ██║${RESET}"
          echo -e "${BLUE}${BOLD}  ███████╗███████╗██║  ██║╚██████╔╝╚██████╔╝${RESET}"
          echo -e "${BLUE}${BOLD}  ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ${RESET}"
          echo -e "  ${DIM}A N T I G R A V I T Y   A G E N T${RESET}"
          echo -e ""
          echo -e "${DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
          echo -e "${BOLD}USAGE:${RESET} zerog <command>"
          echo -e ""
          echo -e "${PURPLE}❖${RESET} ${BOLD}COMMANDS${RESET}"
          echo -e "  ${CYAN}onboard${RESET}    : Run the interactive setup wizard (Tokens, Webhook)"
          echo -e "  ${CYAN}run${RESET}        : Run the bot directly in the foreground"
          echo -e "  ${CYAN}start${RESET}      : Start ZeroG as a background service"
          echo -e "  ${CYAN}stop${RESET}       : Stop the background service"
          echo -e "  ${CYAN}restart${RESET}    : Restart the background service"
          echo -e "  ${CYAN}status${RESET}     : Check if the service is running"
          echo -e "  ${CYAN}doctor${RESET}     : Diagnose system configuration and environment"
          echo -e "  ${CYAN}logs${RESET}       : Tail real-time logs from the background service"
          echo -e "  ${CYAN}clear${RESET}      : Factory reset bot memory and conversation histories"
          echo -e "  ${CYAN}help${RESET}       : Show this beautiful help manual"
          echo -e ""
          echo -e "${PURPLE}❖${RESET} ${BOLD}QUICK START${RESET}"
          echo -e "  1. Run ${GREEN}zerog onboard${RESET} to securely store your tokens."
          echo -e "  2. Run ${GREEN}zerog start${RESET} to awaken your private agent."
          echo -e "${DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
          echo -e ""
          exit 0
          
      else
          echo -e "\\033[1;31m❌ Unknown command: $1\\033[0m"
          echo -e "Run '\\033[1;36mzerog help\\033[0m' to see the manual."
          exit 1
      fi
    EOS
  end

  service do
    run [opt_bin/"zerog", "run"]
    keep_alive true
    working_dir libexec
    log_path var/"log/zerog.log"
    error_log_path var/"log/zerog_error.log"
    environment_variables PATH: "#{HOMEBREW_PREFIX}/bin:#{HOMEBREW_PREFIX}/sbin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
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
