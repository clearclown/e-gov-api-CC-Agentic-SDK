#!/usr/bin/env python3
"""
e-gov API 開発用CLIツール

簡単にセットアップ・起動・テストができるコマンドラインツール
"""

import sys
import subprocess
import os
from pathlib import Path

# 色付き出力
class Colors:
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'  # No Color

def print_header(text):
    print(f"{Colors.BLUE}{'=' * 50}")
    print(f"  {text}")
    print(f"{'=' * 50}{Colors.NC}")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.NC}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.NC}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.NC}")

def run_command(cmd, description=None):
    """コマンド実行"""
    if description:
        print(f"\n{description}...")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print_error(f"コマンド実行エラー: {cmd}")
        print(e.stderr)
        return None

def show_help():
    """ヘルプ表示"""
    print_header("e-gov API CLI")
    print("""
使用方法:
    python dev.py <command>

コマンド:
    setup       - 初回セットアップ（uv確認→インストール→環境構築）
    check       - 環境確認
    start       - APIサーバー起動
    mcp         - MCPサーバー起動
    test        - テスト実行
    clean       - キャッシュクリア
    help        - このヘルプを表示

クイックスタート:
    1. python dev.py setup   # 初回のみ
    2. python dev.py start   # APIサーバー起動

または:
    make setup
    make start
""")

def setup():
    """セットアップ実行"""
    print_header("自動セットアップ")
    run_command("bash scripts/setup.sh", "セットアップスクリプト実行")

def check():
    """環境確認"""
    print_header("環境チェック")
    run_command("bash scripts/check.sh", "環境確認実行")

def start():
    """APIサーバー起動"""
    print_header("APIサーバー起動")
    print("\n停止するには Ctrl+C を押してください\n")
    subprocess.run("bash scripts/start-api.sh", shell=True)

def start_mcp():
    """MCPサーバー起動"""
    print_header("MCPサーバー起動")
    print("\n停止するには Ctrl+C を押してください\n")
    subprocess.run("bash scripts/start-mcp.sh", shell=True)

def test():
    """テスト実行"""
    print_header("テスト実行")
    run_command("uv run pytest tests/ -v", "pytest実行")

def clean():
    """クリーンアップ"""
    print_header("クリーンアップ")
    run_command("make clean", "キャッシュ削除")

def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    commands = {
        'setup': setup,
        'check': check,
        'start': start,
        'mcp': start_mcp,
        'test': test,
        'clean': clean,
        'help': show_help,
    }

    if command in commands:
        commands[command]()
    else:
        print_error(f"不明なコマンド: {command}")
        print("\n利用可能なコマンド:")
        for cmd in commands.keys():
            print(f"  - {cmd}")
        print(f"\n詳細: python dev.py help")

if __name__ == "__main__":
    main()
