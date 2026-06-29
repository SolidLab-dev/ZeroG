#!/bin/bash

# ZeroG MacOS Background Service Setup Script
# 이 스크립트는 ZeroG 디스코드 봇을 맥북이 켜질 때마다 백그라운드에서 자동 실행되도록 설정합니다. (brew services와 동일한 원리)

SERVICE_NAME="com.solidlab.zerog"
PLIST_PATH="$HOME/Library/LaunchAgents/$SERVICE_NAME.plist"
PROJECT_DIR="$(pwd)"
PYTHON_BIN="$PROJECT_DIR/.venv/bin/python3"
LOG_DIR="$HOME/.zerog/logs"

# 가상환경 파이썬 확인
if [ ! -f "$PYTHON_BIN" ]; then
    echo "❌ 가상환경을 찾을 수 없습니다. 프로젝트 루트에서 스크립트를 실행해주세요."
    exit 1
fi

mkdir -p "$LOG_DIR"

# plist 파일 생성 (XML)
cat <<EOF > "$PLIST_PATH"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$SERVICE_NAME</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_BIN</string>
        <string>$PROJECT_DIR/main.py</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>$LOG_DIR/zerog_service.out</string>
    
    <key>StandardErrorPath</key>
    <string>$LOG_DIR/zerog_service.err</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>
EOF

echo "✅ $PLIST_PATH 파일이 생성되었습니다."

# 서비스 등록 및 시작
launchctl unload "$PLIST_PATH" 2>/dev/null
launchctl load "$PLIST_PATH"

echo "🚀 ZeroG 백그라운드 서비스가 시작되었습니다!"
echo "이제 터미널을 닫아도 봇이 계속 실행되며, 맥북을 재부팅해도 자동 실행됩니다."
echo "상태 확인: launchctl list | grep zerog"
echo "서비스 중지: launchctl unload $PLIST_PATH"
