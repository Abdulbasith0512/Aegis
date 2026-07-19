import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, desc
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.research import (
    ResearchProject, ResearchExperiment, ExperimentRun, BenchmarkResult,
    GovernanceScore, GovernanceHistory, AgentReputation, ReputationHistory,
    FailureIndex, MaturityAssessment, AlgorithmVersion, ComparisonReport
)

class ResearchRepository:
    """
    Data tier operations repository managing all AI Research Lab entities and operations.
    """
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # --- Projects & Experiments ---
    async def create_project(self, name: str, description: Optional[str]) -> ResearchProject:
        project = ResearchProject(
            id=uuid.uuid4(),
            name=name,
            description=description,
            created_at=datetime.utcnow()
        )
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def get_project(self, project_id: uuid.UUID) -> Optional[ResearchProject]:
        result = await self.db.execute(
            select(ResearchProject)
            .where(ResearchProject.id == project_id)
            .options(selectinload(ResearchProject.experiments))
        )
        return result.scalars().first()

    async def get_or_create_default_project(self) -> ResearchProject:
        result = await self.db.execute(
            select(ResearchProject).where(ResearchProject.name == "Default Research Project")
        )
        project = result.scalars().first()
        if not project:
            project = await self.create_project(
                name="Default Research Project",
                description="Default namespace for AI governance experiments."
            )
        return project

    async def create_experiment(
        self,
        project_id: uuid.UUID,
        name: str,
        description: Optional[str],
        tags: Optional[List[str]],
        version_string: str,
        config_data: Dict[str, Any]
    ) -> ResearchExperiment:
        exp = ResearchExperiment(
            id=uuid.uuid4(),
            project_id=project_id,
            name=name,
            description=description,
            tags=tags,
            version_string=version_string,
            config_data=config_data,
            is_archived=False,
            created_at=datetime.utcnow()
        )
        self.db.add(exp)
        await self.db.commit()
        await self.db.refresh(exp)
        return exp

    async def list_experiments(self, include_archived: bool = False) -> List[ResearchExperiment]:
        stmt = select(ResearchExperiment)
        if not include_archived:
            stmt = stmt.where(ResearchExperiment.is_archived == False)
        stmt = stmt.order_by(desc(ResearchExperiment.created_at))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_experiment(self, experiment_id: uuid.UUID) -> Optional[ResearchExperiment]:
        result = await self.db.execute(
            select(ResearchExperiment)
            .where(ResearchExperiment.id == experiment_id)
            .options(selectinload(ResearchExperiment.runs))
        )
        return result.scalars().first()

    # --- Runs & Benchmarks ---
    async def create_run(
        self,
        experiment_id: uuid.UUID,
        parameters: Dict[str, Any]
    ) -> ExperimentRun:
        # Ensure default project exists
        project_name = "Default Research Project"
        res_p = await self.db.execute(select(ResearchProject).where(ResearchProject.name == project_name))
        project = res_p.scalars().first()
        if not project:
            project = ResearchProject(
                id=uuid.uuid4(),
                name=project_name,
                description="Auto-generated project for research runs"
            )
            self.db.add(project)
            await self.db.commit()
            await self.db.refresh(project)

        # Ensure experiment exists
        res_e = await self.db.execute(select(ResearchExperiment).where(ResearchExperiment.id == experiment_id))
        experiment = res_e.scalars().first()
        if not experiment:
            experiment = ResearchExperiment(
                id=experiment_id,
                project_id=project.id,
                name=f"Auto-generated Experiment ({experiment_id})",
                description="Auto-generated experiment to track runs",
                config_data={}
            )
            self.db.add(experiment)
            await self.db.commit()
            await self.db.refresh(experiment)

        run = ExperimentRun(
            id=uuid.uuid4(),
            experiment_id=experiment_id,
            status="pending",
            parameters=parameters,
            metrics={},
            started_at=datetime.utcnow()
        )
        self.db.add(run)
        await self.db.commit()
        await self.db.refresh(run)
        return run

    async def get_run(self, run_id: uuid.UUID) -> Optional[ExperimentRun]:
        result = await self.db.execute(
            select(ExperimentRun)
            .where(ExperimentRun.id == run_id)
            .options(selectinload(ExperimentRun.benchmark_results))
        )
        return result.scalars().first()

    async def list_runs(self, limit: int = 50) -> List[ExperimentRun]:
        result = await self.db.execute(
            select(ExperimentRun)
            .order_by(desc(ExperimentRun.started_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update_run_status(
        self,
        run_id: uuid.UUID,
        status: str,
        metrics: Optional[Dict[str, Any]] = None,
        completed: bool = False
    ) -> Optional[ExperimentRun]:
        run = await self.get_run(run_id)
        if not run:
            return None
        run.status = status
        if metrics is not None:
            run.metrics = metrics
        if completed:
            run.completed_at = datetime.utcnow()
        self.db.add(run)
        await self.db.commit()
        await self.db.refresh(run)
        return run

    async def create_benchmark_result(
        self,
        run_id: uuid.UUID,
        algorithm_name: str,
        algorithm_type: str,
        metrics: Dict[str, float]
    ) -> BenchmarkResult:
        res = BenchmarkResult(
            id=uuid.uuid4(),
            run_id=run_id,
            algorithm_name=algorithm_name,
            algorithm_type=algorithm_type,
            accuracy=metrics.get("accuracy", 0.0),
            precision=metrics.get("precision", 0.0),
            recall=metrics.get("recall", 0.0),
            f1_score=metrics.get("f1_score", 0.0),
            roc_auc=metrics.get("roc_auc", 0.0),
            latency_ms=metrics.get("latency_ms", 0.0),
            throughput=metrics.get("throughput", 0.0),
            cpu_usage=metrics.get("cpu_usage", 0.0),
            memory_usage=metrics.get("memory_usage", 0.0),
            recovery_time_ms=metrics.get("recovery_time_ms", 0.0),
            created_at=datetime.utcnow()
        )
        self.db.add(res)
        await self.db.commit()
        await self.db.refresh(res)
        return res

    async def list_benchmarks(self, limit: int = 100) -> List[BenchmarkResult]:
        result = await self.db.execute(
            select(BenchmarkResult)
            .order_by(desc(BenchmarkResult.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    # --- Governance Scores & Trends ---
    async def save_governance_score(self, score_data: Dict[str, Any]) -> GovernanceScore:
        score = GovernanceScore(
            id=uuid.uuid4(),
            overall_score=score_data["overall_score"],
            grade=score_data["grade"],
            trust_score=score_data["trust_score"],
            policy_compliance=score_data["policy_compliance"],
            explainability_score=score_data["explainability_score"],
            model_health=score_data["model_health"],
            agent_health=score_data["agent_health"],
            drift_score=score_data["drift_score"],
            security_score=score_data["security_score"],
            recovery_score=score_data["recovery_score"],
            incident_frequency=score_data["incident_frequency"],
            human_review_rate=score_data["human_review_rate"],
            created_at=datetime.utcnow()
        )
        self.db.add(score)
        
        # Save snapshot in history as well
        history = GovernanceHistory(
            id=uuid.uuid4(),
            timestamp=datetime.utcnow(),
            score=score_data["overall_score"],
            metrics_snapshot=score_data
        )
        self.db.add(history)
        
        await self.db.commit()
        await self.db.refresh(score)
        return score

    async def get_latest_governance_score(self) -> Optional[GovernanceScore]:
        result = await self.db.execute(
            select(GovernanceScore)
            .order_by(desc(GovernanceScore.created_at))
            .limit(1)
        )
        return result.scalars().first()

    async def get_governance_history(self, limit: int = 50) -> List[GovernanceHistory]:
        result = await self.db.execute(
            select(GovernanceHistory)
            .order_by(desc(GovernanceHistory.timestamp))
            .limit(limit)
        )
        return list(result.scalars().all())

    # --- Agent Reputation ---
    async def get_agent_reputation(self, agent_name: str) -> Optional[AgentReputation]:
        result = await self.db.execute(
            select(AgentReputation).where(AgentReputation.agent_name == agent_name)
        )
        return result.scalars().first()

    async def save_agent_reputation(self, repo_data: Dict[str, Any]) -> AgentReputation:
        agent_name = repo_data["agent_name"]
        rep = await self.get_agent_reputation(agent_name)
        if not rep:
            rep = AgentReputation(id=uuid.uuid4(), agent_name=agent_name)
            self.db.add(rep)

        for key, val in repo_data.items():
            if hasattr(rep, key):
                setattr(rep, key, val)
        rep.last_updated = datetime.utcnow()

        # Append to history log
        hist = ReputationHistory(
            id=uuid.uuid4(),
            agent_name=agent_name,
            score=repo_data["score"],
            recorded_at=datetime.utcnow()
        )
        self.db.add(hist)

        await self.db.commit()
        await self.db.refresh(rep)
        return rep

    async def list_agent_reputations(self) -> List[AgentReputation]:
        result = await self.db.execute(
            select(AgentReputation).order_by(desc(AgentReputation.score))
        )
        return list(result.scalars().all())

    async def get_reputation_history(self, agent_name: str, limit: int = 50) -> List[ReputationHistory]:
        result = await self.db.execute(
            select(ReputationHistory)
            .where(ReputationHistory.agent_name == agent_name)
            .order_by(desc(ReputationHistory.recorded_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    # --- Failure Index ---
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

    async def get_latest_failure_index(self) -> Optional[FailureIndex]:
        result = await self.db.execute(
            select(FailureIndex)
            .order_by(desc(FailureIndex.created_at))
            .limit(1)
        )
        return result.scalars().first()

    # --- Maturity Assessment ---
    async def save_maturity_assessment(self, assessment_data: Dict[str, Any]) -> MaturityAssessment:
        ma = MaturityAssessment(
            id=uuid.uuid4(),
            maturity_level=assessment_data["maturity_level"],
            scores=assessment_data["scores"],
            recommendations=assessment_data["recommendations"],
            created_at=datetime.utcnow()
        )
        self.db.add(ma)
        await self.db.commit()
        await self.db.refresh(ma)
        return ma

    async def get_latest_maturity_assessment(self) -> Optional[MaturityAssessment]:
        result = await self.db.execute(
            select(MaturityAssessment)
            .order_by(desc(MaturityAssessment.created_at))
            .limit(1)
        )
        return result.scalars().first()

    # --- Algorithm Versions & Comparison Reports ---
    async def create_algorithm_version(
        self,
        name: str,
        type_: str,
        version: str,
        config: Dict[str, Any]
    ) -> AlgorithmVersion:
        av = AlgorithmVersion(
            id=uuid.uuid4(),
            algorithm_name=name,
            algorithm_type=type_,
            version_string=version,
            parameters_config=config,
            is_active=True,
            created_at=datetime.utcnow()
        )
        self.db.add(av)
        await self.db.commit()
        await self.db.refresh(av)
        return av

    async def list_algorithm_versions(self) -> List[AlgorithmVersion]:
        result = await self.db.execute(
            select(AlgorithmVersion).order_by(desc(AlgorithmVersion.created_at))
        )
        return list(result.scalars().all())

    async def create_comparison_report(
        self,
        title: str,
        comparison_data: Dict[str, Any],
        summary: str
    ) -> ComparisonReport:
        cr = ComparisonReport(
            id=uuid.uuid4(),
            title=title,
            comparison_data=comparison_data,
            summary=summary,
            created_at=datetime.utcnow()
        )
        self.db.add(cr)
        await self.db.commit()
        await self.db.refresh(cr)
        return cr

    async def list_comparison_reports(self) -> List[ComparisonReport]:
        result = await self.db.execute(
            select(ComparisonReport).order_by(desc(ComparisonReport.created_at))
        )
        return list(result.scalars().all())
