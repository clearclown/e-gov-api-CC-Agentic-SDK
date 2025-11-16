# 📱 e-gov 法律相談 AI チャット - フロントエンド

Claude Agent SDK と直接会話できる Next.js フロントエンドアプリケーション

## 🎯 技術スタック

- **Next.js 15** - React フレームワーク (App Router)
- **TypeScript** - 型安全な開発
- **Tailwind CSS** - ユーティリティファーストCSS
- **shadcn/ui** - 高品質UIコンポーネント
- **Biome** - 高速Linter & Formatter
- **Vitest** - 単体・結合テスト
- **Playwright** - E2Eテスト

## 🚀 セットアップ

### 方法1: npm で個別起動

```bash
# 依存関係のインストール
npm install

# 環境変数の設定
cp .env.example .env

# 開発サーバー起動
npm run dev
```

### 方法2: Make コマンド（推奨）

```bash
# プロジェクトルートから
make frontend-setup   # セットアップ
make frontend-dev     # 開発サーバー起動
```

### 方法3: Docker Compose（最も簡単）

```bash
# プロジェクトルートから
make docker-up  # バックエンド + フロントエンド + DB を一括起動
```

アクセスURL: http://localhost:3000

## 📦 利用可能なコマンド

```bash
npm run dev           # 開発サーバー起動
npm run build         # 本番ビルド
npm run start         # 本番サーバー起動
npm run lint          # Biome lintチェック
npm run lint:fix      # Biome lint自動修正
npm run format        # Biome フォーマット
npm run test          # Vitest テスト実行
npm run test:ui       # Vitest UI表示
npm run test:coverage # カバレッジ測定
npm run test:e2e      # Playwright E2Eテスト
npm run test:e2e:ui   # Playwright UI表示
```

## 🧪 テスト

### 単体・結合テスト (Vitest)

```bash
# テスト実行
npm run test

# UI モードで実行
npm run test:ui

# カバレッジ測定
npm run test:coverage
```

### E2Eテスト (Playwright)

```bash
# E2Eテスト実行
npm run test:e2e

# UI モードで実行
npm run test:e2e:ui
```

## 📁 ディレクトリ構造

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx         # ルートレイアウト
│   │   ├── page.tsx           # トップページ
│   │   └── globals.css        # グローバルCSS
│   ├── components/
│   │   ├── ui/                # shadcn/ui コンポーネント
│   │   │   ├── button.tsx
│   │   │   └── card.tsx
│   │   └── chat/              # チャット関連コンポーネント
│   │       ├── ChatWindow.tsx
│   │       └── ChatMessage.tsx
│   ├── lib/
│   │   ├── api-client.ts      # Agent SDK API クライアント
│   │   └── utils.ts           # ユーティリティ関数
│   └── tests/
│       ├── components/        # コンポーネントテスト
│       ├── e2e/               # E2Eテスト
│       └── setup.ts           # テストセットアップ
├── public/                     # 静的ファイル
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── biome.json                  # Biome設定
├── vitest.config.ts           # Vitestテスト
├── playwright.config.ts       # Playwright設定
└── Dockerfile                 # Docker設定
```

## 🎨 主な機能

### ChatWindow コンポーネント

- リアルタイムストリーミングチャット
- セッション管理（継続的な会話）
- 自動スクロール
- ローディング状態表示
- エラーハンドリング

### API クライアント

```typescript
import { apiClient } from '@/lib/api-client';

// セッション作成
const session = await apiClient.createSession();

// ストリーミングチャット
for await (const chunk of apiClient.chat(message, sessionId)) {
  console.log(chunk.content);
}
```

## 🔧 環境変数

`.env` ファイルで設定：

```bash
# APIエンドポイントURL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🐛 トラブルシューティング

### ポートが既に使用されている

```bash
# ポート3000を使用しているプロセスを終了
lsof -ti:3000 | xargs kill -9
```

### 依存関係のエラー

```bash
# node_modules を削除して再インストール
rm -rf node_modules package-lock.json
npm install
```

## 📚 参考リンク

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/)
- [shadcn/ui](https://ui.shadcn.com/)
- [Biome](https://biomejs.dev/)
- [Vitest](https://vitest.dev/)
- [Playwright](https://playwright.dev/)

## 🤝 開発ガイドライン

- **コードスタイル**: Biome で自動管理
- **コミットメッセージ**: Conventional Commits 形式
- **テスト**: 新機能には必ずテストを追加
- **型安全性**: `any` の使用を最小限に

---

Made with ❤️ using Claude Agent SDK
