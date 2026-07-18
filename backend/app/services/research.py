import uuid
import math
import io
import csv
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from app.repositories.research import ResearchRepository

class ResearchService:
    """
    Core service coordinating the governance intelligence, benchmarking, and algorithm simulations.
    """
    def __init__(self, repo: ResearchRepository) -> None:
        self.repo = repo

    # --- 1. Governance Score Engine ---
    def calculate_governance_score(self, inputs: Dict[str, float]) -> Dict[str, Any]:
        """
        Generates overall governance rating (0-100) and grade (A-F) based on weighted inputs.
        """
        weights = {
            "trust_score": 0.15,
            "policy_compliance": 0.15,
            "explainability_score": 0.10,
            "model_health": 0.10,
            "agent_health": 0.10,
            "drift_score": 0.10,
            "security_score": 0.10,
            "recovery_score": 0.08,
            "incident_frequency": 0.06,  # Negative impact
            "human_review_rate": 0.06    # Medium Review Rate is positive, High is negative. We map normalized val.
        }

        # Validate and bound inputs to [0, 100]
        bounded = {}
        for key in weights.keys():
            val = float(inputs.get(key, 80.0))
            bounded[key] = max(0.0, min(100.0, val))

        # Invert negative indicators
        incident_impact = 100.0 - bounded["incident_frequency"]
        
        # Human review rate sweet spot is ~15% (85% normalized score). If 0% or 100%, it decreases.
        review_rate = bounded["human_review_rate"]
        review_score = 100.0 - abs(review_rate - 15.0) * 2.0
        review_score = max(0.0, review_score)

        score_sum = (
            bounded["trust_score"] * weights["trust_score"] +
            bounded["policy_compliance"] * weights["policy_compliance"] +
            bounded["explainability_score"] * weights["explainability_score"] +
            bounded["model_health"] * weights["model_health"] +
            bounded["agent_health"] * weights["agent_health"] +
            bounded["drift_score"] * weights["drift_score"] +
            bounded["security_score"] * weights["security_score"] +
            bounded["recovery_score"] * weights["recovery_score"] +
            incident_impact * weights["incident_frequency"] +
            review_score * weights["human_review_rate"]
        )

        overall = round(max(0.0, min(100.0, score_sum)), 2)

        # Map Grade
        if overall >= 90.0:
            grade = "A"
        elif overall >= 80.0:
            grade = "B"
        elif overall >= 70.0:
            grade = "C"
        elif overall >= 60.0:
            grade = "D"
        else:
            grade = "F"

        return {
            "overall_score": overall,
            "grade": grade,
            "trust_score": bounded["trust_score"],
            "policy_compliance": bounded["policy_compliance"],
            "explainability_score": bounded["explainability_score"],
            "model_health": bounded["model_health"],
            "agent_health": bounded["agent_health"],
            "drift_score": bounded["drift_score"],
            "security_score": bounded["security_score"],
            "recovery_score": bounded["recovery_score"],
            "incident_frequency": bounded["incident_frequency"],
            "human_review_rate": bounded["human_review_rate"]
        }

    async def get_governance_report(self) -> Dict[str, Any]:
        latest = await self.repo.get_latest_governance_score()
        history = await self.repo.get_governance_history(limit=10)

        # Baseline defaults if empty
        if not latest:
            default_inputs = {
                "trust_score": 88.0,
                "policy_compliance": 95.0,
                "explainability_score": 90.0,
                "model_health": 92.0,
                "agent_health": 100.0,
                "drift_score": 96.0,
                "security_score": 98.0,
                "recovery_score": 90.0,
                "incident_frequency": 2.0,
                "human_review_rate": 12.0
            }
            res = self.calculate_governance_score(default_inputs)
            latest = await self.repo.save_governance_score(res)

        # Calculate trend slope
        trend_direction = "stable"
        if len(history) > 1:
            diff = history[0].score - history[-1].score
            if diff > 1.0:
                trend_direction = "improving"
            elif diff < -1.0:
                trend_direction = "declining"

        return {
            "score": latest.overall_score,
            "grade": latest.grade,
            "metrics": {
                "trust_score": latest.trust_score,
                "policy_compliance": latest.policy_compliance,
                "explainability_score": latest.explainability_score,
                "model_health": latest.model_health,
                "agent_health": latest.agent_health,
                "drift_score": latest.drift_score,
                "security_score": latest.security_score,
                "recovery_score": latest.recovery_score,
                "incident_frequency": latest.incident_frequency,
                "human_review_rate": latest.human_review_rate
            },
            "trend": trend_direction,
            "evaluated_at": latest.created_at
        }

    # --- 2. Agent Reputation Engine ---
    async def update_agent_reputation(self, agent_name: str, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dynamically updates reputation score based on accuracy, false rates, overrides, and health.
        """
        accuracy = float(telemetry.get("accuracy", 1.0))
        avg_confidence = float(telemetry.get("avg_confidence", 0.90))
        latency = float(telemetry.get("latency_ms", 15.0))
        
        success = int(telemetry.get("success_count", 100))
        failures = int(telemetry.get("failure_count", 0))
        false_pos = int(telemetry.get("false_positives", 0))
        false_neg = int(telemetry.get("false_negatives", 0))
        overrides = int(telemetry.get("human_overrides", 0))
        violations = int(telemetry.get("policy_violations", 0))
        drift_events = int(telemetry.get("drift_events", 0))
        recovery_success = int(telemetry.get("recovery_success", 0))

        # Base calculation: start at 100, apply deductibles
        rep_score = 100.0
        
        # Accuracy deduction (0 to 30 points)
        rep_score -= (1.0 - accuracy) * 100.0 * 0.30
        
        # Incomplete confidence penalty (0 to 10 points)
        rep_score -= (1.0 - avg_confidence) * 10.0
        
        # Operational deductibles
        rep_score -= failures * 5.0
        rep_score -= false_pos * 2.0
        rep_score -= false_neg * 4.0
        rep_score -= overrides * 3.0
        rep_score -= violations * 5.0
        rep_score -= drift_events * 3.0
        
        # Recovery bonus (restores up to 5 points)
        rep_score += min(5.0, recovery_success * 2.0)
        
        final_score = round(max(0.0, min(100.0, rep_score)), 2)

        payload = {
            "agent_name": agent_name,
            "score": final_score,
            "accuracy": accuracy,
            "avg_confidence": avg_confidence,
            "latency_ms": latency,
            "success_count": success,
            "failure_count": failures,
            "false_positives": false_pos,
            "false_negatives": false_neg,
            "human_overrides": overrides,
            "policy_violations": violations,
            "drift_events": drift_events,
            "recovery_success": recovery_success
        }

        await self.repo.save_agent_reputation(payload)
        return payload

    async def get_reputation_leaderboard(self) -> List[Dict[str, Any]]:
        agents = await self.repo.list_agent_reputations()
        
        # Default seeding if empty
        if not agents:
            default_agents = [
                ("fraud-agent", 92.5, 0.94, 0.90, 42.5),
                ("aml-agent", 88.0, 0.89, 0.85, 58.2),
                ("kyc-agent", 96.4, 0.98, 0.95, 15.1),
                ("device-agent", 95.0, 0.96, 0.92, 8.4),
                ("explainability-agent", 94.2, 0.95, 0.94, 115.0)
            ]
            for name, score, acc, conf, lat in default_agents:
                await self.update_agent_reputation(name, {
                    "accuracy": acc,
                    "avg_confidence": conf,
                    "latency_ms": lat,
                    "success_count": 500,
                    "failure_count": 2,
                    "false_positives": 4,
                    "false_negatives": 1,
                    "human_overrides": 3,
                    "policy_violations": 0,
                    "drift_events": 1,
                    "recovery_success": 1
                })
            agents = await self.repo.list_agent_reputations()

        leaderboard = []
        for i, a in enumerate(agents):
            leaderboard.append({
                "rank": i + 1,
                "agent_name": a.agent_name,
                "reputation_score": a.score,
                "accuracy": a.accuracy,
                "avg_confidence": a.avg_confidence,
                "latency_ms": a.latency_ms,
                "incidents": a.failure_count + a.policy_violations,
                "drift_events": a.drift_events
            })
        return leaderboard

    # --- 3. Governance Maturity Index ---
    async def get_maturity_assessment(self) -> Dict[str, Any]:
        latest = await self.repo.get_latest_maturity_assessment()
        if not latest:
            # Baseline assessment mapping
            scores = {
                "Monitoring": 82.0,
                "Security": 90.0,
                "Compliance": 88.0,
                "Observability": 85.0,
                "Explainability": 80.0,
                "Automation": 75.0,
                "Recovery": 82.0,
                "Policy Coverage": 90.0,
                "Human Oversight": 85.0
            }
            avg = sum(scores.values()) / len(scores)
            
            if avg >= 90.0:
                level = "Optimized"
            elif avg >= 80.0:
                level = "Quantitatively Managed"
            elif avg >= 70.0:
                level = "Defined"
            elif avg >= 60.0:
                level = "Managed"
            else:
                level = "Initial"

            latest = await self.repo.save_maturity_assessment({
                "maturity_level": level,
                "scores": scores,
                "recommendations": [
                    "Increase explainability telemetry coverage on older custom models.",
                    "Enhance self-healing automated actions for database connection recovery locks.",
                    "Review threshold drift profiles for transaction aml rules weekly."
                ]
            })

        return {
            "level": latest.maturity_level,
            "scores": latest.scores,
            "recommendations": latest.recommendations,
            "assessed_at": latest.created_at
        }

    # --- 4. AI Failure Index ---
    async def get_failure_index_report(self) -> Dict[str, Any]:
        latest = await self.repo.get_latest_failure_index()
        if not latest:
            # Seed default failure index
            index_val = 14.5 # low danger rating
            latest = await self.repo.save_failure_index({
                "failure_index": index_val,
                "severity": "low",
                "model_failures": 1,
                "infra_failures": 0,
                "policy_violations": 2,
                "agent_failures": 1,
                "consensus_failures": 0,
                "recovery_failures": 0,
                "drift_events": 1,
                "security_events": 0,
                "root_cause_summary": "Minor drift identified on the Fraud RFClassifier, model rolled back and re-indexed successfully."
            })

        return {
            "failure_index": latest.failure_index,
            "severity": latest.severity,
            "breakdown": {
                "model_failures": latest.model_failures,
                "infra_failures": latest.infra_failures,
                "policy_violations": latest.policy_violations,
                "agent_failures": latest.agent_failures,
                "consensus_failures": latest.consensus_failures,
                "recovery_failures": latest.recovery_failures,
                "drift_events": latest.drift_events,
                "security_events": latest.security_events
            },
            "summary": latest.root_cause_summary,
            "recorded_at": latest.created_at
        }

    # --- 5. Dynamic Consensus V2 Engine ---
    async def simulate_consensus_v2(self, agent_votes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Upgraded voting simulation weighting inputs dynamically based on active agent reputations.
        """
        # Load repetitions mapping
        reps = {a.agent_name: a.score for a in await self.repo.list_agent_reputations()}

        weighted_votes = []
        total_weight = 0.0
        approval_weighted_sum = 0.0
        confidence_matrix = {}

        for vote in agent_votes:
            name = vote["agent_name"]
            decision = vote["decision"] # approve or decline
            confidence = float(vote.get("confidence", 0.90))
            is_healthy = bool(vote.get("is_healthy", True))
            has_drift = bool(vote.get("has_drift", False))

            # Base reputation weight (defaults to 85.0 if not seeded)
            base_rep = reps.get(name, 85.0)
            
            # Formulate dynamic weights
            weight = base_rep / 100.0
            if not is_healthy:
                weight *= 0.20 # Severe penalty for degradation
            if has_drift:
                weight *= 0.60 # Penalty for model drift
            
            # Apply current prediction confidence
            weight *= confidence

            total_weight += weight
            vote_val = 1.0 if decision == "approve" else 0.0
            approval_weighted_sum += vote_val * weight

            confidence_matrix[name] = {
                "decision": decision,
                "confidence": confidence,
                "reputation_applied": base_rep,
                "effective_weight": round(weight, 3)
            }

            weighted_votes.append({
                "agent_name": name,
                "decision": decision,
                "weight": round(weight, 3)
            })

        consensus_confidence = 1.0
        if total_weight > 0.0:
            consensus_confidence = float(approval_weighted_sum / total_weight)

        # Decision Stability is mapping variance of votes
        decision_stability = float(1.0 - abs(consensus_confidence - 0.5) * 2.0)
        # Invert so 1.0 means strong unanimity (either 100% approve or 100% decline)
        decision_stability = round(1.0 - decision_stability, 3)

        verdict = "approve" if consensus_confidence >= 0.50 else "decline"

        return {
            "verdict": verdict,
            "consensus_confidence": round(consensus_confidence, 4),
            "decision_stability": decision_stability,
            "weighted_votes": weighted_votes,
            "confidence_matrix": confidence_matrix
        }

    # --- 6. Benchmark Engine ---
    async def get_benchmarks_report(self) -> List[Dict[str, Any]]:
        results = await self.repo.list_benchmarks()
        
        # Default seeding if empty
        if not results:
            run = await self.repo.create_run(uuid.uuid4(), {"env": "benchmarking"})
            
            benchmark_seeds = [
                ("FraudRFClassifier_v1", "fraud", 0.95, 0.94, 0.96, 0.95, 0.97, 12.4, 4500.0, 1.2, 45.0, 12.0),
                ("FraudGBCClassifier_v2", "fraud", 0.96, 0.95, 0.97, 0.96, 0.98, 18.2, 3200.0, 2.4, 85.0, 18.0),
                ("AmlNetworkGraph_v1", "aml", 0.92, 0.90, 0.93, 0.91, 0.94, 48.5, 800.0, 8.5, 250.0, 120.0),
                ("ConsensusV1_Simple", "consensus", 0.94, 0.92, 0.95, 0.93, 0.95, 1.5, 25000.0, 0.1, 5.0, 0.5),
                ("ConsensusV2_ReputationWeighted", "consensus", 0.97, 0.96, 0.98, 0.97, 0.99, 2.8, 18000.0, 0.2, 8.0, 1.2)
            ]
            
            for name, type_, acc, prec, rec, f1, auc, lat, tps, cpu, mem, rec_t in benchmark_seeds:
                await self.repo.create_benchmark_result(run.id, name, type_, {
                    "accuracy": acc,
                    "precision": prec,
                    "recall": rec,
                    "f1_score": f1,
                    "roc_auc": auc,
                    "latency_ms": lat,
                    "throughput": tps,
                    "cpu_usage": cpu,
                    "memory_usage": mem,
                    "recovery_time_ms": rec_t
                })
            results = await self.repo.list_benchmarks()

        report = []
        for r in results:
            report.append({
                "algorithm_name": r.algorithm_name,
                "algorithm_type": r.algorithm_type,
                "accuracy": r.accuracy,
                "precision": r.precision,
                "recall": r.recall,
                "f1_score": r.f1_score,
                "roc_auc": r.roc_auc,
                "latency_ms": r.latency_ms,
                "throughput": r.throughput,
                "cpu_usage": r.cpu_usage,
                "memory_usage": r.memory_usage,
                "recovery_time_ms": r.recovery_time_ms,
                "created_at": r.created_at
            })
        return report

    # --- 7. Report Compilation & Exports ---
    async def export_report_csv(self, metrics_data: List[Dict[str, Any]]) -> str:
        """
        Compiles research benchmark metrics into a downloadable CSV string.
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow([
            "Algorithm Name", "Type", "Accuracy", "Precision", 
            "Recall", "F1 Score", "ROC-AUC", "Latency (ms)", 
            "Throughput (TPS)", "CPU (%)", "Memory (MB)"
        ])
        
        for row in metrics_data:
            writer.writerow([
                row.get("algorithm_name"),
                row.get("algorithm_type"),
                row.get("accuracy"),
                row.get("precision"),
                row.get("recall"),
                row.get("f1_score"),
                row.get("roc_auc"),
                row.get("latency_ms"),
                row.get("throughput"),
                row.get("cpu_usage"),
                row.get("memory_usage")
            ])
            
        return output.getvalue()

    async def export_report_json(self, data: Dict[str, Any]) -> str:
        """
        Compiles JSON executive reports formatted with pretty print indent.
        """
        return json.dumps(data, indent=2, default=str)
