#!/bin/bash
# APIサーバー起動スクリプト

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=========================================="
echo "  APIサーバーを起動します"
echo -e "==========================================${NC}"
echo ""

# 環境変数読み込み
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# APIキーチェック
if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "your_api_key_here" ]; then
    echo -e "${YELLOW}⚠ 警告: ANTHROPIC_API_KEY が設定されていません${NC}"
    echo "Agent機能を使用するには .env でAPIキーを設定してください"
    echo ""
fi

# ポート確認
PORT=${API_PORT:-8000}
echo "ポート: $PORT"
echo ""

echo -e "${GREEN}サーバーを起動中...${NC}"
echo ""
echo "アクセスURL:"
echo -e "  ${BLUE}API: http://localhost:$PORT${NC}"
echo -e "  ${BLUE}Docs: http://localhost:$PORT/docs${NC}"
echo ""
echo "停止するには Ctrl+C を押してください"
echo ""

# サーバー起動
uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload
