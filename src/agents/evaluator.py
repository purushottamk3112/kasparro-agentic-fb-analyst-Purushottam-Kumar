"""
Evaluator Agent - Validates hypotheses with statistical analysis
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from scipy import stats
from .base_agent import BaseAgent


class EvaluatorAgent(BaseAgent):
    """
    Evaluator Agent responsible for:
    - Validating hypotheses with statistical tests
    - Calculating confidence scores
    - Providing quantitative evidence
    - Determining actionability
    """
    
    def __init__(self, config: Dict[str, Any], logger: Any, data_agent):
        super().__init__("Evaluator", config, logger)
        self.prompt_template = self.load_prompt("evaluator_prompt")
        self.data_agent = data_agent
    
    def evaluate_hypothesis(
        self,
        hypothesis: Dict[str, Any],
        data_summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate a single hypothesis using statistical analysis
        
        Args:
            hypothesis: Hypothesis to evaluate
            data_summary: Data summary from DataAgent
            
        Returns:
            Evaluation results with confidence score
        """
        self.logger.info(f"Evaluating hypothesis: {hypothesis.get('hypothesis_id')}")
        
        # Perform statistical tests based on hypothesis category
        statistical_results = self._perform_statistical_tests(hypothesis)
        
        # Analyze evidence
        evaluation = self._analyze_evidence(hypothesis, statistical_results, data_summary)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(evaluation, statistical_results)
        evaluation['confidence_score'] = confidence
        evaluation['actionable_confidence'] = confidence
        
        # Determine evaluation result
        evaluation['evaluation_result'] = self._determine_result(confidence)
        
        # Log execution
        self.log_execution("evaluate_hypothesis", evaluation, {
            "hypothesis_id": hypothesis.get('hypothesis_id'),
            "confidence": confidence
        })
        
        return evaluation
    
    def evaluate_all_hypotheses(
        self,
        hypotheses: Dict[str, Any],
        data_summary: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Evaluate all hypotheses"""
        results = []
        
        for hypothesis in hypotheses.get('hypotheses', []):
            evaluation = self.evaluate_hypothesis(hypothesis, data_summary)
            results.append(evaluation)
        
        return results
    
    def _perform_statistical_tests(self, hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        """Perform relevant statistical tests for the hypothesis"""
        category = hypothesis.get('category', 'general')
        hypothesis_id = hypothesis.get('hypothesis_id', '')
        
        results = {
            "tests_performed": [],
            "summary": {}
        }
        
        if self.data_agent.df is None:
            return results
        
        df = self.data_agent.df
        
        # Test based on category
        if 'creative' in hypothesis_id or category == 'creative':
            results = self._test_creative_hypothesis(df, hypothesis)
        elif 'audience' in hypothesis_id or category == 'audience':
            results = self._test_audience_hypothesis(df, hypothesis)
        elif 'roas' in hypothesis_id:
            results = self._test_roas_hypothesis(df, hypothesis)
        elif 'ctr' in hypothesis_id:
            results = self._test_ctr_hypothesis(df, hypothesis)
        
        return results
    
    def _test_creative_hypothesis(self, df: pd.DataFrame, hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        """Test creative-related hypotheses"""
        tests = []
        
        if 'creative_type' not in df.columns:
            return {"tests_performed": tests, "summary": {}}
        
        # Compare ROAS across creative types
        creative_groups = []
        for ctype in df['creative_type'].unique():
            group_data = df[df['creative_type'] == ctype]['roas'].dropna()
            if len(group_data) >= 3:  # Minimum sample size
                creative_groups.append({
                    'name': ctype,
                    'data': group_data,
                    'mean': group_data.mean(),
                    'std': group_data.std(),
                    'n': len(group_data)
                })
        
        if len(creative_groups) >= 2:
            # Perform ANOVA or t-test
            group_data_arrays = [g['data'] for g in creative_groups]
            
            if len(creative_groups) == 2:
                # T-test for two groups
                t_stat, p_value = stats.ttest_ind(group_data_arrays[0], group_data_arrays[1])
                effect_size = self._calculate_cohens_d(group_data_arrays[0], group_data_arrays[1])
                
                tests.append({
                    "test_name": "Independent t-test",
                    "metric": "roas_by_creative_type",
                    "result": f"t={t_stat:.3f}, p={p_value:.4f}",
                    "p_value": float(p_value),
                    "effect_size": f"Cohen's d = {effect_size:.3f}",
                    "interpretation": self._interpret_test_result(p_value, effect_size)
                })
            else:
                # ANOVA for multiple groups
                f_stat, p_value = stats.f_oneway(*group_data_arrays)
                
                # Handle NaN p_value from ANOVA
                p_value_safe = p_value if p_value is not None and not np.isnan(p_value) else 1.0
                effect_size_val = 0.5 if p_value_safe < 0.05 else 0.1
                
                tests.append({
                    "test_name": "One-way ANOVA",
                    "metric": "roas_by_creative_type",
                    "result": f"F={f_stat:.3f}, p={p_value:.4f}" if not np.isnan(p_value) else f"F={f_stat:.3f}, p=N/A",
                    "p_value": float(p_value) if not np.isnan(p_value) else None,
                    "effect_size": "Multiple groups",
                    "interpretation": self._interpret_test_result(p_value, effect_size_val)
                })
        
        # CTR comparison
        if 'ctr' in df.columns:
            creative_ctr_means = df.groupby('creative_type')['ctr'].mean().to_dict()
            tests.append({
                "test_name": "Descriptive comparison",
                "metric": "ctr_by_creative_type",
                "result": str(creative_ctr_means),
                "p_value": None,
                "effect_size": "N/A",
                "interpretation": "Descriptive statistics show variation across creative types"
            })
        
        return {
            "tests_performed": tests,
            "summary": {
                "creative_groups": [{'name': g['name'], 'mean_roas': round(g['mean'], 3), 'n': g['n']} for g in creative_groups]
            }
        }
    
    def _test_audience_hypothesis(self, df: pd.DataFrame, hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        """Test audience-related hypotheses"""
        tests = []
        
        if 'audience_type' not in df.columns:
            return {"tests_performed": tests, "summary": {}}
        
        # Compare ROAS across audience types
        audience_groups = []
        for atype in df['audience_type'].unique():
            group_data = df[df['audience_type'] == atype]['roas'].dropna()
            if len(group_data) >= 3:
                audience_groups.append({
                    'name': atype,
                    'data': group_data,
                    'mean': group_data.mean(),
                    'std': group_data.std(),
                    'n': len(group_data)
                })
        
        if len(audience_groups) >= 2:
            group_data_arrays = [g['data'] for g in audience_groups]
            
            if len(audience_groups) == 2:
                t_stat, p_value = stats.ttest_ind(group_data_arrays[0], group_data_arrays[1])
                effect_size = self._calculate_cohens_d(group_data_arrays[0], group_data_arrays[1])
                
                tests.append({
                    "test_name": "Independent t-test",
                    "metric": "roas_by_audience_type",
                    "result": f"t={t_stat:.3f}, p={p_value:.4f}",
                    "p_value": float(p_value),
                    "effect_size": f"Cohen's d = {effect_size:.3f}",
                    "interpretation": self._interpret_test_result(p_value, effect_size)
                })
            else:
                f_stat, p_value = stats.f_oneway(*group_data_arrays)
                
                # Handle NaN p_value from ANOVA
                p_value_safe = p_value if p_value is not None and not np.isnan(p_value) else 1.0
                effect_size_val = 0.5 if p_value_safe < 0.05 else 0.1
                
                tests.append({
                    "test_name": "One-way ANOVA",
                    "metric": "roas_by_audience_type",
                    "result": f"F={f_stat:.3f}, p={p_value:.4f}" if not np.isnan(p_value) else f"F={f_stat:.3f}, p=N/A",
                    "p_value": float(p_value) if not np.isnan(p_value) else None,
                    "effect_size": "Multiple groups",
                    "interpretation": self._interpret_test_result(p_value, effect_size_val)
                })
        
        return {
            "tests_performed": tests,
            "summary": {
                "audience_groups": [{'name': g['name'], 'mean_roas': round(g['mean'], 3), 'n': g['n']} for g in audience_groups]
            }
        }
    
    def _test_roas_hypothesis(self, df: pd.DataFrame, hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        """Test ROAS trend hypotheses"""
        tests = []
        
        if 'date' not in df.columns or 'roas' not in df.columns:
            return {"tests_performed": tests, "summary": {}}
        
        # Time series analysis
        daily_roas = df.groupby('date')['roas'].mean().sort_index()
        
        if len(daily_roas) >= 7:
            # Split into early vs late period
            mid_point = len(daily_roas) // 2
            early_period = daily_roas.iloc[:mid_point]
            late_period = daily_roas.iloc[mid_point:]
            
            # T-test comparing periods
            t_stat, p_value = stats.ttest_ind(early_period, late_period)
            effect_size = self._calculate_cohens_d(early_period, late_period)
            
            tests.append({
                "test_name": "Time period comparison (t-test)",
                "metric": "roas_early_vs_late",
                "result": f"Early: {early_period.mean():.3f}, Late: {late_period.mean():.3f}, t={t_stat:.3f}, p={p_value:.4f}",
                "p_value": float(p_value),
                "effect_size": f"Cohen's d = {effect_size:.3f}",
                "interpretation": self._interpret_test_result(p_value, effect_size)
            })
            
            # Trend analysis
            x = np.arange(len(daily_roas))
            y = daily_roas.values
            slope, intercept, r_value, p_value_trend, std_err = stats.linregress(x, y)
            
            tests.append({
                "test_name": "Linear trend analysis",
                "metric": "roas_over_time",
                "result": f"Slope={slope:.4f}, R²={r_value**2:.3f}, p={p_value_trend:.4f}",
                "p_value": float(p_value_trend),
                "effect_size": f"R² = {r_value**2:.3f}",
                "interpretation": f"{'Significant' if p_value_trend < 0.05 else 'Non-significant'} {'downward' if slope < 0 else 'upward'} trend"
            })
        
        return {
            "tests_performed": tests,
            "summary": {
                "overall_roas_mean": float(df['roas'].mean()),
                "roas_std": float(df['roas'].std()),
                "days_analyzed": len(daily_roas)
            }
        }
    
    def _test_ctr_hypothesis(self, df: pd.DataFrame, hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        """Test CTR hypotheses"""
        tests = []
        
        if 'ctr' not in df.columns:
            return {"tests_performed": tests, "summary": {}}
        
        # Overall CTR analysis
        overall_ctr = df['ctr'].mean()
        benchmark_ctr = 0.015  # 1.5% benchmark
        
        # One-sample t-test against benchmark
        t_stat, p_value = stats.ttest_1samp(df['ctr'].dropna(), benchmark_ctr)
        
        tests.append({
            "test_name": "One-sample t-test vs benchmark",
            "metric": "ctr_vs_benchmark",
            "result": f"Observed: {overall_ctr:.4f}, Benchmark: {benchmark_ctr:.4f}, t={t_stat:.3f}, p={p_value:.4f}",
            "p_value": float(p_value),
            "effect_size": f"Difference = {(overall_ctr - benchmark_ctr):.4f}",
            "interpretation": f"CTR is {'significantly lower' if overall_ctr < benchmark_ctr and p_value < 0.05 else 'not significantly different from'} benchmark"
        })
        
        return {
            "tests_performed": tests,
            "summary": {
                "overall_ctr": float(overall_ctr),
                "benchmark_ctr": float(benchmark_ctr),
                "n_observations": len(df)
            }
        }
    
    def _calculate_cohens_d(self, group1, group2) -> float:
        """Calculate Cohen's d effect size"""
        n1, n2 = len(group1), len(group2)
        var1, var2 = group1.var(), group2.var()
        
        # Pooled standard deviation
        pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        
        if pooled_std == 0:
            return 0.0
        
        return abs(group1.mean() - group2.mean()) / pooled_std
    
    def _interpret_test_result(self, p_value: float, effect_size: float) -> str:
        """Interpret statistical test results"""
        # Handle None or NaN p_value
        if p_value is None or (isinstance(p_value, float) and np.isnan(p_value)):
            return "Unable to determine significance (invalid p-value)"
        
        significance = "Statistically significant" if p_value < 0.05 else "Not statistically significant"
        
        if isinstance(effect_size, float) and not np.isnan(effect_size):
            if effect_size >= 0.8:
                magnitude = "large effect size"
            elif effect_size >= 0.5:
                magnitude = "medium effect size"
            elif effect_size >= 0.2:
                magnitude = "small effect size"
            else:
                magnitude = "negligible effect size"
        else:
            magnitude = "effect size calculated"
        
        return f"{significance} (p={p_value:.4f}), {magnitude}"
    
    def _analyze_evidence(
        self,
        hypothesis: Dict[str, Any],
        statistical_results: Dict[str, Any],
        data_summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze evidence for hypothesis"""
        
        tests = statistical_results.get('tests_performed', [])
        
        # Extract key findings
        key_findings = []
        contradicting_evidence = []
        
        for test in tests:
            p_value = test.get('p_value')
            if p_value is not None:
                if p_value < 0.05:
                    key_findings.append({
                        "finding": test['interpretation'],
                        "support_level": "strong" if p_value < 0.01 else "moderate",
                        "data_source": test['test_name']
                    })
                else:
                    contradicting_evidence.append(test['interpretation'])
        
        # Quantitative support assessment - handle None p_values properly
        significant_tests = sum(1 for t in tests if t.get('p_value') is not None and t.get('p_value') < 0.05)
        total_tests = len([t for t in tests if t.get('p_value') is not None])
        
        return {
            "hypothesis_id": hypothesis.get('hypothesis_id'),
            "hypothesis_statement": hypothesis.get('hypothesis'),
            "evidence_analysis": {
                "statistical_tests_performed": tests,
                "key_findings": key_findings,
                "contradicting_evidence": contradicting_evidence,
                "confounding_factors": []
            },
            "quantitative_support": {
                "primary_metric_change": "N/A",
                "statistical_significance": "yes" if significant_tests > 0 else "no",
                "effect_size_rating": "medium",
                "sample_size_adequate": "yes" if total_tests > 0 else "insufficient data",
                "consistency_across_segments": "partial"
            },
            "reasoning": f"Evaluated using {total_tests} statistical tests. {significant_tests} tests showed significant results.",
            "limitations": [
                "Analysis based on observational data (correlation, not causation)",
                "Potential confounding variables not fully controlled",
                "Time-series analysis limited by available data period"
            ],
            "additional_tests_recommended": [
                "Frequency analysis to confirm audience fatigue",
                "Competitive intelligence data",
                "A/B test validation of proposed solutions"
            ],
            "recommendation": self._generate_recommendation(hypothesis, significant_tests, total_tests)
        }
    
    def _calculate_confidence(self, evaluation: Dict[str, Any], statistical_results: Dict[str, Any]) -> float:
        """Calculate confidence score for evaluation"""
        
        tests = statistical_results.get('tests_performed', [])
        
        if not tests:
            return 0.5  # Neutral confidence if no tests
        
        # Count significant tests
        significant = sum(1 for t in tests if t.get('p_value') is not None and t.get('p_value') < 0.05)
        total = len([t for t in tests if t.get('p_value') is not None])
        
        if total == 0:
            return 0.5
        
        # Base confidence on proportion of significant tests
        base_confidence = significant / total
        
        # Adjust for effect sizes
        large_effects = sum(1 for t in tests if 'large effect' in t.get('interpretation', ''))
        if large_effects > 0:
            base_confidence = min(base_confidence + 0.1, 1.0)
        
        # Penalize for contradicting evidence
        contradicting = len(evaluation['evidence_analysis']['contradicting_evidence'])
        if contradicting > 0:
            base_confidence = max(base_confidence - 0.1 * contradicting, 0.1)
        
        return round(base_confidence, 2)
    
    def _determine_result(self, confidence: float) -> str:
        """Determine evaluation result based on confidence"""
        if confidence >= 0.7:
            return "SUPPORTED"
        elif confidence >= 0.5:
            return "LIKELY"
        elif confidence >= 0.3:
            return "INCONCLUSIVE"
        elif confidence >= 0.1:
            return "UNLIKELY"
        else:
            return "REFUTED"
    
    def _generate_recommendation(self, hypothesis: Dict[str, Any], significant: int, total: int) -> str:
        """Generate actionable recommendation"""
        if significant == 0:
            return "Insufficient evidence to support this hypothesis. Consider alternative explanations or gather more data."
        
        if significant / total >= 0.7:
            solutions = hypothesis.get('potential_solutions', [])
            if solutions:
                return f"Strong evidence supports this hypothesis. Recommended actions: {'; '.join(solutions[:2])}"
        
        return f"Moderate evidence supports this hypothesis. Consider testing proposed solutions: {hypothesis.get('potential_solutions', ['N/A'])[0]}"
