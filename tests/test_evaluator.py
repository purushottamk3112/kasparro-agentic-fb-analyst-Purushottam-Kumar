"""
Tests for Evaluator Agent
"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.evaluator import EvaluatorAgent
from src.agents.data_agent import DataAgent
from src.utils import load_config, setup_logger


class TestEvaluatorAgent(unittest.TestCase):
    """Test cases for Evaluator Agent"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.config = load_config()
        cls.logger = setup_logger("TestEvaluator", cls.config)
        
        # Initialize data agent and load test data
        cls.data_agent = DataAgent(cls.config, cls.logger)
        
        # Try to load data
        data_path = Path(__file__).parent.parent / "synthetic_fb_ads_undergarments.csv"
        if data_path.exists():
            cls.data_agent.load_data(str(data_path))
            cls.has_data = True
        else:
            cls.has_data = False
        
        cls.evaluator = EvaluatorAgent(cls.config, cls.logger, cls.data_agent)
    
    def test_evaluator_initialization(self):
        """Test evaluator initializes correctly"""
        self.assertIsNotNone(self.evaluator)
        self.assertEqual(self.evaluator.name, "Evaluator")
    
    def test_calculate_cohens_d(self):
        """Test Cohen's d calculation"""
        import numpy as np
        
        group1 = np.array([1, 2, 3, 4, 5])
        group2 = np.array([3, 4, 5, 6, 7])
        
        d = self.evaluator._calculate_cohens_d(group1, group2)
        
        # Should have a positive effect size
        self.assertGreater(d, 0)
        self.assertLess(d, 3)  # Reasonable upper bound
    
    def test_interpret_test_result(self):
        """Test interpretation of statistical results"""
        # Significant with large effect
        interpretation = self.evaluator._interpret_test_result(0.01, 0.9)
        self.assertIn("Statistically significant", interpretation)
        self.assertIn("large effect", interpretation)
        
        # Not significant
        interpretation = self.evaluator._interpret_test_result(0.5, 0.1)
        self.assertIn("Not statistically significant", interpretation)
    
    def test_determine_result(self):
        """Test result determination from confidence"""
        self.assertEqual(self.evaluator._determine_result(0.8), "SUPPORTED")
        self.assertEqual(self.evaluator._determine_result(0.6), "LIKELY")
        self.assertEqual(self.evaluator._determine_result(0.4), "INCONCLUSIVE")
        self.assertEqual(self.evaluator._determine_result(0.2), "UNLIKELY")
        self.assertEqual(self.evaluator._determine_result(0.05), "REFUTED")
    
    @unittest.skipIf(not hasattr(setUpClass.__func__(None), 'has_data') or not setUpClass.__func__(None).has_data,
                     "Data not available for testing")
    def test_evaluate_hypothesis_with_data(self):
        """Test hypothesis evaluation with real data"""
        # Create a test hypothesis
        hypothesis = {
            "hypothesis_id": "test_hyp",
            "hypothesis": "Test hypothesis",
            "category": "creative",
            "evidence_required": []
        }
        
        data_summary = self.data_agent.analyze_data("Test analysis")
        
        result = self.evaluator.evaluate_hypothesis(hypothesis, data_summary)
        
        # Check result structure
        self.assertIn("hypothesis_id", result)
        self.assertIn("evaluation_result", result)
        self.assertIn("confidence_score", result)
        self.assertIn("evidence_analysis", result)
    
    def test_generate_recommendation(self):
        """Test recommendation generation"""
        hypothesis = {
            "potential_solutions": ["Solution 1", "Solution 2"]
        }
        
        # High confidence
        rec = self.evaluator._generate_recommendation(hypothesis, 3, 3)
        self.assertIn("Solution 1", rec)
        
        # Low confidence
        rec = self.evaluator._generate_recommendation(hypothesis, 0, 3)
        self.assertIn("Insufficient", rec)


def run_tests():
    """Run all tests"""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == "__main__":
    run_tests()
