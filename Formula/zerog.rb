class Zerog < Formula
  desc "Antigravity Discord Wrapper Bot (ZeroG)"
  homepage "https://github.com/SolidLab-dev/ZeroG"
  url "https://github.com/SolidLab-dev/ZeroG/archive/refs/heads/main.tar.gz"
  version "1.0.0"
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
          # ANSI Colors
          BLUE="\\033[1;34m"
          CYAN="\\033[1;36m"
          GREEN="\\033[1;32m"
          YELLOW="\\033[1;33m"
          BOLD="\\033[1m"
          RESET="\\033[0m"

          echo -e ""
          echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
          echo -e "${CYAN}${BOLD}                 🚀 Welcome to ZeroG Onboarding!                 ${RESET}"
          echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
          echo -e "${YELLOW}ZeroG will run seamlessly in the background as your private agent.${RESET}"
          echo -e "We will securely save your settings to ${BOLD}$ENV_FILE${RESET}"
          echo -e ""
          
          echo -e "${BLUE}[Step 1/3] Discord Bot Token${RESET}"
          echo -e "You can get this from the Discord Developer Portal."
          read -p "➜ Enter Token: " token
          echo -e ""
          
          echo -e "${BLUE}[Step 2/3] Allowed User ID${RESET}"
          echo -e "Only this User ID will be able to talk to ZeroG (Numbers only)."
          read -p "➜ Enter User ID: " uid
          echo -e ""
          
          echo -e "${BLUE}[Step 3/3] Discord Webhook URL (Optional)${RESET}"
          echo -e "ZeroG will push ERROR and WARNING alerts to this webhook."
          read -p "➜ Enter Webhook URL (Press Enter to skip): " webhook
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
