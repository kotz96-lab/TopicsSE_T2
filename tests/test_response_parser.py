"""Infrastructure tests for parsing structured LLM responses."""

from src.parsing.response_parser import parse


class TestParseCleanJson:
    def test_bare_json_object_parses_all_fields(self) -> None:
        text = (
            '{"top_1_line": 12, "top_3_lines": [12, 14, 9], '
            '"faulty_region": "loop condition", "explanation": "off by one"}'
        )
        result = parse(text)
        assert result.is_valid
        assert result.top_1_line == 12
        assert result.top_3_lines == [12, 14, 9]
        assert result.faulty_region == "loop condition"
        assert result.explanation == "off by one"

    def test_json_wrapped_in_fenced_code_block_is_extracted(self) -> None:
        text = 'Here is my analysis:\n```json\n{"top_1_line": 4, "top_3_lines": [4, 5, 6], "faulty_region": "x", "explanation": "y"}\n```\nDone.'
        result = parse(text)
        assert result.is_valid
        assert result.top_1_line == 4


class TestParseHandlesModelSlop:
    def test_prose_around_json_is_stripped(self) -> None:
        text = 'Sure, here you go: {"top_1_line": 7, "top_3_lines": [7, 8, 9], "faulty_region": "return", "explanation": "wrong"} that\'s my answer.'
        result = parse(text)
        assert result.is_valid
        assert result.top_1_line == 7

    def test_top_1_as_string_is_coerced_to_int(self) -> None:
        text = '{"top_1_line": "12", "top_3_lines": ["12", "14"], "faulty_region": "", "explanation": ""}'
        result = parse(text)
        assert result.is_valid
        assert result.top_1_line == 12
        assert result.top_3_lines == [12, 14]


class TestParseInvalidResponses:
    def test_no_json_at_all_is_invalid(self) -> None:
        text = "I cannot answer that."
        result = parse(text)
        assert not result.is_valid
        assert "no JSON" in result.parse_error

    def test_missing_top_1_line_is_invalid(self) -> None:
        text = '{"top_3_lines": [1, 2, 3], "faulty_region": "x", "explanation": "y"}'
        result = parse(text)
        assert not result.is_valid

    def test_top_1_as_boolean_is_invalid(self) -> None:
        # Guards against `True` being coerced to 1 via int(True)
        text = '{"top_1_line": true, "top_3_lines": [], "faulty_region": "", "explanation": ""}'
        result = parse(text)
        assert not result.is_valid

    def test_malformed_json_is_invalid(self) -> None:
        # Object braces are balanced but contents are not valid JSON.
        text = '{"top_1_line": 12, "top_3_lines": [12,,]}'
        result = parse(text)
        assert not result.is_valid
        assert "json decode error" in result.parse_error
