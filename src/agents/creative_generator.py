"""
Creative Generator Agent - Generates new creative recommendations
"""

import json
import random
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent


class CreativeGeneratorAgent(BaseAgent):
    """
    Creative Generator Agent responsible for:
    - Analyzing existing creative performance
    - Generating new creative concepts
    - Providing data-driven recommendations
    - Creating diverse messaging approaches
    """
    
    def __init__(self, config: Dict[str, Any], logger: Any):
        super().__init__("CreativeGenerator", config, logger)
        self.prompt_template = self.load_prompt("creative_generator_prompt")
        
        # Creative frameworks
        self.hook_frameworks = [
            "problem_solution",
            "social_proof",
            "scarcity",
            "curiosity",
            "value_proposition",
            "contrast"
        ]
        
        self.messaging_angles = [
            "comfort",
            "performance",
            "quality",
            "value",
            "social",
            "health"
        ]
    
    def generate_recommendations(
        self,
        validated_hypotheses: List[Dict[str, Any]],
        creative_performance_data: List[Dict[str, Any]],
        campaign_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate creative recommendations based on validated insights
        
        Args:
            validated_hypotheses: Hypotheses validated by Evaluator
            creative_performance_data: Historical creative performance
            campaign_context: Additional campaign context
            
        Returns:
            Creative recommendations with testing strategy
        """
        self.logger.info("Generating creative recommendations")
        
        # Analyze existing creative patterns
        analysis = self._analyze_creative_patterns(creative_performance_data)
        
        # Identify performance issues to address
        issues = self._identify_performance_issues(validated_hypotheses)
        
        # Generate creative concepts
        recommendations = self._generate_creative_concepts(
            analysis,
            issues,
            creative_performance_data,
            campaign_context or {}
        )
        
        # Create testing strategy
        testing_strategy = self._create_testing_strategy(recommendations)
        
        # Package results
        result = {
            "analysis_summary": analysis,
            "creative_recommendations": recommendations,
            "testing_strategy": testing_strategy,
            "alternative_approaches": self._suggest_alternatives()
        }
        
        # Log execution
        self.log_execution("generate_recommendations", result, {
            "num_recommendations": len(recommendations)
        })
        
        return result
    
    def _analyze_creative_patterns(self, creative_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in existing creative performance"""
        if not creative_data:
            return {
                "top_performing_patterns": [],
                "underperforming_patterns": [],
                "key_insights": ["Insufficient creative data for pattern analysis"],
                "recommendation_strategy": "Generate diverse creative approaches based on best practices"
            }
        
        # Sort by ROAS
        sorted_by_roas = sorted(creative_data, key=lambda x: x.get('roas', 0), reverse=True)
        
        top_performers = sorted_by_roas[:5]
        bottom_performers = sorted_by_roas[-5:]
        
        # Extract patterns
        top_patterns = self._extract_patterns(top_performers)
        bottom_patterns = self._extract_patterns(bottom_performers)
        
        # Analyze messaging angles
        top_messages = [c.get('creative_message', '') for c in top_performers]
        
        key_insights = []
        
        # Check creative type performance
        creative_types = {}
        for c in creative_data:
            ctype = c.get('creative_type', 'Unknown')
            if ctype not in creative_types:
                creative_types[ctype] = []
            creative_types[ctype].append(c.get('roas', 0))
        
        avg_by_type = {k: sum(v)/len(v) for k, v in creative_types.items() if v}
        if avg_by_type:
            best_type = max(avg_by_type, key=avg_by_type.get)
            key_insights.append(f"'{best_type}' creative type performs best (avg ROAS: {avg_by_type[best_type]:.2f})")
        
        # Check for common words/themes in top performers
        common_words = self._find_common_words(top_messages)
        if common_words:
            key_insights.append(f"Top performers often mention: {', '.join(common_words[:3])}")
        
        return {
            "top_performing_patterns": top_patterns,
            "underperforming_patterns": bottom_patterns,
            "key_insights": key_insights,
            "recommendation_strategy": "Build on successful patterns while testing new angles"
        }
    
    def _extract_patterns(self, creatives: List[Dict[str, Any]]) -> List[str]:
        """Extract common patterns from creatives"""
        patterns = []
        
        for c in creatives:
            message = c.get('creative_message', '')
            ctype = c.get('creative_type', '')
            
            # Pattern: Creative type
            patterns.append(f"{ctype} format")
            
            # Pattern: Message themes
            if 'guarantee' in message.lower() or 'guaranteed' in message.lower():
                patterns.append("Guarantee/warranty messaging")
            if '—' in message or ':' in message:
                patterns.append("Problem-solution structure")
            if 'limited' in message.lower() or 'stock' in message.lower():
                patterns.append("Scarcity/urgency")
            if 'cooling' in message.lower() or 'breathable' in message.lower():
                patterns.append("Performance/comfort benefits")
        
        # Return unique patterns
        return list(set(patterns))[:5]
    
    def _find_common_words(self, messages: List[str]) -> List[str]:
        """Find common words in messages"""
        if not messages:
            return []
        
        # Common meaningful words (excluding stopwords)
        word_freq = {}
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        for message in messages:
            words = message.lower().split()
            for word in words:
                word = word.strip('.,!?—')
                if len(word) > 3 and word not in stopwords:
                    word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top words
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words if freq >= 2][:5]
    
    def _identify_performance_issues(self, hypotheses: List[Dict[str, Any]]) -> List[str]:
        """Identify key performance issues from validated hypotheses"""
        issues = []
        
        for hyp in hypotheses:
            if hyp.get('evaluation_result') in ['SUPPORTED', 'LIKELY']:
                category = hyp.get('category', '')
                
                if category == 'creative':
                    issues.append('creative_underperformance')
                elif category == 'audience':
                    issues.append('audience_fatigue')
                
                # Check CTR
                if 'ctr' in hyp.get('hypothesis_statement', '').lower():
                    issues.append('low_ctr')
        
        return list(set(issues))
    
    def _generate_creative_concepts(
        self,
        analysis: Dict[str, Any],
        issues: List[str],
        creative_data: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate diverse creative concepts"""
        recommendations = []
        
        # Get top performers for inspiration
        top_performers = sorted(creative_data, key=lambda x: x.get('roas', 0), reverse=True)[:3] if creative_data else []
        
        # Generate concepts for each messaging angle
        max_suggestions = self.config.get('agents', {}).get('creative_generator', {}).get('max_suggestions', 5)
        
        # Template-based generation (in production, would use LLM)
        concepts = [
            {
                "angle": "comfort",
                "hook": "No more discomfort",
                "body": "All-day comfort with premium organic cotton",
                "cta": "Experience the difference",
                "creative_type": "Image"
            },
            {
                "angle": "performance",
                "hook": "Stay cool. Stay focused.",
                "body": "Advanced moisture-wicking technology for peak performance",
                "cta": "Shop performance collection",
                "creative_type": "Video"
            },
            {
                "angle": "social_proof",
                "hook": "Join 50,000+ satisfied customers",
                "body": "Rated 4.8/5 stars — the underwear men actually recommend",
                "cta": "See why they switched",
                "creative_type": "UGC"
            },
            {
                "angle": "value",
                "hook": "Premium quality. Honest price.",
                "body": "No retail markup. Just exceptional underwear delivered to your door.",
                "cta": "Shop now — Free shipping",
                "creative_type": "Image"
            },
            {
                "angle": "problem_solution",
                "hook": "Tired of ride-up?",
                "body": "Our stay-put design finally solves it. Guaranteed.",
                "cta": "Try risk-free",
                "creative_type": "Video"
            }
        ]
        
        # Select and customize concepts
        for i, concept in enumerate(concepts[:max_suggestions]):
            # Determine target based on issues
            target_campaign = "Men_ComfortMax_Launch"  # Default
            target_audience = "Broad"
            
            if 'audience_fatigue' in issues:
                target_audience = "Lookalike"
            
            # Build creative message
            message = f"{concept['hook']} {concept['body']} {concept['cta']}"
            
            # Add inspired by reference if available
            inspired_by = []
            if top_performers:
                inspired_by = [top_performers[0].get('creative_message', '')]
            
            # Determine priority
            priority = "high" if i < 2 else "medium" if i < 4 else "low"
            
            recommendation = {
                "recommendation_id": f"rec_{i+1}",
                "creative_type": concept['creative_type'],
                "target_campaign": target_campaign,
                "target_audience": target_audience,
                "creative_message": message,
                "headline": concept['hook'],
                "body": concept['body'],
                "cta": concept['cta'],
                "messaging_angle": concept['angle'],
                "hook_type": self._infer_hook_type(concept['hook']),
                "rationale": self._generate_rationale(concept, analysis, issues),
                "inspired_by": inspired_by,
                "expected_improvement": self._estimate_improvement(concept, issues),
                "testing_priority": priority,
                "confidence": self._estimate_confidence(concept, analysis)
            }
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _infer_hook_type(self, hook: str) -> str:
        """Infer hook type from the headline"""
        hook_lower = hook.lower()
        
        if 'join' in hook_lower or 'customers' in hook_lower:
            return "social_proof"
        elif 'tired' in hook_lower or '?' in hook:
            return "problem_solution"
        elif 'premium' in hook_lower or 'quality' in hook_lower:
            return "value_proposition"
        elif 'limited' in hook_lower or 'now' in hook_lower:
            return "scarcity"
        else:
            return "benefit_focused"
    
    def _generate_rationale(self, concept: Dict[str, Any], analysis: Dict[str, Any], issues: List[str]) -> str:
        """Generate rationale for the creative recommendation"""
        angle = concept['angle']
        ctype = concept['creative_type']
        
        rationale_parts = []
        
        # Address specific issues
        if 'low_ctr' in issues:
            rationale_parts.append(f"Strong hook '{concept['hook']}' designed to improve CTR")
        
        if 'creative_underperformance' in issues:
            rationale_parts.append(f"{ctype} format with {angle} messaging angle to refresh creative approach")
        
        # Reference analysis insights
        insights = analysis.get('key_insights', [])
        if insights:
            rationale_parts.append(f"Builds on insight: {insights[0][:60]}")
        
        if not rationale_parts:
            rationale_parts.append(f"Tests {angle} messaging angle with {ctype} format to optimize engagement")
        
        return ". ".join(rationale_parts) + "."
    
    def _estimate_improvement(self, concept: Dict[str, Any], issues: List[str]) -> str:
        """Estimate expected improvement"""
        if 'low_ctr' in issues:
            return "Expected CTR improvement of 15-25% through stronger hooks and benefit-focused messaging"
        elif 'creative_underperformance' in issues:
            return "Expected ROAS improvement of 10-20% by testing fresh creative approach"
        elif 'audience_fatigue' in issues:
            return "Expected engagement recovery of 20-30% with new creative in fatigued segments"
        
        return "Expected incremental performance improvement through creative testing and optimization"
    
    def _estimate_confidence(self, concept: Dict[str, Any], analysis: Dict[str, Any]) -> float:
        """Estimate confidence in recommendation"""
        confidence = 0.65  # Base confidence
        
        # Increase if aligns with top patterns
        top_patterns = analysis.get('top_performing_patterns', [])
        if any(concept['creative_type'] in p for p in top_patterns):
            confidence += 0.15
        
        # Increase for proven messaging angles
        if concept['angle'] in ['performance', 'comfort', 'social_proof']:
            confidence += 0.10
        
        return min(round(confidence, 2), 0.95)
    
    def _create_testing_strategy(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create testing strategy for recommendations"""
        
        # Order by priority
        high_priority = [r for r in recommendations if r['testing_priority'] == 'high']
        medium_priority = [r for r in recommendations if r['testing_priority'] == 'medium']
        
        # Budget allocation (weighted by priority)
        budget_allocation = {}
        total_weight = len(high_priority) * 2 + len(medium_priority)
        
        for rec in high_priority:
            budget_allocation[rec['recommendation_id']] = f"{(2 / total_weight * 100):.0f}%"
        
        for rec in medium_priority:
            budget_allocation[rec['recommendation_id']] = f"{(1 / total_weight * 100):.0f}%"
        
        return {
            "recommended_test_order": [r['recommendation_id'] for r in recommendations],
            "budget_allocation": budget_allocation,
            "success_metrics": [
                "CTR improvement (target: +15%)",
                "ROAS improvement (target: +10%)",
                "Cost per purchase (target: -10%)"
            ],
            "test_duration": "7-14 days minimum per creative variant for statistical significance",
            "testing_methodology": "Sequential A/B testing with holdout control group"
        }
    
    def _suggest_alternatives(self) -> List[Dict[str, Any]]:
        """Suggest alternative approaches"""
        return [
            {
                "approach": "Dynamic Creative Optimization (DCO)",
                "description": "Use Facebook's DCO to automatically test combinations of headlines, images, and CTAs",
                "when_to_use": "When you have multiple creative assets and want platform to optimize combinations"
            },
            {
                "approach": "Iterative creative refresh",
                "description": "Update creatives every 10-14 days to prevent fatigue",
                "when_to_use": "For long-running campaigns with consistent audience"
            },
            {
                "approach": "Audience-specific creative",
                "description": "Create unique creative messaging for each audience segment",
                "when_to_use": "When audience segments show significantly different behaviors"
            }
        ]
