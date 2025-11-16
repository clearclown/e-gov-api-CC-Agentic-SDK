# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **FastAPI-based API server** for accessing Japanese legal information (laws and court precedents), powered by **Anthropic Claude Agent SDK**. The project integrates with e-gov API and Courts website to provide comprehensive legal data access with AI-enhanced search and analysis capabilities.

**Current Status**: Phase 1 & 2 Complete → Phase 3 (AI Integration) in progress

**Key Differentiator**: This project leverages Claude Agent SDK's production-ready agent framework to provide intelligent legal search, natural language queries, and context-aware legal analysis—going beyond simple data retrieval to offer true agentic capabilities.

## Why Claude Agent SDK?

### Strategic Advantages for This Project

**1. Automatic Context Management**
Legal documents can be extremely long (laws with hundreds of articles, court precedents spanning dozens of pages). The SDK's automatic context compaction prevents context window exhaustion during long-running analysis sessions.

**2. Built-in Tool Ecosystem**
File operations, code execution, and web search are essential for:
- Caching legal documents locally
- Processing legal XML from e-gov API
- Scraping court precedent data
- Performing cross-reference analysis

**3. MCP Integration for Legal Tools**
Custom MCP tools enable:
- Semantic search across legal corpus
- Law-precedent relationship mapping
- Automated legal citation validation
- Natural language legal queries

**4. Production-Ready Features**
- Error handling for flaky government APIs
- Session management for long legal research sessions
- Monitoring for compliance tracking
- Automatic prompt caching reduces API costs for repetitive queries

**5. Fine-Grained Permission Control**
Legal data requires careful access control. SDK's `allowedTools`, `disallowedTools`, and `permissionMode` enable precise capability constraints.

## Development Setup

This project uses `uv` as the package manager:

```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies (includes claude-agent-sdk)
uv pip install -e .

# Install Claude Agent SDK specifically
uv pip install claude-agent-sdk
```

## Architecture Overview

### Three-Layer Architecture with Agent SDK

```
┌─────────────────────────────────────────────────────┐
│           Claude Agent SDK Layer                    │
│  ┌─────────────────────────────────────────────┐  │
│  │  Agentic RAG Engine                          │  │
│  │  - Semantic search via pgvector              │  │
│  │  - Context-aware legal analysis              │  │
│  │  - Natural language query processing         │  │
│  └─────────────────────────────────────────────┘  │
└──────────────┬──────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────┐
│           FastAPI Application Layer                 │
│  ┌─────────────────────────────────────────────┐  │
│  │  REST API Endpoints                          │  │
│  │  - /api/v1/laws/*                            │  │
│  │  │  - /api/v1/cases/*                            │  │
│  │  - /api/v1/agent/query (Agent SDK endpoint)  │  │
│  └─────────────────────────────────────────────┘  │
└──────────────┬──────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────┐
│           Data Integration Layer                    │
│  ┌──────────┐  ┌──────────┐  ┌─────────────────┐  │
│  │ e-gov API│  │ Courts   │  │ PostgreSQL      │  │
│  │ Client   │  │ Scraper  │  │ + pgvector      │  │
│  └──────────┘  └──────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Data Layer Implementation

**1. Legal Data Layer** (`app/services/egov_client.py`)
- Integrates with e-gov API (https://elaws.e-gov.go.jp/)
- Handles law searches, retrieval, and amendment history
- XML parsing and normalization
- Redis caching for performance

**2. Case Law Layer** (`app/services/case_scraper.py`)
- Integrates with Courts website (https://www.courts.go.jp/)
- Web scraping for precedent data
- PDF extraction where applicable
- Structured case metadata storage

**3. AI Integration Layer** (`app/services/rag_service.py`)
- Agentic RAG with Claude Agent SDK
- Vector embeddings via pgvector
- Semantic search and similarity matching
- Context-aware legal reasoning

### API Design

RESTful API with versioning:

**Laws Endpoints**:
```
GET  /api/v1/laws/search              # Search laws
GET  /api/v1/laws/{law_id}            # Get specific law
GET  /api/v1/laws/{law_id}/history    # Amendment history
GET  /api/v1/laws/{law_id}/related    # Related precedents
```

**Cases Endpoints**:
```
GET  /api/v1/cases/search             # Search court precedents
GET  /api/v1/cases/{case_id}          # Get specific case
GET  /api/v1/cases/{case_id}/laws     # Related laws
```

**Agent Endpoints** (Claude Agent SDK):
```
POST /api/v1/agent/query              # Natural language legal query
POST /api/v1/agent/analyze            # Deep legal analysis
POST /api/v1/agent/chat               # Interactive legal consultation
GET  /api/v1/agent/session/{id}       # Session management
```

## Claude Agent SDK Integration

### Implementation Patterns

**Pattern 1: Stateless Query (One-shot analysis)**

```python
from claude_agent_sdk import query

async def analyze_legal_text(text: str) -> str:
    """
    One-shot legal text analysis using stateless query pattern.
    Best for: Quick law summaries, single-document analysis
    """
    result = await query(
        query=f"この法律文書を要約してください: {text}",
        allowed_tools=["read_file", "web_search"],
        permission_mode="acceptEdits",
    )

    async for message in result:
        if message.type == "text":
            return message.content
```

**Pattern 2: Stateful Session (Multi-turn conversation)**

```python
from claude_agent_sdk import ClaudeSDKClient

class LegalConsultationAgent:
    """
    Stateful agent for interactive legal consultation.
    Best for: Complex legal research, multi-document analysis
    """

    def __init__(self):
        self.client = ClaudeSDKClient(
            system_prompt="あなたは日本の法律の専門家です。",
            allowed_tools=[
                "search_law",      # Custom MCP tool
                "search_case",     # Custom MCP tool
                "read_file",
                "web_search",
            ],
            mcp_servers={
                "legal_tools": {
                    "command": "python",
                    "args": ["-m", "app.mcp.legal_server"],
                }
            },
        )

    async def chat(self, user_query: str):
        """Multi-turn conversation with context preservation"""
        async for message in self.client.query(user_query):
            yield message

    async def deep_analysis(self, law_id: str, case_ids: list[str]):
        """Complex analysis requiring multiple tool invocations"""
        query = f"法令ID {law_id} について、判例 {', '.join(case_ids)} との関連性を分析してください。"

        async for message in self.client.query(query):
            yield message
```

### Custom MCP Tools for Legal Domain

**Why TOON Format?**

このプロジェクトでは、MCP ツール定義に **TOON (Tool-Oriented Object Notation)** を採用します。

**TOON の利点:**
- 📉 **トークン削減**: JSON と比較して 30-60% のトークン削減
- 🚀 **構文効率**: 波括弧、角括弧、引用符などの冗長な句読点を排除
- 📖 **可読性向上**: YAML 風のインデント + CSV 風の表形式で直感的
- 💰 **コスト削減**: API コールのトークン数が減少し、運用コストを削減

**Tool Definition with TOON** (`app/mcp/legal_tools.py`):

```python
from claude_agent_sdk import tool

@tool(
    name="search_law",
    description="日本の法令を検索します。キーワード、法令番号、または自然言語で検索できます。",
    # TOON形式でスキーマを定義（JSONより30-60%トークン削減）
    input_schema="""
type: object
properties:
  query:
    type: string
    description: 検索クエリ（キーワードまたは法令番号）
  category:
    type: string
    enum[4]: constitution,law,ordinance,rule
    description: 法令の種類（憲法、法律、政令、省令）
  limit:
    type: integer
    description: 取得する結果の最大数
    default: 10
required[1]: query
""",
)
async def search_law(args: dict) -> dict:
    """法令検索ツール"""
    from app.services.egov_client import EgovClient

    client = EgovClient()
    results = await client.search(
        query=args["query"],
        category=args.get("category"),
        limit=args.get("limit", 10),
    )

    return {
        "content": [
            {
                "type": "text",
                "text": f"検索結果: {len(results)}件の法令が見つかりました。\n\n"
                       + "\n\n".join([
                           f"【{r['name']}】\n"
                           f"法令番号: {r['law_num']}\n"
                           f"施行日: {r['enforcement_date']}\n"
                           f"概要: {r['summary']}"
                           for r in results
                       ]),
            }
        ]
    }


@tool(
    name="search_case",
    description="判例を検索します。事件名、キーワード、または裁判所名で検索できます。",
    # TOON形式: enum配列の長さを明示的に指定
    input_schema="""
type: object
properties:
  keywords:
    type: string
    description: 検索キーワード
  court:
    type: string
    enum[5]: supreme,high,district,family,summary
    description: 裁判所の種類
  date_from:
    type: string
    description: 判決日の開始日（YYYY-MM-DD）
  date_to:
    type: string
    description: 判決日の終了日（YYYY-MM-DD）
required[1]: keywords
""",
)
async def search_case(args: dict) -> dict:
    """判例検索ツール"""
    from app.services.case_service import CaseService

    service = CaseService()
    results = await service.search(
        keywords=args["keywords"],
        court=args.get("court"),
        date_from=args.get("date_from"),
        date_to=args.get("date_to"),
    )

    return {
        "content": [
            {
                "type": "text",
                "text": f"検索結果: {len(results)}件の判例が見つかりました。\n\n"
                       + "\n\n".join([
                           f"【{r['case_name']}】\n"
                           f"裁判所: {r['court']}\n"
                           f"判決日: {r['decision_date']}\n"
                           f"事件番号: {r['case_number']}\n"
                           f"要旨: {r['summary']}"
                           for r in results
                       ]),
            }
        ]
    }


@tool(
    name="analyze_law_case_relationship",
    description="特定の法令と判例の関連性を分析します。",
    # TOON形式: シンプルな構造で最大限のトークン削減
    input_schema="""
type: object
properties:
  law_id: {type: string, description: 法令ID}
  case_id: {type: string, description: 判例ID}
required[2]: law_id,case_id
""",
)
async def analyze_law_case_relationship(args: dict) -> dict:
    """法令と判例の関連性分析ツール"""
    from app.services.relationship_analyzer import RelationshipAnalyzer

    analyzer = RelationshipAnalyzer()
    result = await analyzer.analyze(
        law_id=args["law_id"],
        case_id=args["case_id"],
    )

    return {
        "content": [
            {
                "type": "text",
                "text": f"関連性分析結果:\n\n"
                       f"適用条文: {', '.join(result['applied_articles'])}\n"
                       f"引用回数: {result['citation_count']}\n"
                       f"判断の要旨: {result['judgment_summary']}\n"
                       f"関連度スコア: {result['relevance_score']}/100",
            }
        ]
    }
```

### MCP Server Configuration

**Project-level MCP Config** (`.mcp.json`):

```json
{
  "mcpServers": {
    "legal_tools": {
      "command": "uv",
      "args": ["run", "python", "-m", "app.mcp.legal_server"],
      "env": {
        "EGOV_API_KEY": "${EGOV_API_KEY}",
        "DATABASE_URL": "${DATABASE_URL}"
      }
    },
    "vector_search": {
      "command": "uv",
      "args": ["run", "python", "-m", "app.mcp.vector_server"],
      "env": {
        "POSTGRES_VECTOR_URL": "${POSTGRES_VECTOR_URL}"
      }
    }
  }
}
```

**MCP Server Implementation** (`app/mcp/legal_server.py`):

```python
from claude_agent_sdk import create_sdk_mcp_server
from app.mcp.legal_tools import search_law, search_case, analyze_law_case_relationship

# Create MCP server with custom tools
server = create_sdk_mcp_server(
    name="legal_tools",
    description="日本の法令・判例検索および分析ツール",
    tools=[
        search_law,
        search_case,
        analyze_law_case_relationship,
    ],
)

if __name__ == "__main__":
    server.run()
```

## Advanced Features

### 1. Hook System for Legal Compliance

```python
from claude_agent_sdk import ClaudeSDKClient, Hook

class ComplianceHook(Hook):
    """法律データアクセスの監査ログを記録"""

    async def on_pre_tool_use(self, tool_name: str, args: dict):
        # ツール使用前のログ記録
        await log_access(
            tool=tool_name,
            args=args,
            timestamp=datetime.now(),
        )

    async def on_post_tool_use(self, tool_name: str, result: dict):
        # ツール使用後の結果監査
        await audit_result(
            tool=tool_name,
            result=result,
            timestamp=datetime.now(),
        )

client = ClaudeSDKClient(
    hooks=[ComplianceHook()],
)
```

### 2. Session Forking for Parallel Analysis

```python
async def compare_legal_interpretations(law_id: str):
    """複数の解釈パターンを並列分析"""

    base_client = ClaudeSDKClient()

    # ベースセッションでコンテキスト構築
    await base_client.query(f"法令ID {law_id} について分析を開始してください")

    # 異なる解釈パターンで分岐
    interpretation_a = base_client.fork_session()
    interpretation_b = base_client.fork_session()

    results = await asyncio.gather(
        interpretation_a.query("条文の文理解釈を行ってください"),
        interpretation_b.query("立法趣旨から解釈してください"),
    )

    return results
```

### 3. Subagent Delegation for Complex Research

```python
async def comprehensive_legal_research(topic: str):
    """複雑な法律調査をサブエージェントに委任"""

    main_agent = ClaudeSDKClient(
        allowed_tools=["Task"],  # Subagent delegation tool
    )

    query = f"""
    以下のトピックについて包括的な法律調査を実施してください: {topic}

    1. 関連法令の検索（サブエージェントに委任）
    2. 判例の検索（サブエージェントに委任）
    3. 学説の調査（サブエージェントに委任）
    4. 総合分析（メインエージェント）
    """

    async for message in main_agent.query(query):
        yield message
```

## TOON vs JSON: Migration Guide

### Why Migrate to TOON?

**TOON (Tool-Oriented Object Notation)** は、LLM向けに最適化された構造化データフォーマットです。

**トークン削減の実例:**

従来の JSON 形式:
```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "検索クエリ（キーワードまたは法令番号）"
    },
    "category": {
      "type": "string",
      "enum": ["constitution", "law", "ordinance", "rule"],
      "description": "法令の種類（憲法、法律、政令、省令）"
    },
    "limit": {
      "type": "integer",
      "description": "取得する結果の最大数",
      "default": 10
    }
  },
  "required": ["query"]
}
```
**トークン数: 約 120 トークン**

TOON 形式:
```
type: object
properties:
  query:
    type: string
    description: 検索クエリ（キーワードまたは法令番号）
  category:
    type: string
    enum[4]: constitution,law,ordinance,rule
    description: 法令の種類（憲法、法律、政令、省令）
  limit:
    type: integer
    description: 取得する結果の最大数
    default: 10
required[1]: query
```
**トークン数: 約 65 トークン（45% 削減）**

さらに簡潔な TOON 形式（インライン記法）:
```
type: object
properties:
  query: {type: string, description: 検索クエリ（キーワードまたは法令番号）}
  category: {type: string, enum[4]: constitution,law,ordinance,rule, description: 法令の種類}
  limit: {type: integer, description: 取得する結果の最大数, default: 10}
required[1]: query
```
**トークン数: 約 50 トークン（58% 削減）**

### TOON Syntax Guide

**基本構文:**

1. **シンプルなオブジェクト:**
```
name: Alice
age: 30
city: Tokyo
```

2. **ネストされたオブジェクト:**
```
user:
  name: Alice
  age: 30
  address:
    city: Tokyo
    zip: 100-0001
```

3. **均一な配列（表形式）:**
```
users[3,]{id,name,age}:
  1,Alice,30
  2,Bob,25
  3,Charlie,35
```

4. **配列の長さインジケーター:**
```
tags[5]: tag1,tag2,tag3,tag4,tag5
enum[3]: option1,option2,option3
required[2]: field1,field2
```

5. **インライン記法（簡潔化）:**
```
properties:
  name: {type: string, description: 名前}
  age: {type: integer, minimum: 0, maximum: 150}
```

### Python Implementation

**TOON エンコード/デコード:**

```python
from toon import encode, decode

# JSON to TOON
json_data = {
    "name": "Alice",
    "age": 30,
    "tags": ["python", "fastapi", "claude"]
}

toon_string = encode(json_data)
print(toon_string)
# Output:
# name: Alice
# age: 30
# tags[3]: python,fastapi,claude

# TOON to Python dict
original_data = decode(toon_string)
```

**MCP ツールでの使用:**

```python
from claude_agent_sdk import tool

# TOON形式のスキーマ定義
@tool(
    name="example_tool",
    description="Example tool with TOON schema",
    input_schema="""
type: object
properties:
  name: {type: string, description: ユーザー名}
  age: {type: integer, minimum: 0, description: 年齢}
  tags[]: {type: string, description: タグリスト}
required[1]: name
""",
)
async def example_tool(args: dict) -> dict:
    # args is automatically parsed from TOON to dict
    return {"result": f"Hello, {args['name']}"}
```

### Migration Checklist

**既存の JSON スキーマを TOON に移行する手順:**

1. **波括弧・角括弧を削除**
   - `{` `}` → インデントで構造化
   - `[` `]` → 長さインジケーター `[N]`

2. **引用符を削除**
   - `"key": "value"` → `key: value`
   - `"enum": ["a", "b"]` → `enum[2]: a,b`

3. **配列の長さを明示**
   - `"required": ["field1", "field2"]` → `required[2]: field1,field2`
   - `"enum": ["a", "b", "c"]` → `enum[3]: a,b,c`

4. **簡潔化できる箇所はインライン記法を使用**
   - シンプルなプロパティは 1 行で記述
   - ネストが深い場合は複数行で構造化

5. **Python TOON ライブラリのインストール**
```bash
uv pip install python-toon
```

### Best Practices

**TOON を使うべき場合:**
- ✅ MCP ツールの `input_schema` 定義
- ✅ 均一な構造を持つデータ（法令データ、判例データ）
- ✅ 繰り返し使用されるスキーマ（トークンコスト削減）
- ✅ API レスポンスの構造定義

**JSON を使うべき場合:**
- ❌ 深くネストした異種混合データ
- ❌ 既存の JSON ツールとの互換性が必要な場合
- ❌ 動的に構造が変わるデータ

### Legal Domain Examples with TOON

**法令検索結果のフォーマット:**
```
results[100,]{law_id,name,law_num,enforcement_date,category}:
  LAW001,憲法,昭和21年憲法,1947-05-03,constitution
  LAW002,民法,明治29年法律第89号,1898-07-16,law
  LAW003,刑法,明治40年法律第45号,1908-10-01,law
  ...
```

**判例検索結果のフォーマット:**
```
cases[50,]{case_id,case_name,court,decision_date,case_number}:
  CASE001,表現の不自由展かんさい事件,最高裁判所,2023-04-15,令和4年(行ツ)第123号
  CASE002,...,...,...,
  ...
```

## Key Technical Decisions

**Package Manager**: uv
- Fast, reliable dependency management
- Reproducible builds
- Better than pip for production environments

**API Framework**: FastAPI
- Async support for concurrent API calls
- Automatic OpenAPI documentation
- Type hints and validation
- Native Python 3.10+ features

**Agent Framework**: Claude Agent SDK
- Production-ready agent harness
- Automatic context management
- Built-in tool ecosystem
- MCP integration for extensibility
- Fine-grained permission control

**Structured Data Format**: TOON (Tool-Oriented Object Notation)
- 30-60% token reduction compared to JSON
- Optimized for LLM processing
- YAML-style indentation + CSV-style tabular format
- Explicit metadata with array length indicators
- Significant cost reduction for API calls
- Better readability and maintainability

**Database**: PostgreSQL 16 + pgvector
- Vector similarity search for semantic matching
- Full-text search for legal documents
- JSONB for flexible schema
- Robust transaction support

**Cache**: Redis 7
- High-performance caching for API responses
- Session storage for agent conversations
- Rate limiting and request throttling

**Python Version**: 3.12+
- Modern async features
- Pattern matching for complex logic
- Performance improvements
- Type hint enhancements

## Data Sources

**1. e-gov Law API**
- Official source for all Japanese laws
- Real-time updates and amendment tracking
- XML format requiring parsing

**2. Courts Website**
- Supreme Court precedents
- High Court, District Court decisions
- Requires web scraping (no official API)

**3. Future Considerations**
- Commercial case databases (LEX/DB, Westlaw Japan)
- Open legal data initiatives
- Legal scholarship repositories

## Development Phases

### Phase 1: Foundation ✅ COMPLETE
- [x] FastAPI project initialization
- [x] e-gov API client implementation
- [x] Basic law search endpoints
- [x] Docker/Podman support
- [x] Redis caching

### Phase 2: Case Law Integration ✅ COMPLETE
- [x] Court precedent scraper implementation
- [x] Case search endpoints
- [x] PostgreSQL database schema
- [x] Data normalization and storage

### Phase 3: AI Integration 🔄 IN PROGRESS
- [ ] Claude Agent SDK installation and setup
- [ ] Custom MCP tools implementation (`search_law`, `search_case`, etc.)
- [ ] MCP server deployment
- [ ] Agent endpoints (`/api/v1/agent/*`)
- [ ] Vector embeddings with pgvector
- [ ] Agentic RAG implementation
- [ ] Session management for conversations

### Phase 4: Advanced Features 📋 PLANNED
- [ ] Law-case relationship graph visualization
- [ ] Citation network analysis
- [ ] Automatic legal document summarization
- [ ] Natural language legal consultation interface
- [ ] Multi-turn conversation support
- [ ] Subagent delegation for complex research
- [ ] Hook system for compliance logging

## Performance Optimization

**Caching Strategy**:
- Redis for API response caching (TTL: 1 hour)
- Prompt caching for repetitive agent queries
- Vector search result caching

**Database Optimization**:
- Indexes on frequently queried fields
- Materialized views for complex joins
- Connection pooling
- Prepared statements

**Agent SDK Optimization**:
- Tool permission allowlisting (reduce unnecessary invocations)
- Session reuse for multi-turn conversations
- Automatic context compaction
- Streaming responses for better UX

## Security Considerations

**API Security**:
- Rate limiting per client
- API key authentication for agent endpoints
- Input validation and sanitization
- SQL injection prevention

**Agent Security**:
- Tool permission control via `allowedTools`
- Audit logging via hook system
- Sensitive data masking in logs
- Secure credential management for MCP servers

**Data Privacy**:
- No storage of personal legal queries (unless explicitly opted in)
- Anonymized analytics
- GDPR compliance considerations for EU users

## Testing Strategy

**Unit Tests**:
- e-gov API client
- Court scraper
- MCP tool functions
- Database models

**Integration Tests**:
- Full API endpoint flows
- Agent SDK integration
- MCP server communication
- Database transactions

**Agent Tests**:
- Tool invocation accuracy
- Context preservation across turns
- Error handling and recovery
- Permission enforcement

## Monitoring and Observability

**Metrics**:
- API response times
- Agent query latency
- Cache hit rates
- Tool invocation frequency
- Database query performance

**Logging**:
- Structured JSON logs
- Request/response logging
- Agent conversation logs
- Error tracking with stack traces

**Alerting**:
- API downtime alerts
- Database connection failures
- Agent SDK errors
- MCP server disconnections

## Important Notes

**Data Accuracy**:
- Legal data accuracy is critical—always verify sources
- Implement versioning for laws (amendments over time)
- Cross-reference with official government sources

**Language**:
- All API responses in Japanese (legal data is in Japanese)
- Agent prompts optimized for Japanese legal terminology
- Multilingual summary generation (future feature)

**Update Frequency**:
- Daily sync with e-gov API for law updates
- Weekly scrape of new court precedents
- Real-time updates for constitutional amendments (rare but critical)

**Agent Behavior**:
- MCP tools should handle both structured queries and natural language
- Always cite sources in agent responses
- Provide confidence scores for AI-generated analyses
- Distinguish between legal facts and AI interpretations

## Resources

**Official Documentation**:
- [Claude Agent SDK Overview](https://docs.claude.com/ja/docs/agent-sdk/overview) - SDK の全体像
- [Claude Agent SDK Python Reference](https://docs.claude.com/ja/docs/agent-sdk/python) - Python 実装
- [MCP Integration Guide](https://docs.claude.com/ja/docs/agent-sdk/mcp) - MCP 統合
- [FastAPI](https://fastapi.tiangolo.com/) - Web フレームワーク
- [e-gov Law API Specification](https://elaws.e-gov.go.jp/apitop/) - 法令API仕様
- [uv Package Manager](https://github.com/astral-sh/uv) - パッケージマネージャー
- [PostgreSQL + pgvector](https://github.com/pgvector/pgvector) - ベクトル検索

**TOON Format**:
- [TOON Official Documentation - Zenn](https://zenn.dev/akasan/articles/1fa9ad262ac719) - TOON 仕様
- [python-toon Library](https://github.com/akasan/python-toon) - Python 実装
- [TOON vs JSON Comparison](https://medium.com/medialesson/json-vs-toon-a-new-era-of-structured-input-19cbb7fc552b) - 比較記事

**Related Projects**:
- [Claude Code](https://claude.ai/code) - The IDE this project is designed for
- [Model Context Protocol](https://modelcontextprotocol.io/) - Tool integration standard

**Data Sources**:
- [e-gov Law Database](https://elaws.e-gov.go.jp/)
- [Courts Website](https://www.courts.go.jp/)

## Contributing Guidelines

**Code Style**:
- PEP 8 compliance
- Type hints for all function signatures
- Docstrings in Japanese for domain-specific functions
- Docstrings in English for technical infrastructure

**Commit Messages**:
- Conventional Commits format
- Japanese OK for feature commits
- English preferred for infrastructure changes

**Testing Requirements**:
- Unit tests for all new functions
- Integration tests for API endpoints
- Agent behavior tests for MCP tools
- Minimum 80% code coverage

**Documentation**:
- Update CLAUDE.md for architectural changes
- Update README.md for user-facing changes
- Add inline comments for complex legal logic
- Maintain API documentation in OpenAPI format

## Development Workflow

**Local Development**:
```bash
# Start infrastructure
podman compose up -d postgres redis

# Run development server with auto-reload
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
uv run pytest

# Type checking
uv run mypy app/

# Linting
uv run ruff check app/
```

**Docker/Podman Development**:
```bash
# Build and start all services
podman compose up -d

# View logs
podman compose logs -f app

# Execute commands in container
podman compose exec app uv run python -m app.scripts.seed_db

# Rebuild after dependency changes
podman compose up -d --build
```

**MCP Server Development**:
```bash
# Test MCP server locally
uv run python -m app.mcp.legal_server

# Validate MCP tool schemas
uv run python -m app.scripts.validate_mcp_tools

# Debug MCP communication
export MCP_DEBUG=1
uv run python -m app.mcp.legal_server
```

---

*This document is maintained by the development team and should be updated whenever architectural decisions or integration patterns change.*
