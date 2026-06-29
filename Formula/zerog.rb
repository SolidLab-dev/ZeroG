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

    # Create a wrapper script in bin
    (bin/"zerog").write <<~EOS
      #!/bin/bash
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
