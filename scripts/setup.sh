#!/bin/bash
# e-gov API - 自動セットアップスクリプト
# すべての環境確認・インストール・設定を自動実行

set -e  # エラーで即座に終了

# 色付き出力用
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================="
echo "  e-gov API - 自動セットアップ"
echo -e "==========================================${NC}"
echo ""

# ========================================
# Step 1: uvのインストール確認
# ========================================
echo -e "${YELLOW}[1/6] uv パッケージマネージャーの確認...${NC}"

if command -v uv >/dev/null 2>&1; then
    UV_VERSION=$(uv --version 2>&1 | head -n 1)
    echo -e "${GREEN}✓ uv が見つかりました: ${UV_VERSION}${NC}"
else
    echo -e "${YELLOW}⚠ uv が見つかりません。自動インストールを開始します...${NC}"

    # uvの自動インストール
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # PATHに追加
    export PATH="$HOME/.cargo/bin:$PATH"

    if command -v uv >/dev/null 2>&1; then
        echo -e "${GREEN}✓ uv のインストールに成功しました${NC}"
    else
        echo -e "${RED}✗ uv のインストールに失敗しました${NC}"
        echo "手動でインストールしてください: https://docs.astral.sh/uv/"
        exit 1
    fi
fi

echo ""

# ========================================
# Step 2: Pythonバージョン確認
# ========================================
echo -e "${YELLOW}[2/6] Python バージョンの確認...${NC}"

if command -v python3 >/dev/null 2>&1; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ ${PYTHON_VERSION}${NC}"
else
    echo -e "${RED}✗ Python 3 が見つかりません${NC}"
    exit 1
fi

echo ""

# ========================================
# Step 3: 仮想環境の作成
# ========================================
echo -e "${YELLOW}[3/6] 仮想環境の作成...${NC}"

if [ -d ".venv" ]; then
    echo -e "${GREEN}✓ 仮想環境は既に存在します${NC}"
else
    uv venv
    echo -e "${GREEN}✓ 仮想環境を作成しました${NC}"
fi

echo ""

# ========================================
# Step 4: 依存関係のインストール
# ========================================
echo -e "${YELLOW}[4/6] 依存関係のインストール...${NC}"

uv sync

echo -e "${GREEN}✓ 依存関係のインストールが完了しました${NC}"
echo ""

# ========================================
# Step 5: 環境変数の確認
# ========================================
echo -e "${YELLOW}[5/6] 環境変数の確認...${NC}"

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ .env ファイルが見つかりません${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ .env.example から .env を作成しました${NC}"
        echo -e "${YELLOW}! 重要: .env ファイルを編集して ANTHROPIC_API_KEY を設定してください${NC}"
    else
        echo -e "${RED}✗ .env.example も見つかりません${NC}"
    fi
else
    echo -e "${GREEN}✓ .env ファイルが存在します${NC}"

    # APIキーの確認
    if grep -q "ANTHROPIC_API_KEY=your" .env 2>/dev/null || \
       ! grep -q "ANTHROPIC_API_KEY=sk-ant" .env 2>/dev/null; then
        echo -e "${YELLOW}! 警告: ANTHROPIC_API_KEY が設定されていない可能性があります${NC}"
        echo -e "${YELLOW}  .env ファイルで設定してください${NC}"
    else
        echo -e "${GREEN}✓ ANTHROPIC_API_KEY が設定されています${NC}"
    fi
fi

echo ""

# ========================================
# Step 6: データベース・Redis確認（オプション）
# ========================================
echo -e "${YELLOW}[6/6] オプショナルサービスの確認...${NC}"

# PostgreSQL
if command -v psql >/dev/null 2>&1; then
    echo -e "${GREEN}✓ PostgreSQL が利用可能です${NC}"
else
    echo -e "${YELLOW}⚠ PostgreSQL が見つかりません（オプション）${NC}"
fi

# Redis
if command -v redis-cli >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis が利用可能です${NC}"
else
    echo -e "${YELLOW}⚠ Redis が見つかりません（オプション）${NC}"
fi

echo ""

# ========================================
# セットアップ完了
# ========================================
echo -e "${GREEN}=========================================="
echo "  ✓ セットアップが完了しました！"
echo -e "==========================================${NC}"
echo ""
echo "次のステップ:"
echo ""
echo "1. APIキーを設定:"
echo -e "   ${BLUE}nano .env${NC}  # または好きなエディタで編集"
echo ""
echo "2. APIサーバーを起動:"
echo -e "   ${BLUE}make start${NC}"
echo ""
echo "3. テストを実行:"
echo -e "   ${BLUE}make test${NC}"
echo ""
echo "ヘルプを表示:"
echo -e "   ${BLUE}make help${NC}"
echo ""
