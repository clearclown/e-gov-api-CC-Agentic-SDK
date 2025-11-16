.PHONY: help setup install check start start-api start-mcp start-frontend start-all-services test clean docker-up docker-down

# デフォルトターゲット - ヘルプを表示
help:
	@echo "=========================================="
	@echo "  e-gov API - Claude Agent SDK"
	@echo "=========================================="
	@echo ""
	@echo "使用可能なコマンド:"
	@echo ""
	@echo "【バックエンド】"
	@echo "  make setup          - 初回セットアップ（uv確認→インストール→環境構築）"
	@echo "  make install        - 依存関係のインストール"
	@echo "  make check          - 環境・設定の確認"
	@echo "  make start          - APIサーバー起動"
	@echo "  make start-mcp      - MCPサーバー起動"
	@echo "  make start-all      - API + MCPサーバー同時起動"
	@echo ""
	@echo "【フロントエンド】"
	@echo "  make frontend-setup - フロントエンドのセットアップ"
	@echo "  make frontend-dev   - フロントエンド開発サーバー起動"
	@echo "  make frontend-build - フロントエンドビルド"
	@echo "  make frontend-test  - フロントエンドテスト実行"
	@echo "  make frontend-lint  - フロントエンドlint実行"
	@echo ""
	@echo "【Docker】"
	@echo "  make docker-up      - Docker Composeで全サービス起動"
	@echo "  make docker-down    - Docker Composeで全サービス停止"
	@echo "  make docker-logs    - Docker logs表示"
	@echo ""
	@echo "【テスト】"
	@echo "  make test           - バックエンドテスト実行"
	@echo "  make test-live      - 実環境統合テスト"
	@echo "  make clean          - キャッシュ・一時ファイル削除"
	@echo ""
	@echo "クイックスタート:"
	@echo "  1. make setup               # バックエンド初回セットアップ"
	@echo "  2. make frontend-setup      # フロントエンド初回セットアップ"
	@echo "  3. make docker-up           # Docker Composeで全サービス起動"
	@echo ""

# 初回セットアップ（全自動）
setup:
	@echo "=========================================="
	@echo "  自動セットアップを開始します"
	@echo "=========================================="
	@bash scripts/setup.sh

# 依存関係インストール
install:
	@echo "依存関係をインストール中..."
	@if command -v uv >/dev/null 2>&1; then \
		uv sync; \
	else \
		echo "エラー: uvがインストールされていません"; \
		echo "make setup を実行してください"; \
		exit 1; \
	fi

# 環境確認
check:
	@bash scripts/check.sh

# APIサーバー起動
start: start-api

# APIサーバー起動
start-api:
	@echo "APIサーバーを起動しています..."
	@bash scripts/start-api.sh

# MCPサーバー起動
start-mcp:
	@echo "MCPサーバーを起動しています..."
	@bash scripts/start-mcp.sh

# 両方同時起動
start-all:
	@echo "API + MCPサーバーを起動しています..."
	@bash scripts/start-all.sh

# テスト実行
test:
	@echo "テストを実行中..."
	@uv run pytest tests/ -v

# 実環境統合テスト
test-live:
	@echo "実環境統合テストを実行中..."
	@uv run python test_live_integration.py

# クリーンアップ
clean:
	@echo "キャッシュをクリーンアップ中..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✓ クリーンアップ完了"

# 開発モード起動（ホットリロード）
dev:
	@echo "開発モードでAPIサーバーを起動..."
	@uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 本番モード起動
prod:
	@echo "本番モードでAPIサーバーを起動..."
	@uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# ========================================
# フロントエンド関連
# ========================================

# フロントエンドセットアップ
frontend-setup:
	@echo "フロントエンドのセットアップ中..."
	@cd frontend && npm install
	@cd frontend && cp .env.example .env 2>/dev/null || true
	@echo "✓ フロントエンドのセットアップ完了"

# フロントエンド開発サーバー起動
frontend-dev:
	@echo "フロントエンド開発サーバーを起動中..."
	@cd frontend && npm run dev

# フロントエンドビルド
frontend-build:
	@echo "フロントエンドをビルド中..."
	@cd frontend && npm run build

# フロントエンドテスト
frontend-test:
	@echo "フロントエンドテストを実行中..."
	@cd frontend && npm run test

# フロントエンドE2Eテスト
frontend-test-e2e:
	@echo "フロントエンドE2Eテストを実行中..."
	@cd frontend && npm run test:e2e

# フロントエンドlint
frontend-lint:
	@echo "フロントエンドlintを実行中..."
	@cd frontend && npm run lint

# フロントエンドlint自動修正
frontend-lint-fix:
	@echo "フロントエンドlintを自動修正中..."
	@cd frontend && npm run lint:fix

# ========================================
# Docker Compose関連
# ========================================

# 全サービスを起動
docker-up:
	@echo "Docker Composeで全サービスを起動中..."
	@docker compose up -d
	@echo "✓ 全サービスが起動しました"
	@echo ""
	@echo "アクセスURL:"
	@echo "  フロントエンド: http://localhost:3000"
	@echo "  API: http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"

# 全サービスを停止
docker-down:
	@echo "Docker Composeで全サービスを停止中..."
	@docker compose down

# 全サービスを再起動
docker-restart: docker-down docker-up

# ログ表示
docker-logs:
	@docker compose logs -f

# 全サービスのビルドと起動
docker-build:
	@echo "Docker Composeで全サービスをビルド＆起動中..."
	@docker compose up -d --build
