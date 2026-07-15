import pytest
import asyncio
from src.profiler.engine import calculate_throughput, AsyncLLMProfiler, BenchmarkMetrics
from src.evaluator.parser import ResponseValidator

def test_throughput_calculation_math():
    """Validates throughput evaluation constraints under standard and zero division boundaries."""
    # Standard operational run calculation
    assert calculate_throughput(token_count=100, duration_seconds=2.0) == 50.0
    
    # Structural safety fallback check to ensure no math crashes occur on immediate execution
    assert calculate_throughput(token_count=50, duration_seconds=0.0) == 0.0
    assert calculate_throughput(token_count=50, duration_seconds=-0.5) == 0.0

def test_regex_json_extraction_intelligence():
    """Verifies the regex layer successfully sanitizes and parses structurally messy LLM outputs."""
    clean_json = '{"name": "Alice", "age": 30}'
    markdown_wrapped_json = '```json\n{"name": "Bob", "age": 25}\n```'
    conversational_json = 'Sure! Here is the data: {"name": "Charlie", "age": 40} Hope this helps!'
    completely_broken = 'The engineer is named John and he is 29 years old.'

    # Test extractions
    assert ResponseValidator.extract_json(clean_json) == {"name": "Alice", "age": 30}
    assert ResponseValidator.extract_json(markdown_wrapped_json) == {"name": "Bob", "age": 25}
    assert ResponseValidator.extract_json(conversational_json) == {"name": "Charlie", "age": 40}
    assert ResponseValidator.extract_json(completely_broken) is None

def test_schema_evaluation_grading_logic():
    """Validates that the verification rules correctly grade model accuracy against constraints."""
    valid_payload = '{"name": "David", "age": 35}'
    missing_fields_payload = '{"name": "Emma"}' # Fails schema because 'age' is missing

    assert ResponseValidator.validate_schema(valid_payload, "json") is True
    assert ResponseValidator.validate_schema(missing_fields_payload, "json") is False
    assert ResponseValidator.validate_schema("def my_func(): pass", "raw_text") is True

@pytest.mark.asyncio
async def test_profiler_resilient_fallback_loop():
    """Ensures the asynchronous client triggers its defensive mock sequence smoothly without crashing."""
    profiler = AsyncLLMProfiler(base_url="http://invalid-localhost-port:9999")
    
    try:
        metrics = await profiler.profile_stream(
            model_name="test-model", 
            prompt_id="json_extraction", 
            prompt_text="Test prompt."
        )
        
        # Ensure the fallback system yields a valid data layout object
        assert isinstance(metrics, BenchmarkMetrics)
        assert "MOCK" in metrics.model_name
        assert metrics.tokens_per_second > 0.0
        assert len(metrics.response_text) > 0
    finally:
        await profiler.close()
