# Agent Architecture & Data Flow

## Overview

The Kasparro Agentic FB Analyst is a sophisticated multi-agent system designed for autonomous Facebook Ads performance analysis. The system follows a structured workflow where specialized agents collaborate to deliver comprehensive insights and actionable recommendations.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER QUERY                               │
│                    "Analyze ROAS drop"                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR                                │
│  • Coordinates agent workflow                                    │
│  • Manages execution state                                       │
│  • Handles error recovery                                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
        ┌────────────────────┴────────────────────┐
        │                                          │
        ▼                                          ▼
┌──────────────────┐                    ┌──────────────────┐
│ PLANNER AGENT    │                    │   DATA AGENT     │
│                  │                    │                  │
│ • Decomposes     │───────────────────▶│ • Loads CSV      │
│   query          │   Dataset Info     │ • Cleans data    │
│ • Creates plan   │                    │ • Computes stats │
│ • Manages deps   │                    │ • Identifies     │
│                  │                    │   patterns       │
└──────────────────┘                    └─────────┬────────┘
        │                                          │
        │                                    Data Summary
        │                                          │
        │         ┌────────────────────────────────┘
        │         │
        ▼         ▼
┌──────────────────────────────────────┐
│        INSIGHT AGENT                  │
│                                       │
│ • Generates hypotheses                │
│ • Explains ROAS patterns              │
│ • Identifies drivers                  │
│ • Ranks by likelihood                 │
└─────────────────┬─────────────────────┘
                  │
            Hypotheses
                  │
                  ▼
┌──────────────────────────────────────┐
│       EVALUATOR AGENT                 │
│                                       │
│ • Tests hypotheses statistically      │
│ • Performs t-tests, ANOVA             │
│ • Calculates effect sizes             │
│ • Assigns confidence scores           │
│ • Validates with data                 │
└─────────────────┬─────────────────────┘
                  │
        Validated Insights
                  │
                  ▼
┌──────────────────────────────────────┐
│    CREATIVE GENERATOR AGENT           │
│                                       │
│ • Analyzes top performers             │
│ • Generates new concepts              │
│ • Creates testing strategy            │
│ • Provides recommendations            │
└─────────────────┬─────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│           OUTPUT GENERATION             │
│                                         │
│ • reports/report.md                     │
│ • reports/insights.json                 │
│ • reports/creatives.json                │
│ • logs/*.log                            │
└─────────────────────────────────────────┘
```

## Agent Roles & Responsibilities

### 1. Planner Agent
**Purpose**: Strategic query decomposition and workflow orchestration

**Inputs**:
- User query (natural language)
- Dataset schema and metadata

**Outputs**:
- Structured execution plan
- Task dependencies
- Expected insights

**Key Capabilities**:
- Query understanding and intent recognition
- Task decomposition into atomic subtasks
- Dependency management
- Adaptive planning based on intermediate results

**Prompt Structure**:
```
UNDERSTAND → DECOMPOSE → SEQUENCE → SPECIFY
```

### 2. Data Agent
**Purpose**: Data loading, cleaning, and statistical analysis

**Inputs**:
- CSV file path
- Analysis parameters (time periods, metrics)

**Outputs**:
- Data quality report
- Summary statistics (overall, by campaign, by creative, by audience)
- Trend analysis
- Top/bottom performers
- Key observations

**Key Capabilities**:
- Robust data cleaning (missing values, outliers)
- Multi-dimensional aggregations
- Time-series trend detection
- Anomaly identification
- Performance segmentation

**Data Structures**:
```python
{
  "data_quality": {
    "total_rows": int,
    "date_range": {"start": str, "end": str},
    "missing_values": dict,
    "anomalies": list
  },
  "summary_statistics": {
    "overall": {...},
    "by_campaign": [...],
    "by_creative_type": {...},
    "by_audience_type": {...}
  },
  "trends": {...},
  "top_performers": {...},
  "bottom_performers": {...}
}
```

### 3. Insight Agent
**Purpose**: Hypothesis generation and causal reasoning

**Inputs**:
- Data summary from Data Agent
- Key observations
- Historical context (optional, for memory)

**Outputs**:
- 3-7 data-driven hypotheses
- Evidence requirements for each
- Likelihood scores
- Potential solutions

**Key Capabilities**:
- Pattern recognition in performance data
- Causal reasoning frameworks:
  - Audience fatigue detection
  - Creative performance analysis
  - Competitive factors
  - Technical issues
  - External factors
- Hypothesis prioritization
- Solution recommendation

**Hypothesis Categories**:
- Audience (fatigue, saturation, quality)
- Creative (fatigue, underperformance, format effectiveness)
- Competitive (CPM inflation, market saturation)
- Technical (budget pacing, bid strategy)
- External (seasonality, market conditions)

### 4. Evaluator Agent
**Purpose**: Quantitative hypothesis validation with statistical rigor

**Inputs**:
- Hypotheses from Insight Agent
- Raw data access from Data Agent
- Data summary statistics

**Outputs**:
- Validation results (SUPPORTED/LIKELY/INCONCLUSIVE/UNLIKELY/REFUTED)
- Statistical test results (p-values, effect sizes)
- Confidence scores (0.0-1.0)
- Recommendations

**Key Capabilities**:
- Statistical testing:
  - Independent t-tests (2 groups)
  - One-way ANOVA (3+ groups)
  - One-sample tests (vs benchmarks)
  - Linear regression (trends)
  - Correlation analysis
- Effect size calculations (Cohen's d)
- Multiple comparison handling
- Confidence score computation

**Statistical Thresholds**:
```
Significance: p < 0.05
Effect Sizes (Cohen's d):
  - Large: d >= 0.8
  - Medium: 0.5 <= d < 0.8
  - Small: 0.2 <= d < 0.5
  - Negligible: d < 0.2

Confidence Levels:
  - SUPPORTED: >= 0.7
  - LIKELY: 0.5-0.7
  - INCONCLUSIVE: 0.3-0.5
  - UNLIKELY: 0.1-0.3
  - REFUTED: < 0.1
```

### 5. Creative Generator Agent
**Purpose**: Data-driven creative recommendation generation

**Inputs**:
- Validated hypotheses from Evaluator
- Creative performance data from Data Agent
- Campaign context

**Outputs**:
- 3-5 creative recommendations
- Testing strategy
- Budget allocation
- Success metrics

**Key Capabilities**:
- Creative pattern analysis
- Top performer identification
- Messaging angle selection:
  - Comfort & Feel
  - Performance (no ride-up, stays in place)
  - Quality (organic, premium)
  - Value (price, durability)
  - Social (style, confidence)
  - Health (skin-friendly)
- Hook framework application:
  - Problem-Solution
  - Social Proof
  - Scarcity
  - Curiosity
  - Value Proposition
  - Contrast
- A/B testing strategy design

## Data Flow

### Flow Diagram

```
User Query
    ↓
[Planner] Creates Plan
    ↓
[Data Agent] Loads Data ──→ dataset.csv
    ↓
[Data Agent] Analyzes ──→ data_summary.json
    ↓
[Insight Agent] Generates ──→ hypotheses.json
    ↓
[Evaluator] Validates ──→ validated_hypotheses.json
    ↓
[Creative Gen] Recommends ──→ creatives.json
    ↓
[Orchestrator] Generates:
    • reports/report.md
    • reports/insights.json
    • reports/creatives.json
    • logs/*.jsonl
```

### Data Formats

#### Task Structure (Planner Output)
```json
{
  "task_id": "task_1",
  "task_name": "Load and analyze data",
  "agent": "data_agent",
  "description": "Load dataset and calculate summary statistics",
  "inputs": ["full_dataset"],
  "outputs": ["data_summary"],
  "dependencies": [],
  "priority": "high"
}
```

#### Hypothesis Structure (Insight Agent Output)
```json
{
  "hypothesis_id": "hyp_1",
  "hypothesis": "Audience fatigue caused CTR decline",
  "category": "audience",
  "reasoning": "Declining engagement after extended exposure",
  "likelihood": 0.75,
  "potential_impact": "high",
  "actionability": "high",
  "evidence_required": [
    {
      "metric": "frequency",
      "comparison": "week-over-week",
      "expected_pattern": "increasing frequency with decreasing CTR"
    }
  ],
  "validation_approach": "Compare early vs late campaign performance",
  "potential_solutions": ["Refresh creative", "Expand audience"]
}
```

#### Evaluation Result (Evaluator Output)
```json
{
  "hypothesis_id": "hyp_1",
  "evaluation_result": "SUPPORTED",
  "confidence_score": 0.85,
  "evidence_analysis": {
    "statistical_tests_performed": [...],
    "key_findings": [...],
    "contradicting_evidence": []
  },
  "quantitative_support": {
    "primary_metric_change": "-25%",
    "statistical_significance": "yes",
    "effect_size_rating": "large"
  },
  "recommendation": "Strong evidence supports this hypothesis..."
}
```

#### Creative Recommendation (Creative Generator Output)
```json
{
  "recommendation_id": "rec_1",
  "creative_type": "Video",
  "creative_message": "No more ride-up. Guaranteed comfort...",
  "headline": "No more ride-up",
  "body": "Guaranteed comfort all day with stay-put technology",
  "cta": "Try risk-free",
  "messaging_angle": "performance",
  "hook_type": "problem_solution",
  "rationale": "Strong hook designed to improve CTR...",
  "expected_improvement": "Expected CTR improvement of 15-25%",
  "testing_priority": "high",
  "confidence": 0.85
}
```

## Execution Flow

### Step-by-Step Process

1. **Initialization**
   ```
   User provides query → Orchestrator loads config → Agents initialized
   ```

2. **Planning Phase**
   ```
   Planner receives query + dataset info
   → Analyzes intent
   → Decomposes into tasks
   → Creates execution plan with dependencies
   ```

3. **Data Phase**
   ```
   Data Agent loads CSV
   → Cleans data (missing values, outliers)
   → Computes aggregations
   → Identifies trends
   → Returns data_summary
   ```

4. **Insight Phase**
   ```
   Insight Agent receives data_summary
   → Generates 3-7 hypotheses
   → Ranks by likelihood × impact × actionability
   → Specifies evidence requirements
   → Returns hypotheses
   ```

5. **Evaluation Phase**
   ```
   Evaluator receives hypotheses
   → For each hypothesis:
       → Performs statistical tests
       → Calculates effect sizes
       → Assigns confidence score
       → Determines SUPPORTED/LIKELY/INCONCLUSIVE/UNLIKELY/REFUTED
   → Returns validated_hypotheses
   ```

6. **Creative Phase**
   ```
   Creative Generator receives validated_hypotheses + creative_data
   → Analyzes top performers
   → Generates 3-5 creative concepts
   → Creates testing strategy
   → Returns creatives
   ```

7. **Output Phase**
   ```
   Orchestrator compiles all results
   → Generates report.md (human-readable)
   → Generates insights.json (structured data)
   → Generates creatives.json (recommendations)
   → Saves logs
   ```

## Inter-Agent Communication

### Message Passing Pattern

```python
# Orchestrator manages state
execution_state = {
    "data_summary": None,
    "hypotheses": None,
    "validated_hypotheses": None,
    "creative_recommendations": None
}

# Sequential execution with state updates
data_summary = data_agent.analyze_data(...)
execution_state['data_summary'] = data_summary

hypotheses = insight_agent.generate_hypotheses(data_summary, ...)
execution_state['hypotheses'] = hypotheses

validated = evaluator.evaluate_all(hypotheses, data_summary)
execution_state['validated_hypotheses'] = validated

creatives = creative_generator.generate(validated, ...)
execution_state['creative_recommendations'] = creatives
```

### Error Handling & Recovery

- **Retry Logic**: Agents can retry with reflection on low confidence
- **Graceful Degradation**: System continues even if one agent fails
- **Fallback Strategies**: Default plans and rule-based backups
- **Comprehensive Logging**: All decisions logged for debugging

## Configuration & Customization

### Agent Configuration

```yaml
agents:
  planner:
    model: "gpt-4"
    temperature: 0.3
  data_agent:
    model: "gpt-4"
    temperature: 0.1
  insight_agent:
    model: "gpt-4"
    temperature: 0.5
  evaluator:
    model: "gpt-4"
    temperature: 0.2
  creative_generator:
    model: "gpt-4"
    temperature: 0.8
    max_suggestions: 5
```

### Thresholds

```yaml
thresholds:
  roas_drop_threshold: 0.15    # 15%
  ctr_low_threshold: 0.015     # 1.5%
  spend_significance: 100      # $100 minimum
  fatigue_days: 14             # 14 days
```

## Observability

### Logging Strategy

- **Structured JSON logs**: Machine-readable, searchable
- **Per-agent log files**: Isolated debugging
- **Colored console output**: Human-readable progress
- **Metadata tracking**: Timestamps, confidence, token usage

### Log Locations

```
logs/
├── orchestrator.log        # Main workflow
├── planner.log            # Planning decisions
├── dataagent.log          # Data operations
├── insightagent.log       # Hypotheses generation
├── evaluator.log          # Statistical tests
└── creativegenerator.log  # Creative recommendations
```

## Performance Considerations

### Computational Complexity

- **Data Agent**: O(n) for basic stats, O(n log n) for sorting
- **Insight Agent**: O(1) rule-based, O(n) with LLM
- **Evaluator**: O(n) for most tests, O(n²) for some comparisons
- **Creative Generator**: O(1) template-based, O(n) with LLM

### Optimization Strategies

1. **Early Data Filtering**: Filter by time period before analysis
2. **Caching**: Cache expensive computations
3. **Batch Processing**: Process multiple hypotheses in parallel
4. **Sample Data**: Use sample for development/testing

## Future Architecture Enhancements

1. **Memory System**: Persist insights across sessions
2. **Real-time Updates**: Stream data for live monitoring
3. **Parallel Evaluation**: Test hypotheses concurrently
4. **Feedback Loop**: Learn from user feedback on recommendations
5. **Multi-Platform**: Extend beyond Facebook to Google, LinkedIn
6. **Interactive Mode**: Allow user to guide analysis interactively

---

**Architecture Version**: 1.0  
**Last Updated**: 2025-11-28
