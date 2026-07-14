import time 
from typing import Optional
from pydantic import BaseModel, Field

class BenchMarkMetrics(BaseModel):
    model_name: str
    prompt_id: str
    total_duration_ms: float = Field(..., description="Total round-trip API time")
    ttft_ms: float = Field(...,description="Generation throughput rate")
    token_count: int
    response_text: str
    schema_valid: bool = False

def calculate_throughput(token_count: int, duration_seconds: float) -> float:
    """Calculates tokens generated per second accurately"""
    if duration_seconds <= 0:
        return 0.0
    return float(token_count / duration_seconds)