#!/bin/bash
# API + MCPサーバー同時起動スクリプト

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=========================================="
echo "  API + MCPサーバー同時起動"
echo -e "==========================================${NC}"
echo ""

# 環境変数読み込み
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# tmux または screenの確認
if command -v tmux >/dev/null 2>&1; then
    echo -e "${GREEN}tmux を使用して起動します${NC}"
    echo ""

    # tmuxセッション作成
    SESSION_NAME="egov-api"

    # 既存セッションがあれば削除
    tmux kill-session -t $SESSION_NAME 2>/dev/null || true

    # 新しいセッション作成
    tmux new-session -d -s $SESSION_NAME

    # ウィンドウ1: APIサーバー
    tmux rename-window -t $SESSION_NAME:0 'API Server'
    tmux send-keys -t $SESSION_NAME:0 'bash scripts/start-api.sh' C-m

    # ウィンドウ2: MCPサーバー
    tmux new-window -t $SESSION_NAME:1 -n 'MCP Server'
    tmux send-keys -t $SESSION_NAME:1 'bash scripts/start-mcp.sh' C-m

    echo -e "${GREEN}✓ サーバーを起動しました${NC}"
    echo ""
    echo "tmuxセッションにアタッチ:"
    echo -e "  ${BLUE}tmux attach -t $SESSION_NAME${NC}"
    echo ""
    echo "ウィンドウ切り替え: Ctrl+b → 0/1"
    echo "デタッチ: Ctrl+b → d"
    echo "セッション終了:"
    echo -e "  ${BLUE}tmux kill-session -t $SESSION_NAME${NC}"

elif command -v screen >/dev/null 2>&1; then
    echo -e "${GREEN}screen を使用して起動します${NC}"
    echo ""

    # screenでバックグラウンド起動
    screen -dmS egov-api bash scripts/start-api.sh
    screen -dmS egov-mcp bash scripts/start-mcp.sh

    echo -e "${GREEN}✓ サーバーを起動しました${NC}"
    echo ""
    echo "screenセッション一覧:"
    echo -e "  ${BLUE}screen -ls${NC}"
    echo ""
    echo "アタッチ:"
    echo -e "  ${BLUE}screen -r egov-api${NC}  # API"
    echo -e "  ${BLUE}screen -r egov-mcp${NC}  # MCP"

else
    echo -e "${YELLOW}⚠ tmux/screen が見つかりません${NC}"
    echo ""
    echo "個別起動してください:"
    echo -e "  ${BLUE}make start-api${NC}  # ターミナル1"
    echo -e "  ${BLUE}make start-mcp${NC}  # ターミナル2"
    echo ""
    echo "または tmux/screen をインストール:"
    echo "  sudo apt install tmux     # Debian/Ubuntu"
    echo "  sudo yum install tmux     # RHEL/CentOS"
    exit 1
fi
