"""
Base Agent class with shared functionality
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class BaseAgent:
    """Base class for all agents with common functionality"""
    
    def __init__(self, name: str, config: Dict[str, Any], logger: Any):
        self.name = name
        self.config = config
        self.logger = logger
        self.call_count = 0
        self.total_tokens = 0
        
    def load_prompt(self, prompt_name: str) -> str:
        """Load prompt template from prompts directory"""
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / f"{prompt_name}.md"
        
        if not prompt_path.exists():
            self.logger.warning(f"Prompt file not found: {prompt_path}")
            return ""
            
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def format_prompt(self, template: str, variables: Dict[str, Any]) -> str:
        """Format prompt template with variables"""
        try:
            return template.format(**variables)
        except KeyError as e:
            self.logger.error(f"Missing prompt variable: {e}")
            # Return template with placeholders for missing variables
            return template
    
    def parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse JSON from LLM response, handling markdown code blocks"""
        try:
            # Try direct parsing first
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                json_str = response[start:end].strip()
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass
                    
            self.logger.error(f"Failed to parse JSON response from {self.name}")
            return None
    
    def call_llm(self, prompt: str, temperature: float = 0.3, model: str = "gpt-4") -> str:
        """
        Call LLM (mock implementation - replace with actual API call)
        In production, this would call OpenAI, Anthropic, or other LLM APIs
        """
        self.call_count += 1
        
        # Mock implementation - in production, replace with:
        # import openai
        # response = openai.ChatCompletion.create(
        #     model=model,
        #     messages=[{"role": "user", "content": prompt}],
        #     temperature=temperature
        # )
        # return response.choices[0].message.content
        
        # For now, return a structured response template
        self.logger.info(f"{self.name} would call LLM here with model={model}, temp={temperature}")
        return self._mock_response()
    
    def _mock_response(self) -> str:
        """Mock response for testing without API calls"""
        return '{"status": "mock_response", "note": "Replace with actual LLM call"}'
    
    def log_execution(self, task: str, result: Any, metadata: Optional[Dict] = None):
        """Log agent execution details"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "task": task,
            "result_summary": str(result)[:200] if result else None,
            "metadata": metadata or {},
            "call_count": self.call_count
        }
        
        self.logger.info(f"{self.name} executed: {task}", extra=log_entry)
        
        # Save to structured log file
        self._save_log_entry(log_entry)
    
    def _save_log_entry(self, entry: Dict):
        """Save log entry to JSON file"""
        log_dir = Path(__file__).parent.parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"{self.name.lower().replace(' ', '_')}.jsonl"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
    
    def validate_output(self, output: Dict[str, Any], required_fields: list) -> bool:
        """Validate that output contains required fields"""
        missing_fields = [field for field in required_fields if field not in output]
        
        if missing_fields:
            self.logger.error(f"{self.name} output missing fields: {missing_fields}")
            return False
            
        return True
    
    def retry_with_reflection(self, func, max_retries: int = 2, *args, **kwargs):
        """Retry function with reflection on failure"""
        for attempt in range(max_retries + 1):
            try:
                result = func(*args, **kwargs)
                
                # Check if result has sufficient confidence
                if isinstance(result, dict) and 'confidence' in result:
                    if result['confidence'] >= self.config.get('confidence_min', 0.6):
                        return result
                    elif attempt < max_retries:
                        self.logger.warning(
                            f"{self.name} low confidence ({result['confidence']}), retrying..."
                        )
                        continue
                
                return result
                
            except Exception as e:
                if attempt < max_retries:
                    self.logger.warning(f"{self.name} attempt {attempt + 1} failed: {e}, retrying...")
                else:
                    self.logger.error(f"{self.name} all attempts failed: {e}")
                    raise
        
        return None
