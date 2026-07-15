import os
import yaml
import asyncio
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.profiler.engine import AsyncLLMProfiler, BenchmarkMetrics
from src.evaluator.parser import ResponseValidator

console = Console()

class BenchmarkOrchestrator:
    def __init__(self, config_path: str = "config/bench_config.yaml"):
        """Loads benchmarking prompts and metric constraints from configuration configurations."""
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
            
        self.profiler = AsyncLLMProfiler()
        self.results = []

    async def execute_suite(self):
        """Orchestrates sequential iteration benchmarking sweeps across all targeted models."""
        models = self.config.get("test_models", [])
        prompts = self.config.get("prompts", [])
        iterations = self.config.get("benchmarking", {}).get("iterations", 3)

        console.print(Panel(f"[bold cyan]🤖 SLM/LLM Performance Benchmarking Agent[/]\nModels Loaded: {models}", border_style="cyan"))

        for model in models:
            for prompt_info in prompts:
                pid = prompt_info["id"]
                p_text = prompt_info["text"]
                schema = prompt_info["expected_schema"]

                console.print(f"\n🚀 Profiling [bold blue]{model}[/] on prompt profile '[bold yellow]{pid}[/]'...")
                
                # Execute evaluation loop across multiple iterations to accurately average latency
                for i in range(iterations):
                    metrics: BenchmarkMetrics = await self.profiler.profile_stream(
                        model_name=model, prompt_id=pid, prompt_text=p_text
                    )
                    
                    # Grade structural schema accuracy
                    metrics.schema_valid = ResponseValidator.validate_schema(metrics.response_text, schema)
                    self.results.append(metrics)
                    
                    console.print(
                        f"  ↳ Run {i+1}: Latency: [green]{metrics.total_duration_ms:.0f}ms[/] | "
                        f"TTFT: [green]{metrics.ttft_ms:.1f}ms[/] | "
                        f"Throughput: [green]{metrics.tokens_per_second:.1f} t/s[/] | "
                        f"Schema Valid: {'[green]True[/]' if metrics.schema_valid else '[red]False[/]'}"
                    )

        await self.profiler.close()
        self.render_summary_table()

    def render_summary_table(self):
        """Aggregates logged iteration records and prints a formatted analytical performance grid."""
        table = Table(title="📊 Final Benchmark Assessment Matrix", expand=True)
        table.add_column("Model Artifact", style="bold white")
        table.add_column("Prompt Task", style="cyan")
        table.add_column("Avg Latency", justify="right")
        table.add_column("Avg TTFT", justify="right")
        table.add_column("Avg Throughput", justify="right")
        table.add_column("Accuracy Score", justify="center")

        # Group data to process averaged outputs per categorical pairing
        pairs = set((r.model_name, r.prompt_id) for r in self.results)
        
        for model_name, prompt_id in sorted(pairs):
            subset = [r for r in self.results if r.model_name == model_name and r.prompt_id == prompt_id]
            
            avg_latency = sum(r.total_duration_ms for r in subset) / len(subset)
            avg_ttft = sum(r.ttft_ms for r in subset) / len(subset)
            avg_tps = sum(r.tokens_per_second for r in subset) / len(subset)
            
            correct_runs = sum(1 for r in subset if r.schema_valid)
            accuracy_percentage = (correct_runs / len(subset)) * 100

            table.add_row(
                model_name,
                prompt_id,
                f"{avg_latency:.0f} ms",
                f"{avg_ttft:.1f} ms",
                f"{avg_tps:.1f} t/s",
                f"[green]{accuracy_percentage:.0f}%[/]" if accuracy_percentage == 100 else f"[yellow]{accuracy_percentage:.0f}%[/]"
            )

        console.print("\n")
        console.print(table)

def main():
    orchestrator = BenchmarkOrchestrator()
    asyncio.run(orchestrator.execute_suite())

if __name__ == "__main__":
    main()
