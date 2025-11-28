"""
Insight Agent - Generates hypotheses explaining performance patterns
"""

import json
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent


class InsightAgent(BaseAgent):
    """
    Insight Agent responsible for:
    - Generating data-driven hypotheses
    - Explaining ROAS fluctuations
    - Identifying performance drivers
    - Ranking hypotheses by likelihood
    """
    
    def __init__(self, config: Dict[str, Any], logger: Any):
        super().__init__("InsightAgent", config, logger)
        self.prompt_template = self.load_prompt("insight_agent_prompt")
    
    def generate_hypotheses(
        self,
        task_description: str,
        data_summary: Dict[str, Any],
        key_observations: List[Dict[str, Any]],
        historical_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate hypotheses explaining observed patterns
        
        Args:
            task_description: What to analyze
            data_summary: Summary statistics from DataAgent
            key_observations: Key observations to explain
            historical_context: Previous insights (for memory)
            
        Returns:
            Structured hypotheses with evidence requirements
        """
        self.logger.info(f"Generating hypotheses for: {task_description}")
        
        # Format prompt variables
        prompt_vars = {
            "task_description": task_description,
            "data_summary": json.dumps(data_summary, indent=2, default=str)[:3000],
            "key_observations": json.dumps(key_observations, indent=2),
            "historical_context": json.dumps(historical_context or {}, indent=2)
        }
        
        prompt = self.format_prompt(self.prompt_template, prompt_vars)
        
        # In production, would call LLM here
        # response = self.call_llm(prompt, temperature=0.5)
        # hypotheses = self.parse_json_response(response)
        
        # For now, generate rule-based hypotheses
        hypotheses = self._generate_rule_based_hypotheses(data_summary, key_observations)
        
        # Validate and rank hypotheses
        self._rank_hypotheses(hypotheses)
        
        # Log execution
        self.log_execution("generate_hypotheses", hypotheses, {
            "num_hypotheses": len(hypotheses.get('hypotheses', []))
        })
        
        return hypotheses
    
    def _generate_rule_based_hypotheses(
        self,
        data_summary: Dict[str, Any],
        observations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate hypotheses using rule-based logic"""
        
        hypotheses_list = []
        
        # Extract key metrics
        overall_stats = data_summary.get('summary_statistics', {}).get('overall', {})
        trends = data_summary.get('trends', {})
        by_creative = data_summary.get('summary_statistics', {}).get('by_creative_type', {})
        by_audience = data_summary.get('summary_statistics', {}).get('by_audience_type', {})
        
        # Handle None values with proper fallbacks
        avg_roas = overall_stats.get('avg_roas') or 0
        avg_ctr = overall_stats.get('avg_ctr') or 0
        roas_trend = trends.get('roas_trend') or 'stable'
        ctr_trend = trends.get('ctr_trend') or 'stable'
        
        # Hypothesis 1: ROAS Trend Analysis
        if roas_trend == 'decreasing':
            hypotheses_list.append({
                "hypothesis_id": "hyp_roas_decline",
                "hypothesis": f"ROAS is declining (trend: {roas_trend}), potentially due to audience fatigue or creative exhaustion after extended campaign runtime.",
                "category": "audience",
                "reasoning": "Declining ROAS often indicates that the target audience has seen the ads multiple times, leading to banner blindness and reduced engagement. This is especially common after 14+ days of continuous exposure.",
                "likelihood": 0.75,
                "potential_impact": "high",
                "actionability": "high",
                "evidence_required": [
                    {
                        "metric": "frequency",
                        "comparison": "week-over-week",
                        "expected_pattern": "increasing frequency correlates with decreasing CTR/ROAS"
                    },
                    {
                        "metric": "ctr",
                        "comparison": "time-series",
                        "expected_pattern": "CTR declines over time within same audience"
                    }
                ],
                "validation_approach": "Compare early campaign performance (days 1-7) vs recent performance (days 14+) for same audience segments. Check frequency metrics.",
                "potential_solutions": [
                    "Refresh creative assets with new messaging",
                    "Expand to new audience segments",
                    "Implement ad rotation strategy",
                    "Add frequency caps"
                ]
            })
        
        # Hypothesis 2: Creative Performance
        if by_creative:
            creative_roas_values = [v.get('roas', 0) for v in by_creative.values() if isinstance(v, dict)]
            if creative_roas_values and max(creative_roas_values) > 1.5 * min(creative_roas_values):
                best_creative = max(by_creative.items(), key=lambda x: x[1].get('roas', 0) if isinstance(x[1], dict) else 0)
                hypotheses_list.append({
                    "hypothesis_id": "hyp_creative_disparity",
                    "hypothesis": f"Significant creative type performance disparity detected. '{best_creative[0]}' creative type outperforms others by 50%+ in ROAS.",
                    "category": "creative",
                    "reasoning": "Different creative formats resonate differently with audiences. Video often allows for storytelling and emotional connection, while images require immediate impact. UGC builds authenticity and trust.",
                    "likelihood": 0.85,
                    "potential_impact": "high",
                    "actionability": "high",
                    "evidence_required": [
                        {
                            "metric": "roas_by_creative_type",
                            "comparison": "cross-sectional",
                            "expected_pattern": "One creative type significantly outperforms others"
                        },
                        {
                            "metric": "engagement_rate",
                            "comparison": "by_creative_type",
                            "expected_pattern": "Higher engagement for top performing creative type"
                        }
                    ],
                    "validation_approach": "Statistical test comparing ROAS across creative types controlling for audience and budget. Check if difference is significant (t-test or ANOVA).",
                    "potential_solutions": [
                        f"Shift budget allocation toward {best_creative[0]} creative type",
                        "Create more assets in top-performing format",
                        "Test hybrid approaches combining elements of top performers",
                        "Discontinue underperforming creative types"
                    ]
                })
        
        # Hypothesis 3: Low CTR Issues
        if avg_ctr < 0.015:  # Below 1.5% CTR threshold
            hypotheses_list.append({
                "hypothesis_id": "hyp_low_ctr",
                "hypothesis": f"Overall CTR is below industry benchmark ({avg_ctr:.3f} vs 0.015+ expected), indicating weak ad creative or poor audience targeting.",
                "category": "creative",
                "reasoning": "Low CTR suggests ads are not compelling enough to drive clicks. This could be due to weak headlines, unclear value propositions, or misalignment between ad content and audience interests.",
                "likelihood": 0.70,
                "potential_impact": "high",
                "actionability": "high",
                "evidence_required": [
                    {
                        "metric": "ctr",
                        "comparison": "overall_average",
                        "expected_pattern": "CTR significantly below 1.5%"
                    },
                    {
                        "metric": "creative_message_analysis",
                        "comparison": "qualitative",
                        "expected_pattern": "Weak hooks or generic messaging in low-CTR ads"
                    }
                ],
                "validation_approach": "Analyze creative messaging of low vs high CTR campaigns. Look for patterns in headline strength, value proposition clarity, and CTA effectiveness.",
                "potential_solutions": [
                    "Rewrite ad copy with stronger hooks and value propositions",
                    "A/B test different headline formulations",
                    "Add social proof or urgency elements",
                    "Improve visual-message alignment"
                ]
            })
        
        # Hypothesis 4: Audience Type Performance
        if by_audience and len(by_audience) > 1:
            audience_roas_values = [(k, v.get('roas', 0)) for k, v in by_audience.items() if isinstance(v, dict)]
            if audience_roas_values:
                best_audience = max(audience_roas_values, key=lambda x: x[1])
                worst_audience = min(audience_roas_values, key=lambda x: x[1])
                
                if best_audience[1] > 1.3 * worst_audience[1]:
                    hypotheses_list.append({
                        "hypothesis_id": "hyp_audience_performance",
                        "hypothesis": f"'{best_audience[0]}' audience type significantly outperforms '{worst_audience[0]}' audience (ROAS: {best_audience[1]:.2f} vs {worst_audience[1]:.2f}).",
                        "category": "audience",
                        "reasoning": "Different audience types have different purchase intent and familiarity with the brand. Lookalike audiences may have higher intent than broad targeting, while retargeting typically performs best due to prior engagement.",
                        "likelihood": 0.80,
                        "potential_impact": "high",
                        "actionability": "high",
                        "evidence_required": [
                            {
                                "metric": "roas_by_audience_type",
                                "comparison": "cross-sectional",
                                "expected_pattern": "Significant ROAS difference across audience types"
                            },
                            {
                                "metric": "conversion_rate",
                                "comparison": "by_audience_type",
                                "expected_pattern": "Higher conversion for better performing audience"
                            }
                        ],
                        "validation_approach": "Compare full funnel metrics (CTR, conversion rate, ROAS) across audience types with statistical significance testing.",
                        "potential_solutions": [
                            f"Increase budget allocation to {best_audience[0]} audience",
                            f"Reduce or pause {worst_audience[0]} audience campaigns",
                            "Create audience-specific creative messaging",
                            "Build more lookalike audiences from best converters"
                        ]
                    })
        
        # Hypothesis 5: Seasonal or External Factors
        hypotheses_list.append({
            "hypothesis_id": "hyp_external_factors",
            "hypothesis": "Performance changes may be influenced by external factors such as seasonality, competitive pressure, or market conditions.",
            "category": "external",
            "reasoning": "Facebook ads performance doesn't occur in a vacuum. Seasonal shopping patterns, competitor campaigns, CPM inflation, and market saturation can all impact results independent of campaign execution.",
            "likelihood": 0.50,
            "potential_impact": "medium",
            "actionability": "low",
            "evidence_required": [
                {
                    "metric": "cpm",
                    "comparison": "time-series",
                    "expected_pattern": "CPM increases during performance decline"
                },
                {
                    "metric": "market_conditions",
                    "comparison": "qualitative",
                    "expected_pattern": "Known seasonal events or competitor activities"
                }
            ],
            "validation_approach": "Check for CPM inflation, review competitive landscape changes, consider calendar events (holidays, sales events).",
            "potential_solutions": [
                "Adjust bidding strategy for competitive periods",
                "Plan campaigns around known seasonal patterns",
                "Differentiate messaging from competitors",
                "Increase creative quality to stand out"
            ]
        })
        
        # Create structured output
        result = {
            "context_summary": {
                "primary_metric": "roas" if 'roas' in str(observations).lower() else "multiple",
                "change_magnitude": self._calculate_change_magnitude(data_summary),
                "time_period": data_summary.get('data_quality', {}).get('date_range', {}).get('start', 'Unknown'),
                "affected_segments": self._identify_affected_segments(data_summary)
            },
            "hypotheses": hypotheses_list,
            "hypothesis_ranking": [],
            "recommended_validation_order": [h["hypothesis_id"] for h in hypotheses_list],
            "confidence": 0.75,
            "reasoning_quality": "Rule-based hypotheses generated from data patterns and marketing science principles"
        }
        
        return result
    
    def _rank_hypotheses(self, hypotheses_data: Dict[str, Any]):
        """Rank hypotheses by priority"""
        hypotheses = hypotheses_data.get('hypotheses', [])
        
        # Calculate composite score for each hypothesis
        ranking = []
        for hyp in hypotheses:
            score = (
                hyp.get('likelihood', 0) * 0.4 +
                (1.0 if hyp.get('potential_impact') == 'high' else 0.5 if hyp.get('potential_impact') == 'medium' else 0.2) * 0.3 +
                (1.0 if hyp.get('actionability') == 'high' else 0.5 if hyp.get('actionability') == 'medium' else 0.2) * 0.3
            )
            
            ranking.append({
                "hypothesis_id": hyp['hypothesis_id'],
                "score": round(score, 3),
                "reasoning": f"Likelihood: {hyp.get('likelihood', 0)}, Impact: {hyp.get('potential_impact')}, Actionability: {hyp.get('actionability')}"
            })
        
        # Sort by score
        ranking.sort(key=lambda x: x['score'], reverse=True)
        
        hypotheses_data['hypothesis_ranking'] = ranking
        hypotheses_data['recommended_validation_order'] = [r['hypothesis_id'] for r in ranking]
    
    def _calculate_change_magnitude(self, data_summary: Dict[str, Any]) -> str:
        """Calculate magnitude of change"""
        # Simple heuristic based on trends
        trends = data_summary.get('trends', {})
        roas_trend = trends.get('roas_trend', 'stable')
        
        if roas_trend == 'decreasing':
            return "-20% (estimated)"
        elif roas_trend == 'increasing':
            return "+15% (estimated)"
        return "stable"
    
    def _identify_affected_segments(self, data_summary: Dict[str, Any]) -> List[str]:
        """Identify which segments are affected"""
        segments = []
        
        # Check bottom performers
        bottom_performers = data_summary.get('bottom_performers', {})
        if bottom_performers.get('by_roas'):
            segments.extend([p['name'] for p in bottom_performers['by_roas'][:3]])
        
        return segments[:5] if segments else ["multiple campaigns"]
