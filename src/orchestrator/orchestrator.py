"""
Main Orchestrator - Coordinates multi-agent workflow
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from ..agents import (
    PlannerAgent,
    DataAgent,
    InsightAgent,
    EvaluatorAgent,
    CreativeGeneratorAgent
)
from ..utils import setup_logger


class AgenticOrchestrator:
    """
    Main orchestrator coordinating the multi-agent system
    
    Workflow:
    1. Planner decomposes query
    2. Data Agent loads and analyzes data
    3. Insight Agent generates hypotheses
    4. Evaluator validates hypotheses
    5. Creative Generator proposes new creatives
    6. Generate final report
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = setup_logger("Orchestrator", config)
        
        # Initialize agents
        self.planner = PlannerAgent(config, setup_logger("Planner", config))
        self.data_agent = DataAgent(config, setup_logger("DataAgent", config))
        self.insight_agent = InsightAgent(config, setup_logger("InsightAgent", config))
        self.evaluator = EvaluatorAgent(config, setup_logger("Evaluator", config), self.data_agent)
        self.creative_generator = CreativeGeneratorAgent(config, setup_logger("CreativeGenerator", config))
        
        # Execution state
        self.execution_state = {
            "completed_tasks": [],
            "data_summary": None,
            "hypotheses": None,
            "validated_hypotheses": None,
            "creative_recommendations": None
        }
        
        self.logger.info("Orchestrator initialized with all agents")
    
    def run(self, query: str, data_path: str = None) -> Dict[str, Any]:
        """
        Execute complete agentic workflow
        
        Args:
            query: User's analytical query
            data_path: Path to data CSV
            
        Returns:
            Complete analysis results
        """
        self.logger.info(f"=== Starting Agentic Analysis ===")
        self.logger.info(f"Query: {query}")
        
        try:
            # Step 1: Load data
            if not self._load_data(data_path):
                return {"error": "Failed to load data"}
            
            # Step 2: Create execution plan
            plan = self._create_plan(query)
            
            # Step 3: Execute plan
            results = self._execute_plan(plan, query)
            
            # Step 4: Generate outputs
            self._generate_outputs(results, query)
            
            self.logger.info("=== Analysis Complete ===")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Orchestration failed: {e}", exc_info=True)
            return {"error": str(e)}
    
    def _load_data(self, data_path: str = None) -> bool:
        """Load data using Data Agent"""
        self.logger.info("Step 1: Loading data")
        
        if data_path is None:
            # Use config path
            if self.config.get('use_sample_data'):
                data_path = self.config.get('sample_data_csv')
            else:
                data_path = self.config.get('data_csv')
        
        # Try relative to project root
        if not Path(data_path).exists():
            project_root = Path(__file__).parent.parent.parent
            data_path = project_root / data_path
        
        success = self.data_agent.load_data(str(data_path))
        
        if success:
            self.logger.info(f"Data loaded successfully from {data_path}")
        else:
            self.logger.error(f"Failed to load data from {data_path}")
        
        return success
    
    def _create_plan(self, query: str) -> Dict[str, Any]:
        """Create execution plan using Planner Agent"""
        self.logger.info("Step 2: Creating execution plan")
        
        dataset_info = self.data_agent.get_dataset_info()
        plan = self.planner.create_plan(query, dataset_info)
        
        num_tasks = len(plan.get('execution_plan', []))
        self.logger.info(f"Plan created with {num_tasks} tasks")
        
        return plan
    
    def _execute_plan(self, plan: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Execute the plan step by step"""
        self.logger.info("Step 3: Executing plan")
        
        results = {
            "query": query,
            "plan": plan,
            "execution_log": []
        }
        
        # Execute tasks in order
        while True:
            next_task = self.planner.get_next_task(
                plan,
                self.execution_state['completed_tasks']
            )
            
            if next_task is None:
                break
            
            self.logger.info(f"Executing: {next_task['task_name']}")
            
            task_result = self._execute_task(next_task)
            
            results['execution_log'].append({
                "task": next_task['task_name'],
                "status": "completed" if task_result else "failed",
                "timestamp": datetime.now().isoformat()
            })
            
            self.execution_state['completed_tasks'].append(next_task['task_id'])
        
        # Package final results
        results.update({
            "data_summary": self.execution_state['data_summary'],
            "hypotheses": self.execution_state['hypotheses'],
            "validated_hypotheses": self.execution_state['validated_hypotheses'],
            "creative_recommendations": self.execution_state['creative_recommendations']
        })
        
        return results
    
    def _execute_task(self, task: Dict[str, Any]) -> bool:
        """Execute a single task"""
        agent_name = task.get('agent')
        
        try:
            if agent_name == 'data_agent':
                return self._execute_data_task(task)
            elif agent_name == 'insight_agent':
                return self._execute_insight_task(task)
            elif agent_name == 'evaluator':
                return self._execute_evaluator_task(task)
            elif agent_name == 'creative_generator':
                return self._execute_creative_task(task)
            else:
                self.logger.warning(f"Unknown agent: {agent_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}", exc_info=True)
            return False
    
    def _execute_data_task(self, task: Dict[str, Any]) -> bool:
        """Execute data analysis task"""
        analysis_period = self._extract_period_from_task(task)
        
        data_summary = self.data_agent.analyze_data(
            task['description'],
            analysis_period
        )
        
        self.execution_state['data_summary'] = data_summary
        return True
    
    def _execute_insight_task(self, task: Dict[str, Any]) -> bool:
        """Execute hypothesis generation task"""
        if not self.execution_state['data_summary']:
            self.logger.error("Data summary not available")
            return False
        
        hypotheses = self.insight_agent.generate_hypotheses(
            task['description'],
            self.execution_state['data_summary'],
            self.execution_state['data_summary'].get('key_observations', [])
        )
        
        self.execution_state['hypotheses'] = hypotheses
        return True
    
    def _execute_evaluator_task(self, task: Dict[str, Any]) -> bool:
        """Execute hypothesis validation task"""
        if not self.execution_state['hypotheses']:
            self.logger.error("Hypotheses not available")
            return False
        
        validated = self.evaluator.evaluate_all_hypotheses(
            self.execution_state['hypotheses'],
            self.execution_state['data_summary']
        )
        
        self.execution_state['validated_hypotheses'] = validated
        return True
    
    def _execute_creative_task(self, task: Dict[str, Any]) -> bool:
        """Execute creative generation task"""
        if not self.execution_state['validated_hypotheses']:
            self.logger.warning("No validated hypotheses, generating creatives anyway")
            validated = []
        else:
            validated = self.execution_state['validated_hypotheses']
        
        creative_performance = self.data_agent.get_creative_performance()
        
        recommendations = self.creative_generator.generate_recommendations(
            validated,
            creative_performance
        )
        
        self.execution_state['creative_recommendations'] = recommendations
        return True
    
    def _extract_period_from_task(self, task: Dict[str, Any]) -> str:
        """Extract time period from task description"""
        description = task.get('description', '').lower()
        
        if 'last 7 days' in description or 'week' in description:
            return 'last 7 days'
        elif 'last 14 days' in description or '2 weeks' in description:
            return 'last 14 days'
        elif 'last 30 days' in description or 'month' in description:
            return 'last 30 days'
        
        return None
    
    def _generate_outputs(self, results: Dict[str, Any], query: str):
        """Generate output files"""
        self.logger.info("Step 4: Generating outputs")
        
        output_dir = Path(self.config.get('output', {}).get('reports_dir', 'reports'))
        output_dir.mkdir(exist_ok=True)
        
        # Generate insights.json
        self._save_insights_json(output_dir, results)
        
        # Generate creatives.json
        self._save_creatives_json(output_dir, results)
        
        # Generate report.md
        self._save_report_md(output_dir, results, query)
        
        self.logger.info(f"Outputs saved to {output_dir}")
    
    def _save_insights_json(self, output_dir: Path, results: Dict[str, Any]):
        """Save insights to JSON"""
        insights_file = output_dir / "insights.json"
        
        insights_data = {
            "query": results.get('query'),
            "analysis_date": datetime.now().isoformat(),
            "data_summary": results.get('data_summary'),
            "hypotheses": results.get('hypotheses'),
            "validated_hypotheses": results.get('validated_hypotheses'),
            "execution_log": results.get('execution_log', [])
        }
        
        with open(insights_file, 'w', encoding='utf-8') as f:
            json.dump(insights_data, f, indent=2, default=str)
        
        self.logger.info(f"Saved insights.json ({insights_file.stat().st_size} bytes)")
    
    def _save_creatives_json(self, output_dir: Path, results: Dict[str, Any]):
        """Save creative recommendations to JSON"""
        creatives_file = output_dir / "creatives.json"
        
        creative_data = results.get('creative_recommendations', {})
        
        with open(creatives_file, 'w', encoding='utf-8') as f:
            json.dump(creative_data, f, indent=2, default=str)
        
        self.logger.info(f"Saved creatives.json ({creatives_file.stat().st_size} bytes)")
    
    def _save_report_md(self, output_dir: Path, results: Dict[str, Any], query: str):
        """Save human-readable report in Markdown"""
        report_file = output_dir / "report.md"
        
        # Build report content
        report_content = self._build_markdown_report(results, query)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.logger.info(f"Saved report.md ({report_file.stat().st_size} bytes)")
    
    def _build_markdown_report(self, results: Dict[str, Any], query: str) -> str:
        """Build comprehensive Markdown report"""
        lines = []
        
        # Header
        lines.append("# Facebook Ads Performance Analysis Report")
        lines.append("")
        lines.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Query:** {query}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")
        data_summary = results.get('data_summary', {})
        if data_summary:
            overall = data_summary.get('summary_statistics', {}).get('overall', {})
            lines.append(f"- **Total Spend:** ${overall.get('total_spend', 0):,.2f}")
            lines.append(f"- **Total Revenue:** ${overall.get('total_revenue', 0):,.2f}")
            lines.append(f"- **Average ROAS:** {overall.get('avg_roas', 0):.2f}")
            lines.append(f"- **Average CTR:** {overall.get('avg_ctr', 0):.3%}")
        lines.append("")
        
        # Key Findings
        lines.append("## Key Findings")
        lines.append("")
        
        validated = results.get('validated_hypotheses', [])
        if validated:
            supported = [h for h in validated if h.get('evaluation_result') == 'SUPPORTED']
            
            if supported:
                lines.append("### Validated Insights")
                lines.append("")
                for i, hyp in enumerate(supported, 1):
                    lines.append(f"{i}. **{hyp.get('hypothesis_statement', 'N/A')}**")
                    lines.append(f"   - Confidence: {hyp.get('confidence_score', 0):.0%}")
                    lines.append(f"   - Recommendation: {hyp.get('recommendation', 'N/A')}")
                    lines.append("")
        
        # Performance Analysis
        lines.append("## Performance Analysis")
        lines.append("")
        
        if data_summary:
            # Top Performers
            top_perf = data_summary.get('top_performers', {})
            if top_perf.get('by_roas'):
                lines.append("### Top Performing Campaigns (by ROAS)")
                lines.append("")
                for perf in top_perf['by_roas'][:3]:
                    lines.append(f"- **{perf['name']}**: {perf['value']:.2f} ROAS")
                lines.append("")
            
            # Bottom Performers
            bottom_perf = data_summary.get('bottom_performers', {})
            if bottom_perf.get('by_roas'):
                lines.append("### Underperforming Campaigns (by ROAS)")
                lines.append("")
                for perf in bottom_perf['by_roas'][:3]:
                    lines.append(f"- **{perf['name']}**: {perf['value']:.2f} ROAS")
                lines.append("")
        
        # Creative Recommendations
        lines.append("## Creative Recommendations")
        lines.append("")
        
        creative_recs = results.get('creative_recommendations', {})
        if creative_recs:
            recommendations = creative_recs.get('creative_recommendations', [])
            
            if recommendations:
                lines.append("### Priority Creative Tests")
                lines.append("")
                
                high_priority = [r for r in recommendations if r.get('testing_priority') == 'high']
                for i, rec in enumerate(high_priority, 1):
                    lines.append(f"#### Test {i}: {rec.get('headline', 'N/A')}")
                    lines.append("")
                    lines.append(f"**Creative Type:** {rec.get('creative_type')}")
                    lines.append(f"**Message:** {rec.get('creative_message')}")
                    lines.append(f"**Rationale:** {rec.get('rationale')}")
                    lines.append(f"**Expected Impact:** {rec.get('expected_improvement')}")
                    lines.append("")
        
        # Next Steps
        lines.append("## Recommended Next Steps")
        lines.append("")
        lines.append("1. Implement top priority creative tests")
        lines.append("2. Monitor performance daily for first 3-5 days")
        lines.append("3. Scale winning creatives after statistical significance")
        lines.append("4. Continue testing secondary recommendations")
        lines.append("")
        
        lines.append("---")
        lines.append("")
        lines.append("*Report generated by Kasparro Agentic FB Analyst*")
        
        return "\n".join(lines)
