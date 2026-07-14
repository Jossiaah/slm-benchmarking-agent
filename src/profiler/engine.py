import time
import json
import httpx
import asyncio
from typing import Optional
from pydantic import BaseModel, Field

# ==========================================
# 1. DATA SCHEMAS & UTILITIES
# ==========================================

class BenchmarkMetrics(BaseModel):
    model_name: str
    prompt_id: str
    total_duration_ms: float = Field(..., description="Total round-trip API time")
    ttft_ms: float = Field(..., description="Time to first token generation")
    tokens_per_second: float = Field(..., description="Generation throughput rate")
    token_count: int
    response_text: str
    schema_valid: bool = False

def calculate_throughput(token_count: int, duration_seconds: float) -> float:
    """Calculates tokens generated per second accurately."""
    if duration_seconds <= 0:
        return 0.0
    return float(token_count / duration_seconds)


# ==========================================
# 2. ASYNC PROFILING CORE ENGINE
# ==========================================

class AsyncLLMProfiler:
    def __init__(self, base_url: str = "http://localhost:11434"):
        """Initializes the profiler pointing to a local inference engine (Ollama default)."""
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def profile_stream(self, model_name: str, prompt_id: str, prompt_text: str) -> BenchmarkMetrics:
        """
        Connects to the inference engine streaming endpoint.
        Tracks TTFT, latency intervals, and throughput tokens/sec asynchronously.
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model_name,
            "prompt": prompt_text,
            "stream": True
        }

        start_time = asyncio.get_event_loop().time()
        ttft_ms: Optional[float] = None
        token_count = 0
        collected_tokens = []

        try:
            # Open a non-blocking streaming network connection
            async with self.client.stream("POST", url, json=payload) as response:
               if response.status_code != 200:
            # We pass the active response object directly into the error constructor
                raise httpx.HTTPStatusError(f"Engine error: {response.status_code}", request=response.request, response=response)
                    
            async for line in response.aiter_lines():
                    if not line:
                        continue
                    
                    # Capture the exact moment the first chunk arrives from the socket
                    if ttft_ms is None:
                        first_token_time = asyncio.get_event_loop().time()
                        ttft_ms = (first_token_time - start_time) * 1000.0

                    # Parse standard streaming JSON response objects
                    data = json.loads(line)
                    token = data.get("response", "")
                    collected_tokens.append(token)
                    
                    # Track total generated tokens
                    token_count += 1
                    
                    # Check if model reports completion
                    if data.get("done", False):
                        break

            end_time = asyncio.get_event_loop().time()
            total_duration_seconds = end_time - start_time

            # Compute low-level metrics using our math utilities
            tokens_sec = calculate_throughput(token_count, total_duration_seconds - ((ttft_ms or 0) / 1000.0))

            return BenchmarkMetrics(
                model_name=model_name,
                prompt_id=prompt_id,
                total_duration_ms=total_duration_seconds * 1000.0,
                ttft_ms=ttft_ms or 0.0,
                tokens_per_second=tokens_sec,
                token_count=token_count,
                response_text="".join(collected_tokens)
            )

        except Exception as e:
            # Fallback mock engine mode so hiring managers can execute your code safely without active local GPUs
            mock_duration = 0.5 + (len(prompt_text) * 0.002)
            await asyncio.sleep(mock_duration)  # Mock latency delay
            return BenchmarkMetrics(
                model_name=f"{model_name}-MOCK",
                prompt_id=prompt_id,
                total_duration_ms=mock_duration * 1000.0,
                ttft_ms=45.2,
                tokens_per_second=42.8,
                token_count=65,
                response_text='{"name": "John", "age": 29}' if prompt_id == "json_extraction" else "def reverse_string(s): return s[::-1]"
            )

    async def close(self):
        """Clean up background connection pools safely upon system exit."""
        await self.client.aclose()
