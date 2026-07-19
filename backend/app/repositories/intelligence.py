import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.research import (
    GovernanceScore, GovernanceHistory, AgentReputation, ReputationHistory,
    BenchmarkRun, BenchmarkResult, GovernanceReport, FailureIndex, MaturityReport,
    ResearchProject, ResearchExperiment, ExperimentRun
)

class IntelligenceRepository:
    """
    Data tier operations repository managing all AegisAI Intelligence Platform entities.
    """
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # --- Governance Scores ---
    async def get_latest_governance_score(self) -> Optional[GovernanceScore]:
        result = await self.db.execute(
            select(GovernanceScore).order_by(desc(GovernanceScore.created_at)).limit(1)
        )
        return result.scalars().first()

    async def get_governance_history(self, limit: int = 30) -> List[GovernanceHistory]:
        result = await self.db.execute(
            select(GovernanceHistory).order_by(desc(GovernanceHistory.timestamp)).limit(limit)
        )
        return list(result.scalars().all())

    async def save_governance_score(self, score_data: Dict[str, Any]) -> GovernanceScore:
        score = GovernanceScore(
            id=uuid.uuid4(),
            overall_score=score_data["overall_score"],
            grade=score_data["grade"],
            trust_score=score_data.get("trust_score", 0.0),
            policy_compliance=score_data.get("policy_compliance", 0.0),
            explainability_score=score_data.get("explainability_score", 0.0),
            model_health=score_data.get("model_health", 0.0),
            agent_health=score_data.get("agent_health", 0.0),
            drift_score=score_data.get("drift_score", 0.0),
            security_score=score_data.get("security_score", 0.0),
            recovery_score=score_data.get("recovery_score", 0.0),
            incident_frequency=score_data.get("incident_frequency", 0.0),
            human_review_rate=score_data.get("human_review_rate", 0.0),
            created_at=datetime.utcnow()
        )
        self.db.add(score)
        
        hist = GovernanceHistory(
            id=uuid.uuid4(),
            timestamp=datetime.utcnow(),
            score=score_data["overall_score"],
            metrics_snapshot=score_data
        )
        self.db.add(hist)
        
        await self.db.commit()
        await self.db.refresh(score)
        return score

    # --- Agent Reputation ---
    async def get_agent_reputation(self, agent_name: str) -> Optional[AgentReputation]:
        result = await self.db.execute(
            select(AgentReputation).where(AgentReputation.agent_name == agent_name)
        )
        return result.scalars().first()

    async def list_agent_reputations(self) -> List[AgentReputation]:
        result = await self.db.execute(
            select(AgentReputation).order_by(desc(AgentReputation.score))
        )
        return list(result.scalars().all())

    async def save_agent_reputation(self, rep_data: Dict[str, Any]) -> AgentReputation:
        agent_name = rep_data["agent_name"]
        rep = await self.get_agent_reputation(agent_name)
        if not rep:
            rep = AgentReputation(id=uuid.uuid4(), agent_name=agent_name)
            self.db.add(rep)

        for key, val in rep_data.items():
            if key == "avg_latency_ms":
                rep.latency_ms = val
            elif key == "model_drift":
                rep.drift_events = int(val * 100)
            elif hasattr(rep, key):
                setattr(rep, key, val)
        rep.last_updated = datetime.utcnow()

        hist = ReputationHistory(
            id=uuid.uuid4(),
            agent_name=agent_name,
            score=rep_data["score"],
            recorded_at=datetime.utcnow()
        )
        self.db.add(hist)
        
        await self.db.commit()
        await self.db.refresh(rep)
        return rep

    # --- Benchmarking ---
    async def create_benchmark_run(self, parameters: Dict[str, Any]) -> BenchmarkRun:
        # 1. Ensure default project exists
        project_name = "Platform Benchmarks Project"
        res_p = await self.db.execute(select(ResearchProject).where(ResearchProject.name == project_name))
        project = res_p.scalars().first()
        if not project:
            project = ResearchProject(
                id=uuid.uuid4(),
                name=project_name,
                description="Auto-generated project for platform benchmarks"
            )
            self.db.add(project)
            await self.db.commit()
            await self.db.refresh(project)

        # 2. Ensure default experiment exists
        experiment_name = "Platform Algorithms Evaluation"
        res_e = await self.db.execute(select(ResearchExperiment).where(ResearchExperiment.name == experiment_name))
        experiment = res_e.scalars().first()
        if not experiment:
            experiment = ResearchExperiment(
                id=uuid.uuid4(),
                project_id=project.id,
                name=experiment_name,
                description="Auto-generated experiment for platform benchmarks",
                config_data={}
            )
            self.db.add(experiment)
            await self.db.commit()
            await self.db.refresh(experiment)

        # 3. Create run ID
        run_id = uuid.uuid4()

        # 4. Create matching ExperimentRun
        exp_run = ExperimentRun(
            id=run_id,
            experiment_id=experiment.id,
            status="completed",
            parameters=parameters,
            metrics={}
        )
        self.db.add(exp_run)

        # 5. Create BenchmarkRun
        run = BenchmarkRun(
            id=run_id,
            status="pending",
            parameters=parameters,
            metrics={},
            started_at=datetime.utcnow()
        )
        self.db.add(run)

        await self.db.commit()
        await self.db.refresh(run)
        return run

    async def get_benchmark_run(self, run_id: uuid.UUID) -> Optional[BenchmarkRun]:
        result = await self.db.execute(
            select(BenchmarkRun).where(BenchmarkRun.id == run_id)
        )
        return result.scalars().first()

    async def update_benchmark_run(self, run_id: uuid.UUID, status: str, metrics: Dict[str, Any]) -> Optional[BenchmarkRun]:
        run = await self.get_benchmark_run(run_id)
        if not run:
            return None
        run.status = status
        run.metrics = metrics
        run.completed_at = datetime.utcnow()
        self.db.add(run)
        await self.db.commit()
        await self.db.refresh(run)
        return run

    async def create_benchmark_result(self, run_id: uuid.UUID, result_data: Dict[str, Any]) -> BenchmarkResult:
        res = BenchmarkResult(
            id=uuid.uuid4(),
            run_id=run_id,
            algorithm_name=result_data["algorithm_name"],
            algorithm_type=result_data["algorithm_type"],
            accuracy=result_data.get("accuracy", 0.0),
            precision=result_data.get("precision", 0.0),
            recall=result_data.get("recall", 0.0),
            f1_score=result_data.get("f1_score", 0.0),
            roc_auc=result_data.get("roc_auc", 0.0),
            latency_ms=result_data.get("latency_ms", 0.0),
            throughput=result_data.get("throughput", 0.0),
            cpu_usage=result_data.get("cpu_usage", 0.0),
            memory_usage=result_data.get("memory_usage", 0.0),
            recovery_time_ms=result_data.get("recovery_time_ms", 0.0),
            created_at=datetime.utcnow()
        )
        self.db.add(res)
        await self.db.commit()
        await self.db.refresh(res)
        return res

    async def list_benchmark_results(self, limit: int = 50) -> List[BenchmarkResult]:
        result = await self.db.execute(
            select(BenchmarkResult).order_by(desc(BenchmarkResult.created_at)).limit(limit)
        )
        return list(result.scalars().all())

    # --- Governance Reports ---
    async def create_governance_report(self, type_: str, format_: str, summary: str, details: Dict[str, Any]) -> GovernanceReport:
        rep = GovernanceReport(
            id=uuid.uuid4(),
            report_type=type_,
            report_format=format_,
            summary=summary,
            details=details,
            created_at=datetime.utcnow()
        )
        self.db.add(rep)
        await self.db.commit()
        await self.db.refresh(rep)
        return rep

    async def list_governance_reports(self, limit: int = 50) -> List[GovernanceReport]:
        result = await self.db.execute(
            select(GovernanceReport).order_by(desc(GovernanceReport.created_at)).limit(limit)
        )
        return list(result.scalars().all())

    # --- Maturity Assess ---
    async def get_latest_maturity_report(self) -> Optional[MaturityReport]:
        result = await self.db.execute(
            select(MaturityReport).order_by(desc(MaturityReport.created_at)).limit(1)
        )
        return result.scalars().first()

    async def save_maturity_report(self, mat_data: Dict[str, Any]) -> MaturityReport:
        rep = MaturityReport(
            id=uuid.uuid4(),
            maturity_level=mat_data["maturity_level"],
            scores=mat_data["scores"],
            recommendations=mat_data["recommendations"],
            created_at=datetime.utcnow()
        )
        self.db.add(rep)
        await self.db.commit()
        await self.db.refresh(rep)
        return rep

    # --- Failure Index ---
    async def get_latest_failure_index(self) -> Optional[FailureIndex]:
        result = await self.db.execute(
            select(FailureIndex).order_by(desc(FailureIndex.created_at)).limit(1)
        )
        return result.scalars().first()

    async def save_failure_index(self, index_data: Dict[str, Any]) -> FailureIndex:
        fi = FailureIndex(
            id=uuid.uuid4(),
            failure_index=index_data["failure_index"],
            severity=index_data["severity"],
            model_failures=index_data.get("model_failures", 0),
            infra_failures=index_data.get("infra_failures", 0),
            policy_violations=index_data.get("policy_violations", 0),
            agent_failures=index_data.get("agent_failures", 0),
            consensus_failures=index_data.get("consensus_failures", 0),
            recovery_failures=index_data.get("recovery_failures", 0),
            drift_events=index_data.get("drift_events", 0),
            security_events=index_data.get("security_events", 0),
            root_cause_summary=index_data.get("root_cause_summary", ""),
            created_at=datetime.utcnow()
        )
        self.db.add(fi)
        await self.db.commit()
        await self.db.refresh(fi)
        return fi
