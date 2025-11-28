"""
Planner Agent - Decomposes user queries into executable subtasks
"""

import json
from typing import Dict, Any, List
from .base_agent import BaseAgent


class PlannerAgent(BaseAgent):
    """
    Planner Agent responsible for:
    - Understanding user queries
    - Decomposing into subtasks
    - Creating execution plans
    - Orchestrating agent workflow
    """
    
    def __init__(self, config: Dict[str, Any], logger: Any):
        super().__init__("Planner", config, logger)
        self.prompt_template = self.load_prompt("planner_prompt")
    
    def create_plan(self, query: str, dataset_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create execution plan from user query
        
        Args:
            query: User's analytical query
            dataset_info: Information about available data
            
        Returns:
            Structured execution plan
        """
        self.logger.info(f"Planning for query: {query}")
        
        # Format prompt with query and dataset info
        prompt_vars = {
            "query": query,
            "dataset_schema": self._format_schema(dataset_info.get("schema", {})),
            "date_range": dataset_info.get("date_range", "Unknown")
        }
        
        prompt = self.format_prompt(self.prompt_template, prompt_vars)
        
        # Call LLM to generate plan
        response = self.call_llm(
            prompt,
            temperature=self.config.get('agents', {}).get('planner', {}).get('temperature', 0.3),
            model=self.config.get('agents', {}).get('planner', {}).get('model', 'gpt-4')
        )
        
        # Parse response
        plan = self.parse_json_response(response)
        
        if not plan or 'execution_plan' not in plan:
            # Fallback to default plan structure
            self.logger.warning("Using fallback plan generation")
            plan = self._create_default_plan(query)
        
        # Validate plan structure
        self._validate_plan(plan)
        
        # Log execution
        self.log_execution("create_plan", plan, {"query": query})
        
        return plan
    
    def _format_schema(self, schema: Dict[str, Any]) -> str:
        """Format dataset schema for prompt"""
        if not schema:
            return "campaign_name, adset_name, date, spend, impressions, clicks, ctr, purchases, revenue, roas, creative_type, creative_message, audience_type, platform, country"
        
        return ", ".join(schema.keys())
    
    def _create_default_plan(self, query: str) -> Dict[str, Any]:
        """Create default plan structure for common queries"""
        self.logger.warning("Using default plan structure")
        
        # Analyze query for keywords
        query_lower = query.lower()
        
        # Determine analysis focus
        metrics_mentioned = []
        if 'roas' in query_lower:
            metrics_mentioned.append('roas')
        if 'ctr' in query_lower or 'click' in query_lower:
            metrics_mentioned.append('ctr')
        if 'spend' in query_lower or 'budget' in query_lower:
            metrics_mentioned.append('spend')
        if 'revenue' in query_lower or 'sales' in query_lower:
            metrics_mentioned.append('revenue')
        
        if not metrics_mentioned:
            metrics_mentioned = ['roas', 'ctr']  # Default metrics
        
        # Determine time period
        time_period = "last 14 days"
        if 'week' in query_lower:
            time_period = "last 7 days"
        elif 'month' in query_lower:
            time_period = "last 30 days"
        
        plan = {
            "query_understanding": {
                "main_objective": query,
                "key_metrics": metrics_mentioned,
                "time_period": time_period,
                "complexity": "medium"
            },
            "execution_plan": [
                {
                    "task_id": "task_1",
                    "task_name": "Load and analyze data",
                    "agent": "data_agent",
                    "description": f"Load dataset and calculate summary statistics for {', '.join(metrics_mentioned)}",
                    "inputs": ["full_dataset"],
                    "outputs": ["data_summary", "key_statistics"],
                    "dependencies": [],
                    "priority": "high"
                },
                {
                    "task_id": "task_2",
                    "task_name": "Generate hypotheses",
                    "agent": "insight_agent",
                    "description": f"Generate hypotheses explaining patterns in {', '.join(metrics_mentioned)}",
                    "inputs": ["data_summary", "key_statistics"],
                    "outputs": ["hypotheses"],
                    "dependencies": ["task_1"],
                    "priority": "high"
                },
                {
                    "task_id": "task_3",
                    "task_name": "Validate hypotheses",
                    "agent": "evaluator",
                    "description": "Test each hypothesis with statistical analysis",
                    "inputs": ["hypotheses", "full_dataset"],
                    "outputs": ["validated_hypotheses"],
                    "dependencies": ["task_2"],
                    "priority": "high"
                },
                {
                    "task_id": "task_4",
                    "task_name": "Generate creative recommendations",
                    "agent": "creative_generator",
                    "description": "Create new creative suggestions for underperforming campaigns",
                    "inputs": ["validated_hypotheses", "creative_performance_data"],
                    "outputs": ["creative_recommendations"],
                    "dependencies": ["task_3"],
                    "priority": "medium"
                }
            ],
            "expected_insights": [
                f"Root causes of {', '.join(metrics_mentioned)} changes",
                "Performance drivers by segment",
                "Actionable recommendations"
            ],
            "confidence": 0.75,
            "reasoning": "Default plan covering standard performance analysis workflow"
        }
        
        return plan
    
    def _validate_plan(self, plan: Dict[str, Any]) -> bool:
        """Validate plan structure"""
        required_fields = ['query_understanding', 'execution_plan', 'confidence']
        
        if not self.validate_output(plan, required_fields):
            self.logger.error("Plan validation failed")
            return False
        
        # Validate execution plan tasks
        if not plan['execution_plan']:
            self.logger.error("Execution plan is empty")
            return False
        
        for task in plan['execution_plan']:
            required_task_fields = ['task_id', 'agent', 'description']
            if not all(field in task for field in required_task_fields):
                self.logger.error(f"Task missing required fields: {task}")
                return False
        
        self.logger.info(f"Plan validated successfully with {len(plan['execution_plan'])} tasks")
        return True
    
    def get_next_task(self, plan: Dict[str, Any], completed_tasks: List[str]) -> Dict[str, Any]:
        """
        Get next task to execute based on dependencies
        
        Args:
            plan: Execution plan
            completed_tasks: List of completed task IDs
            
        Returns:
            Next task to execute or None if all complete
        """
        for task in plan['execution_plan']:
            task_id = task['task_id']
            
            # Skip if already completed
            if task_id in completed_tasks:
                continue
            
            # Check if dependencies are met
            dependencies = task.get('dependencies', [])
            if all(dep in completed_tasks for dep in dependencies):
                self.logger.info(f"Next task: {task_id} - {task['task_name']}")
                return task
        
        self.logger.info("No more tasks to execute")
        return None
    
    def update_plan(self, plan: Dict[str, Any], new_insights: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update plan based on intermediate insights (adaptive planning)
        
        Args:
            plan: Current execution plan
            new_insights: New insights that might affect the plan
            
        Returns:
            Updated plan
        """
        # This enables adaptive planning where the plan evolves based on findings
        self.logger.info("Updating plan based on new insights")
        
        # Could add new tasks, reprioritize, or modify existing tasks
        # For now, return plan as-is (implement adaptive logic as needed)
        
        return plan
