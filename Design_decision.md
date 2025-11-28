# Design Decisions & Tradeoffs

## Overview
This document explains key architectural decisions made in building the Kasparro Agentic FB Analyst.

---

## 1. Multi-Agent Architecture

### Decision: 5 Specialized Agents vs Monolithic System

**Chosen Approach:** 5 specialized agents (Planner, Data, Insight, Evaluator, Creative)

**Rationale:**
- **Separation of concerns**: Each agent has a single, well-defined responsibility
- **Maintainability**: Changes to statistical methods don't affect creative generation
- **Testability**: Can unit test each agent independently
- **Scalability**: Easy to parallelize or replace individual agents

**Tradeoff:**
- More complex orchestration logic
- Increased inter-agent communication overhead
- **Accepted because**: Clarity and maintainability outweigh coordination complexity

---

## 2. Mock LLM vs Real API Integration

### Decision: Mock LLM responses with rule-based fallbacks

**Rationale:**
- Assignment focus is on **agentic reasoning architecture**, not LLM integration
- Allows testing without API keys or costs
- Demonstrates understanding of prompt engineering through structured templates
- Rule-based logic proves agents can reason without LLM calls

**Production Path:**
```python
# Easy to swap in real LLM:
def call_llm(self, prompt: str) -> str:
    import openai
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
```

---

## 3. Statistical Validation Approach

### Decision: Scipy-based statistical tests (t-tests, ANOVA, regression)

**Chosen Tests:**
- Independent t-test (2 groups)
- One-way ANOVA (3+ groups)
- Linear regression (time trends)
- Cohen's d (effect sizes)

**Rationale:**
- Industry-standard methods for A/B testing and performance analysis
- Provides quantitative confidence scores
- Handles multiple comparison scenarios
- Effect sizes prevent misleading significance with large samples

**Alternative Considered:** Bayesian inference
**Why Not:** More complex, harder to interpret for marketing teams

---

## 4. Configuration Management

### Decision: YAML config + environment variable overrides

**Rationale:**
- Human-readable configuration
- Easy to adjust thresholds without code changes
- Environment variables support CI/CD deployments
- Versioned config enables reproducibility

**Example:**
```yaml
thresholds:
  roas_drop_threshold: 0.15  # Easy to tune
  ctr_low_threshold: 0.015
```

---

## 5. Prompt Engineering Strategy

### Decision: Structured prompts with Think→Analyze→Conclude framework

**Structure:**
1. **Role definition**: "You are an expert Marketing Analyst..."
2. **Input specification**: Clear variable placeholders
3. **Reasoning steps**: Multi-step thinking process
4. **Output format**: JSON schema with examples
5. **Quality checks**: Self-validation criteria

**Rationale:**
- Structured prompts reduce hallucination
- Step-by-step reasoning improves output quality
- JSON output enables programmatic processing
- Examples ground the model's responses

---

## 6. Error Handling Philosophy

### Decision: Graceful degradation with comprehensive logging

**Approach:**
- Try-except blocks at every agent method
- Fallback to default plans if LLM fails
- Detailed error logging for debugging
- Never crash - always return partial results

**Example:**
```python
try:
    hypotheses = self.generate_hypotheses(...)
except Exception as e:
    self.logger.error(f"Hypothesis generation failed: {e}")
    hypotheses = self._create_default_hypotheses()
```

**Tradeoff:**
- More verbose code
- **Accepted because**: Production systems must be resilient

---

## 7. Data Processing Strategy

### Decision: Pandas for data manipulation, not SQL database

**Rationale:**
- CSV input format specified in assignment
- Pandas sufficient for 4,500 rows (< 1MB)
- No need for database overhead for this scale
- Easier to deploy (no DB setup required)

**When to Switch to DB:**
- Data > 1GB
- Multiple concurrent users
- Real-time updates required

---

## 8. Testing Strategy

### Decision: Unit tests for Evaluator, integration tests via orchestrator

**Coverage Focus:**
- Statistical calculations (Cohen's d, t-tests)
- Edge cases (NaN values, empty data)
- Confidence scoring logic

**Why Focus on Evaluator:**
- Most critical for accuracy
- Statistical bugs are silent failures
- Math errors propagate to recommendations

**Future Testing:**
- Add integration tests for full workflow
- Snapshot testing for report outputs
- Property-based testing for statistical methods

---

## 9. Observability Design

### Decision: Dual logging (colored console + JSON files)

**Console:** Human-readable progress for developers
**JSON Logs:** Machine-readable for analysis/debugging

**Rationale:**
- Developers need real-time feedback
- JSON logs enable automated monitoring
- Per-agent logs simplify debugging
- Structured data supports log aggregation

---

## 10. Creative Generation Approach

### Decision: Template-based with data-driven customization

**Current Implementation:**
- 5 messaging angle templates (comfort, performance, value, social, health)
- 6 hook frameworks (problem-solution, social proof, scarcity, etc.)
- Recommendations grounded in top performer analysis

**Why Templates:**
- Deterministic outputs for testing
- Demonstrates understanding of copywriting frameworks
- Easy to swap in LLM-based generation later

**Production Enhancement:**
```python
# LLM-powered creative generation
def _generate_with_llm(self, top_performers, issues):
    prompt = f"Generate 5 ad concepts based on these top performers: {top_performers}"
    return self.call_llm(prompt)
```

---

## Key Tradeoffs Summary

| Decision | Benefit | Cost | Verdict |
|----------|---------|------|---------|
| Multi-agent architecture | Modularity, testability | Coordination overhead | ✅ Worth it |
| Mock LLM | No API costs, testable | Less realistic | ✅ Acceptable |
| Pandas vs DB | Simplicity | Scalability limit | ✅ Right for scale |
| Statistical rigor | Confidence in results | Complexity | ✅ Essential |
| Comprehensive logging | Debuggability | Verbose code | ✅ Production need |

---

## Future Enhancements

1. **Memory System**: Store insights across runs in SQLite
2. **Real LLM Integration**: OpenAI/Anthropic API calls
3. **Parallel Evaluation**: Test hypotheses concurrently
4. **Interactive Mode**: User can guide analysis mid-execution
5. **Visualization**: Plotly dashboards for reports

---

**Author:** [Your Name]  
**Date:** 2025-11-28  
**Version:** 1.0
