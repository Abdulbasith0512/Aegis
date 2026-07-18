import time
import os
import sys
import psutil
import statistics
from typing import Dict, Any, List
from app.services.intelligence import IntelligenceService
from app.services.research import ResearchService

class MockRepo:
    async def get_latest_governance_score(self): return None
    async def get_governance_history(self, limit): return []
    async def save_governance_score(self, d): return None
    async def list_agent_reputations(self): return []
    async def save_agent_reputation(self, d): return None
    async def get_latest_maturity_report(self): return None
    async def save_maturity_report(self, d): return None
    async def get_latest_failure_index(self): return None
    async def save_failure_index(self, d): return None
    async def list_benchmark_results(self): return []
    async def create_benchmark_run(self, *args): return None
    async def create_benchmark_result(self, *args): pass
    async def create_governance_report(self, *args, **kwargs): return None
    async def list_governance_reports(self, limit): return []

def run_performance_benchmarks() -> None:
    print("==================================================")
    print("AEGISAI CORE SYSTEM PERFORMANCE BENCHMARK RUNNER")
    print("==================================================")
    
    process = psutil.Process(os.getpid())
    start_memory = process.memory_info().rss / (1024 * 1024) # MB
    
    # 1. Initialize services
    repo = MockRepo()
    int_service = IntelligenceService(repo)
    res_service = ResearchService(repo)

    # 2. Benchmark Governance Score Calculation
    print("\n[1/3] Benchmarking Governance Score Calculations (1,000 runs)...")
    telemetry = {
        "trust_score": 92.5, "policy_compliance": 96.0, "model_health": 90.0,
        "agent_health": 100.0, "explainability_quality": 88.0, "recovery_success": 90.0,
        "security_status": 98.0, "drift_score": 96.0, "incident_rate": 2.0,
        "human_review_rate": 85.0, "consensus_stability": 92.0
    }
    
    calc_times = []
    for _ in range(1000):
        t_start = time.perf_counter_ns()
        int_service.calculate_governance_score(telemetry)
        t_end = time.perf_counter_ns()
        calc_times.append((t_end - t_start) / 1_000_000.0) # convert to ms
        
    p50_calc = statistics.median(calc_times)
    p95_calc = statistics.quantiles(calc_times, n=20)[18] # 95th percentile
    p99_calc = statistics.quantiles(calc_times, n=100)[98] # 99th percentile

    # 3. Benchmark Dynamic Consensus V2 calculation
    print("[2/3] Benchmarking Dynamic Consensus V2 (1,000 runs)...")
    agent_votes = [
        {"agent_name": "fraud-agent", "decision": "approve", "confidence": 0.95, "is_healthy": True, "has_drift": False},
        {"agent_name": "kyc-agent", "decision": "approve", "confidence": 0.90, "is_healthy": True, "has_drift": False},
        {"agent_name": "device-agent", "decision": "decline", "confidence": 0.40, "is_healthy": True, "has_drift": False},
        {"agent_name": "aml-agent", "decision": "approve", "confidence": 0.98, "is_healthy": True, "has_drift": False},
        {"agent_name": "explainability-agent", "decision": "approve", "confidence": 0.92, "is_healthy": True, "has_drift": False}
    ]

    # Warmup async loop
    import asyncio
    consensus_times = []
    
    async def run_consensus():
        for _ in range(1000):
            t_start = time.perf_counter_ns()
            await res_service.simulate_consensus_v2(agent_votes)
            t_end = time.perf_counter_ns()
            consensus_times.append((t_end - t_start) / 1_000_000.0)

    asyncio.run(run_consensus())
    p50_cons = statistics.median(consensus_times)
    p95_cons = statistics.quantiles(consensus_times, n=20)[18]
    p99_cons = statistics.quantiles(consensus_times, n=100)[98]

    # 4. Memory and System audit
    end_memory = process.memory_info().rss / (1024 * 1024)
    cpu_percent = psutil.cpu_percent(interval=0.5)

    print("[3/3] Saving Benchmark Performance Summary Report...")

    report_lines = [
        "==================================================",
        "          AEGISAI PERFORMANCE BENCHMARK REPORT    ",
        "==================================================",
        f"Execution Timestamp : {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"OS Platform         : {sys.platform}",
        f"Python Version      : {sys.version.split()[0]}",
        "",
        "--------------------------------------------------",
        "1. Governance Score Calculations Engine Latency",
        "--------------------------------------------------",
        f"Iterations          : 1,000",
        f"Median Latency (p50): {p50_calc:.4f} ms",
        f"95th Percentile     : {p95_calc:.4f} ms",
        f"99th Percentile     : {p99_calc:.4f} ms",
        f"Throughput          : {int(1000.0 / (sum(calc_times) / 1000.0)):,} Calc/Sec",
        "",
        "--------------------------------------------------",
        "2. Dynamic Consensus V2 Engine Latency",
        "--------------------------------------------------",
        f"Iterations          : 1,000",
        f"Median Latency (p50): {p50_cons:.4f} ms",
        f"95th Percentile     : {p95_cons:.4f} ms",
        f"99th Percentile     : {p99_cons:.4f} ms",
        "",
        "--------------------------------------------------",
        "3. System Hardware Parameters",
        "--------------------------------------------------",
        f"Baseline Memory     : {start_memory:.2f} MB",
        f"Active Memory       : {end_memory:.2f} MB",
        f"Memory Increment    : {end_memory - start_memory:.2f} MB",
        f"CPU Utilization     : {cpu_percent:.1f}%",
        "=================================================="
    ]

    report_content = "\n".join(report_lines)
    print(report_content)

    # Save to file
    report_path = os.path.join(os.path.dirname(__file__), "benchmark_report.txt")
    with open(report_path, "w") as f:
        f.write(report_content)
    print(f"\n[Success] Benchmark report written to: {report_path}")

if __name__ == "__main__":
    run_performance_benchmarks()
