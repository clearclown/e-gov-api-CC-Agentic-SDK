#!/bin/bash
# MCPサーバー起動スクリプト

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=========================================="
echo "  MCPサーバーを起動します"
echo -e "==========================================${NC}"
echo ""

# 環境変数読み込み
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo -e "${GREEN}MCPサーバー (legal_tools) を起動中...${NC}"
echo ""
echo "提供されるツール:"
echo "  - search_law: 法令検索"
echo "  - search_case: 判例検索"
echo "  - analyze_law_case_relationship: 法令-判例関連分析"
echo "  - get_law_detail: 法令詳細取得"
echo "  - get_case_detail: 判例詳細取得"
echo "  - ask_legal_question: 法律相談"
echo ""
echo "停止するには Ctrl+C を押してください"
echo ""

# MCPサーバー起動
uv run python -m app.mcp.legal_server
