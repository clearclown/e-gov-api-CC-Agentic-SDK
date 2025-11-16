#!/bin/bash
# 環境確認スクリプト

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=========================================="
echo "  環境チェック"
echo -e "==========================================${NC}"
echo ""

ERRORS=0
WARNINGS=0

# uv確認
echo -n "uv パッケージマネージャー: "
if command -v uv >/dev/null 2>&1; then
    echo -e "${GREEN}✓ $(uv --version | head -n 1)${NC}"
else
    echo -e "${RED}✗ 未インストール${NC}"
    ((ERRORS++))
fi

# Python確認
echo -n "Python: "
if command -v python3 >/dev/null 2>&1; then
    echo -e "${GREEN}✓ $(python3 --version)${NC}"
else
    echo -e "${RED}✗ 未インストール${NC}"
    ((ERRORS++))
fi

# 仮想環境確認
echo -n "仮想環境 (.venv): "
if [ -d ".venv" ]; then
    echo -e "${GREEN}✓ 存在${NC}"
else
    echo -e "${RED}✗ 未作成${NC}"
    ((ERRORS++))
fi

# .env確認
echo -n ".env ファイル: "
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ 存在${NC}"
else
    echo -e "${RED}✗ 未作成${NC}"
    ((ERRORS++))
fi

# APIキー確認
echo -n "ANTHROPIC_API_KEY: "
if [ -f ".env" ]; then
    if grep -q "ANTHROPIC_API_KEY=sk-ant" .env 2>/dev/null; then
        echo -e "${GREEN}✓ 設定済み${NC}"
    else
        echo -e "${YELLOW}⚠ 未設定または無効${NC}"
        ((WARNINGS++))
    fi
else
    echo -e "${RED}✗ .envファイルなし${NC}"
    ((ERRORS++))
fi

# Claudeモデル確認
echo -n "CLAUDE_MODEL: "
if [ -f ".env" ] && grep -q "CLAUDE_MODEL=" .env 2>/dev/null; then
    MODEL=$(grep "CLAUDE_MODEL=" .env | cut -d'=' -f2)
    echo -e "${GREEN}✓ ${MODEL}${NC}"
else
    echo -e "${YELLOW}⚠ 未設定（デフォルト使用）${NC}"
    ((WARNINGS++))
fi

# PostgreSQL（オプション）
echo -n "PostgreSQL: "
if command -v psql >/dev/null 2>&1; then
    echo -e "${GREEN}✓ 利用可能${NC}"
else
    echo -e "${YELLOW}⚠ 未インストール（オプション）${NC}"
fi

# Redis（オプション）
echo -n "Redis: "
if command -v redis-cli >/dev/null 2>&1; then
    echo -e "${GREEN}✓ 利用可能${NC}"
else
    echo -e "${YELLOW}⚠ 未インストール（オプション）${NC}"
fi

echo ""
echo -e "${BLUE}=========================================="
echo "  主要な依存パッケージ"
echo -e "==========================================${NC}"

# 主要パッケージの確認
if [ -d ".venv" ]; then
    .venv/bin/python -c "
import sys
packages = [
    ('anthropic', 'Anthropic SDK'),
    ('claude_agent_sdk', 'Claude Agent SDK'),
    ('fastapi', 'FastAPI'),
    ('uvicorn', 'Uvicorn'),
]

for pkg, name in packages:
    try:
        mod = __import__(pkg)
        version = getattr(mod, '__version__', 'unknown')
        print(f'✓ {name}: {version}')
    except ImportError:
        print(f'✗ {name}: 未インストール')
        sys.exit(1)
" || ((ERRORS++))
fi

echo ""

# サマリー
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}=========================================="
    echo "  ✓ すべての必須項目がOKです"
    echo -e "==========================================${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠ ${WARNINGS}件の警告があります${NC}"
    fi
    exit 0
else
    echo -e "${RED}=========================================="
    echo "  ✗ ${ERRORS}件のエラーがあります"
    echo -e "==========================================${NC}"
    echo ""
    echo "セットアップを実行してください:"
    echo -e "  ${BLUE}make setup${NC}"
    exit 1
fi
