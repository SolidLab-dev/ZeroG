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
          echo "🚀 Welcome to ZeroG Onboarding!"
          echo "We will securely save your settings to $ENV_FILE"
          echo "------------------------------------------------"
          read -p "Enter DISCORD_BOT_TOKEN: " token
          read -p "Enter ALLOWED_USER_ID (Numbers only): " uid
          read -p "Enter DISCORD_WEBHOOK_URL (Optional, press Enter to skip): " webhook
          
          mkdir -p "$ZEROG_DIR"
          echo "DISCORD_BOT_TOKEN=$token" > "$ENV_FILE"
          echo "ALLOWED_USER_ID=$uid" >> "$ENV_FILE"
          if [ -n "$webhook" ]; then
              echo "DISCORD_WEBHOOK_URL=$webhook" >> "$ENV_FILE"
          fi
          
          echo "------------------------------------------------"
          echo "✅ Onboarding complete!"
          echo "You can now run: brew services start zerog"
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
      
      ZeroG requires a .env file to run. Please create it in the libexec directory:
        nano #{libexec}/.env
      
      Add your Discord tokens:
        DISCORD_BOT_TOKEN=your_token_here
        ALLOWED_USER_ID=your_discord_id_here
      
      To start ZeroG as a background service:
        brew services start zerog
        
      To stop the service:
        brew services stop zerog
    EOS
  end
end
