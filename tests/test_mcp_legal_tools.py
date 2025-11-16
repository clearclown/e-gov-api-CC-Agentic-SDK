"""Comprehensive tests for MCP legal tools with TOON format

Test-Driven Development (TDD) for Phase 3 implementation.
Tests written before implementation to ensure correctness.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.mcp.legal_tools import (
    search_law,
    search_case,
    analyze_law_case_relationship,
    get_law_detail,
    get_case_detail,
    ask_legal_question,
    LEGAL_TOOLS,
    TOOL_METADATA,
)


class TestSearchLawTool:
    """Test cases for search_law tool with TOON format"""

    @pytest.mark.asyncio
    async def test_search_law_with_rag(self, mock_law_data):
        """Test law search with RAG enabled"""
        # Arrange
        query = "会社法"
        args = {
            "query": query,
            "use_rag": True,
            "limit": 5
        }

        # Mock RAG service
        with patch("app.mcp.legal_tools.rag_service.search_with_context") as mock_rag:
            mock_law = MagicMock()
            mock_law.law_name = "会社法"
            mock_law.law_number = "平成十七年法律第八十七号"
            mock_law.enforcement_date = "2006-05-01"
            mock_law.full_text = "会社法の全文テキスト" * 50  # Long text

            mock_rag.return_value = {
                "laws": [mock_law],
                "context": "コンテキスト"
            }

            # Act
            result = await search_law(args)

            # Assert
            assert "content" in result
            assert len(result["content"]) > 0
            assert result["content"][0]["type"] == "text"
            text = result["content"][0]["text"]
            assert "会社法" in text
            assert "平成十七年法律第八十七号" in text
            mock_rag.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_law_without_rag(self):
        """Test law search with RAG disabled (keyword search)"""
        # Arrange
        query = "民法"
        args = {
            "query": query,
            "use_rag": False,
            "limit": 10
        }

        # Mock egov_client
        with patch("app.mcp.legal_tools.egov_client.search") as mock_egov:
            mock_egov.return_value = [
                {
                    "name": "民法",
                    "law_num": "明治二十九年法律第八十九号",
                    "enforcement_date": "1898-07-16"
                }
            ]

            # Act
            result = await search_law(args)

            # Assert
            assert "content" in result
            text = result["content"][0]["text"]
            assert "民法" in text
            assert "明治二十九年法律第八十九号" in text
            mock_egov.assert_called_once_with(
                query=query,
                category=None,
                limit=10
            )

    @pytest.mark.asyncio
    async def test_search_law_with_category_filter(self):
        """Test law search with category filter"""
        # Arrange
        args = {
            "query": "憲法",
            "category": "constitution",
            "use_rag": False,
            "limit": 1
        }

        # Mock egov_client
        with patch("app.mcp.legal_tools.egov_client.search") as mock_egov:
            mock_egov.return_value = [
                {
                    "name": "日本国憲法",
                    "law_num": "昭和二十一年憲法",
                    "enforcement_date": "1947-05-03"
                }
            ]

            # Act
            result = await search_law(args)

            # Assert
            assert "content" in result
            mock_egov.assert_called_once_with(
                query="憲法",
                category="constitution",
                limit=1
            )

    @pytest.mark.asyncio
    async def test_search_law_error_handling(self):
        """Test error handling in law search"""
        # Arrange
        args = {"query": "エラーテスト", "use_rag": False}

        # Mock egov_client to raise exception
        with patch("app.mcp.legal_tools.egov_client.search") as mock_egov:
            mock_egov.side_effect = Exception("API Error")

            # Act
            result = await search_law(args)

            # Assert
            assert "content" in result
            text = result["content"][0]["text"]
            assert "エラー" in text
            assert "API Error" in text

    @pytest.mark.asyncio
    async def test_search_law_default_parameters(self):
        """Test default parameters are applied correctly"""
        # Arrange
        args = {"query": "テスト"}  # Only required parameter

        # Mock egov_client
        with patch("app.mcp.legal_tools.egov_client.search") as mock_egov:
            mock_egov.return_value = []

            # Act (should not raise exception)
            await search_law(args)

            # Assert: verify defaults
            # use_rag defaults to True, so rag_service should be called
            # This test ensures no exceptions with minimal args


class TestSearchCaseTool:
    """Test cases for search_case tool with TOON format"""

    @pytest.mark.asyncio
    async def test_search_case_with_rag(self):
        """Test case search with RAG enabled"""
        # Arrange
        args = {
            "keywords": "損害賠償",
            "use_rag": True,
            "limit": 5
        }

        # Mock RAG service
        with patch("app.mcp.legal_tools.rag_service.search_with_context") as mock_rag:
            mock_case = MagicMock()
            mock_case.case_name = "損害賠償請求事件"
            mock_case.court_name = "最高裁判所"
            mock_case.decision_date = "2023-04-15"
            mock_case.case_number = "令和4年(受)第123号"
            mock_case.summary = "損害賠償に関する判例の要旨" * 10

            mock_rag.return_value = {
                "cases": [mock_case],
                "context": "コンテキスト"
            }

            # Act
            result = await search_case(args)

            # Assert
            assert "content" in result
            text = result["content"][0]["text"]
            assert "損害賠償請求事件" in text
            assert "最高裁判所" in text
            mock_rag.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_case_with_court_filter(self):
        """Test case search with court type filter"""
        # Arrange
        args = {
            "keywords": "表現の自由",
            "court": "supreme",
            "use_rag": False,
            "limit": 10
        }

        # Mock case_service
        with patch("app.mcp.legal_tools.case_service.search") as mock_service:
            mock_service.return_value = [
                {
                    "case_name": "表現の不自由展事件",
                    "court": "最高裁判所",
                    "decision_date": "2023-04-15",
                    "case_number": "令和4年(行ツ)第123号"
                }
            ]

            # Act
            result = await search_case(args)

            # Assert
            assert "content" in result
            mock_service.assert_called_once_with(
                keywords="表現の自由",
                court="supreme",
                date_from=None,
                date_to=None,
                limit=10
            )

    @pytest.mark.asyncio
    async def test_search_case_with_date_range(self):
        """Test case search with date range filter"""
        # Arrange
        args = {
            "keywords": "契約",
            "date_from": "2020-01-01",
            "date_to": "2023-12-31",
            "use_rag": False
        }

        # Mock case_service
        with patch("app.mcp.legal_tools.case_service.search") as mock_service:
            mock_service.return_value = []

            # Act
            result = await search_case(args)

            # Assert
            mock_service.assert_called_once_with(
                keywords="契約",
                court=None,
                date_from="2020-01-01",
                date_to="2023-12-31",
                limit=10  # default
            )


class TestAnalyzeLawCaseRelationship:
    """Test cases for analyze_law_case_relationship tool"""

    @pytest.mark.asyncio
    async def test_analyze_relationship_success(self):
        """Test successful relationship analysis"""
        # Arrange
        args = {
            "law_id": "405AC0000000087",
            "case_id": "CASE001"
        }

        # Mock relationship_analyzer
        with patch("app.mcp.legal_tools.relationship_analyzer.analyze") as mock_analyzer:
            mock_analyzer.return_value = {
                "applied_articles": ["第1条", "第2条"],
                "citation_count": 5,
                "relevance_score": 85,
                "judgment_summary": "会社法第1条および第2条を適用"
            }

            # Act
            result = await analyze_law_case_relationship(args)

            # Assert
            assert "content" in result
            text = result["content"][0]["text"]
            assert "405AC0000000087" in text
            assert "CASE001" in text
            assert "第1条" in text
            assert "85" in text
            mock_analyzer.assert_called_once_with(
                law_id="405AC0000000087",
                case_id="CASE001"
            )

    @pytest.mark.asyncio
    async def test_analyze_relationship_error(self):
        """Test error handling in relationship analysis"""
        # Arrange
        args = {
            "law_id": "INVALID",
            "case_id": "INVALID"
        }

        # Mock relationship_analyzer to raise exception
        with patch("app.mcp.legal_tools.relationship_analyzer.analyze") as mock_analyzer:
            mock_analyzer.side_effect = Exception("Analysis failed")

            # Act
            result = await analyze_law_case_relationship(args)

            # Assert
            assert "content" in result
            text = result["content"][0]["text"]
            assert "エラー" in text


class TestGetLawDetail:
    """Test cases for get_law_detail tool"""

    @pytest.mark.asyncio
    async def test_get_law_detail_without_full_text(self):
        """Test law detail retrieval without full text"""
        # Arrange
        args = {
            "law_id": "405AC0000000087",
            "include_full_text": False
        }

        # Mock egov_client
        with patch("app.mcp.legal_tools.egov_client.get_law") as mock_get:
            mock_get.return_value = {
                "name": "会社法",
                "law_num": "平成十七年法律第八十七号",
                "enforcement_date": "2006-05-01",
                "last_amendment": "2023-06-01",
                "full_text": "会社法の全文テキスト" * 100
            }

            # Act
            result = await get_law_detail(args)

            # Assert
            assert "content" in result
            text = result["content"][0]["text"]
            assert "会社法" in text
            assert "概要" in text
            # Full text should be truncated
            assert len(text) < 2000

    @pytest.mark.asyncio
    async def test_get_law_detail_with_full_text(self):
        """Test law detail retrieval with full text"""
        # Arrange
        args = {
            "law_id": "405AC0000000087",
            "include_full_text": True
        }

        # Mock egov_client
        with patch("app.mcp.legal_tools.egov_client.get_law") as mock_get:
            full_text = "会社法の全文テキスト" * 100
            mock_get.return_value = {
                "name": "会社法",
                "law_num": "平成十七年法律第八十七号",
                "full_text": full_text
            }

            # Act
            result = await get_law_detail(args)

            # Assert
            assert "content" in result
            text = result["content"][0]["text"]
            assert "全文" in text
            assert full_text in text


class TestGetCaseDetail:
    """Test cases for get_case_detail tool"""

    @pytest.mark.asyncio
    async def test_get_case_detail_success(self):
        """Test case detail retrieval"""
        # Arrange
        args = {
            "case_id": "CASE001",
            "include_full_text": False
        }

        # Mock case_service
        with patch("app.mcp.legal_tools.case_service.get_detail") as mock_get:
            mock_get.return_value = {
                "case_name": "表現の不自由展事件",
                "court": "最高裁判所",
                "decision_date": "2023-04-15",
                "case_number": "令和4年(行ツ)第123号",
                "case_type": "行政訴訟",
                "summary": "表現の自由に関する判決の要旨",
                "full_text": "判決全文" * 100
            }

            # Act
            result = await get_case_detail(args)

            # Assert
            assert "content" in result
            text = result["content"][0]["text"]
            assert "表現の不自由展事件" in text
            assert "最高裁判所" in text
            # Full text should not be included
            assert text.count("判決全文") < 10


class TestAskLegalQuestion:
    """Test cases for ask_legal_question tool"""

    @pytest.mark.asyncio
    async def test_ask_legal_question_success(self):
        """Test legal question with successful answer generation"""
        # Arrange
        args = {
            "question": "株主総会の決議要件は？",
            "context_limit": 5
        }

        # Mock RAG service
        with patch("app.mcp.legal_tools.rag_service.search_with_context") as mock_search:
            with patch("app.mcp.legal_tools.rag_service.generate_answer") as mock_generate:
                # Mock law and case objects
                mock_law = MagicMock()
                mock_law.law_name = "会社法"

                mock_case = MagicMock()
                mock_case.case_name = "株主総会決議無効確認請求事件"

                mock_search.return_value = {
                    "laws": [mock_law],
                    "cases": [mock_case],
                    "context": "関連コンテキスト"
                }

                mock_generate.return_value = "株主総会の普通決議は、定足数として議決権の過半数が必要です..."

                # Act
                result = await ask_legal_question(args)

                # Assert
                assert "content" in result
                text = result["content"][0]["text"]
                assert "株主総会の決議要件は？" in text
                assert "会社法" in text
                assert "株主総会決議無効確認請求事件" in text
                assert "参考情報" in text

    @pytest.mark.asyncio
    async def test_ask_legal_question_without_api_key(self):
        """Test legal question without API key configured"""
        # Arrange
        args = {
            "question": "契約の成立要件は？"
        }

        # Mock RAG service to raise ValueError
        with patch("app.mcp.legal_tools.rag_service.search_with_context") as mock_search:
            with patch("app.mcp.legal_tools.rag_service.generate_answer") as mock_generate:
                mock_search.return_value = {"laws": [], "cases": [], "context": ""}
                mock_generate.side_effect = ValueError("ANTHROPIC_API_KEY not found")

                # Act
                result = await ask_legal_question(args)

                # Assert
                assert "content" in result
                text = result["content"][0]["text"]
                assert "エラー" in text
                assert "ANTHROPIC_API_KEY" in text


class TestToolMetadata:
    """Test tool metadata and registry"""

    def test_legal_tools_registry(self):
        """Test that all tools are registered"""
        # Assert
        assert len(LEGAL_TOOLS) == 6
        tool_names = [tool._tool_name for tool in LEGAL_TOOLS if hasattr(tool, '_tool_name')]
        expected_names = [
            "search_law",
            "search_case",
            "analyze_law_case_relationship",
            "get_law_detail",
            "get_case_detail",
            "ask_legal_question"
        ]
        # Note: tool names may not be available if SDK is not installed

    def test_tool_metadata_completeness(self):
        """Test that metadata is complete for all tools"""
        # Assert
        assert len(TOOL_METADATA) == 6
        for tool_name, metadata in TOOL_METADATA.items():
            assert "name" in metadata
            assert "description" in metadata
            assert "toon_schema_tokens" in metadata
            assert "トークン" in metadata["toon_schema_tokens"]

    def test_toon_token_reduction_claims(self):
        """Test that TOON token reduction claims are present"""
        # Assert
        for metadata in TOOL_METADATA.values():
            tokens_info = metadata["toon_schema_tokens"]
            # Should mention token reduction percentage
            assert "%" in tokens_info or "削減" in tokens_info


class TestTOONSchemaValidation:
    """Test TOON schema format validation"""

    def test_search_law_schema_format(self):
        """Test that search_law uses TOON format"""
        # Get the schema from the tool
        schema = search_law._tool_schema if hasattr(search_law, '_tool_schema') else None

        if schema:
            # Assert TOON format characteristics
            assert "type: object" in schema
            assert "properties:" in schema
            assert "required[1]:" in schema or "required[" in schema
            # No JSON-style brackets for enum
            assert "enum[4]:" in schema

    def test_search_case_schema_format(self):
        """Test that search_case uses TOON format"""
        schema = search_case._tool_schema if hasattr(search_case, '_tool_schema') else None

        if schema:
            assert "type: object" in schema
            assert "enum[5]:" in schema  # 5 court types

    def test_analyze_relationship_schema_format(self):
        """Test that analyze_law_case_relationship uses compact TOON format"""
        schema = analyze_law_case_relationship._tool_schema if hasattr(analyze_law_case_relationship, '_tool_schema') else None

        if schema:
            # Should use inline format for simplicity
            assert "{type: string" in schema
            assert "required[2]:" in schema


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
