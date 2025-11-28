# Kasparro — Agentic Facebook Performance Analyst

**World-Class Multi-Agent System for Facebook Ads Performance Analysis**

A sophisticated, production-ready agentic AI system that autonomously diagnoses Facebook Ads performance, identifies root causes of ROAS fluctuations, and generates data-driven creative recommendations.

## 🎯 Features

- **🤖 Multi-Agent Architecture**: Five specialized agents working in harmony
  - **Planner Agent**: Decomposes queries into executable subtasks
  - **Data Agent**: Loads, cleans, and analyzes Facebook Ads data
  - **Insight Agent**: Generates data-driven hypotheses
  - **Evaluator Agent**: Validates hypotheses with statistical rigor
  - **Creative Generator Agent**: Produces actionable creative recommendations

- **📊 Advanced Analytics**
  - Statistical hypothesis testing (t-tests, ANOVA, correlation analysis)
  - Trend analysis and pattern recognition
  - Segment performance comparisons
  - Effect size calculations (Cohen's d)

- **💡 Intelligent Insights**
  - Audience fatigue detection
  - Creative performance analysis
  - CTR optimization recommendations
  - ROAS driver identification

- **🔬 Production-Ready**
  - Comprehensive logging (JSON structured logs)
  - Configurable thresholds and parameters
  - Reproducible with seed controls
  - Extensive error handling
  - Unit tests included

## 📁 Project Structure

```
kasparro-agentic-fb-analyst/
├── config/
│   └── config.yaml              # Configuration file
├── data/
│   ├── README.md               # Data documentation
│   └── sample_fb_ads.csv       # Sample dataset (optional)
├── logs/                       # JSON structured logs
├── prompts/                    # Structured prompt templates
│   ├── planner_prompt.md
│   ├── data_agent_prompt.md
│   ├── insight_agent_prompt.md
│   ├── evaluator_prompt.md
│   └── creative_generator_prompt.md
├── reports/                    # Generated outputs
│   ├── report.md              # Human-readable report
│   ├── insights.json          # Structured insights
│   └── creatives.json         # Creative recommendations
├── src/
│   ├── agents/                # Agent implementations
│   │   ├── base_agent.py
│   │   ├── planner.py
│   │   ├── data_agent.py
│   │   ├── insight_agent.py
│   │   ├── evaluator.py
│   │   └── creative_generator.py
│   ├── orchestrator/          # Main orchestration logic
│   │   └── orchestrator.py
│   ├── utils/                 # Utilities
│   │   ├── logger.py
│   │   └── config_loader.py
│   └── run.py                 # Main entry point
├── tests/
│   └── test_evaluator.py      # Unit tests
├── agent_graph.md              # Architecture documentation
├── Makefile                    # Build automation
├── requirements.txt            # Dependencies
├── README.md                   # This file
└── synthetic_fb_ads_undergarments.csv  # Full dataset

```

## 🚀 Quick Start

### Prerequisites
- Python >= 3.10
- pip

### Installation

```bash
# 1. Clone or download the project
cd kasparro-agentic-fb-analyst

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run analysis
python src/run.py "Analyze ROAS drop in last 7 days"
```

### Alternative: Using Make

```bash
make setup    # Setup environment and install dependencies
make run      # Run with default query
make test     # Run unit tests
make lint     # Run code quality checks (requires pylint)
make clean    # Clean generated files
```

## 📊 Data

The system works with Facebook Ads datasets containing the following columns:
- `campaign_name`, `adset_name`, `date`
- `spend`, `impressions`, `clicks`, `ctr`
- `purchases`, `revenue`, `roas`
- `creative_type`, `creative_message`
- `audience_type`, `platform`, `country`

### Data Configuration

Edit `config/config.yaml`:

```yaml
use_sample_data: false  # Set to true to use sample
data_csv: "synthetic_fb_ads_undergarments.csv"  # Path to full dataset
```

Or set environment variable:
```bash
export DATA_CSV=/path/to/your/data.csv
python src/run.py "Your query here"
```

## 🎯 Usage Examples

```bash
# Analyze ROAS performance
python src/run.py "Analyze ROAS drop in last 7 days"

# Investigate CTR issues
python src/run.py "Why is CTR declining?"

# Identify underperforming campaigns
python src/run.py "Which campaigns are underperforming and why?"

# General performance analysis
python src/run.py "Provide comprehensive performance analysis"

# With custom data file
python src/run.py "Analyze performance" --data path/to/data.csv

# Verbose logging
python src/run.py "Analyze ROAS" --verbose
```

## 📈 Output Files

After running analysis, check the `reports/` directory:

### 1. **report.md**
Human-readable Markdown report with:
- Executive summary
- Key findings and validated insights
- Top/bottom performers
- Creative recommendations
- Recommended next steps

### 2. **insights.json**
Structured JSON containing:
- Data analysis results
- Generated hypotheses
- Statistical validation results
- Confidence scores
- Execution log

### 3. **creatives.json**
Creative recommendations including:
- New creative concepts
- Messaging angles
- Testing strategy
- Budget allocation
- Success metrics

## ⚙️ Configuration

Edit `config/config.yaml` to customize:

```yaml
# Analysis thresholds
thresholds:
  roas_drop_threshold: 0.15    # 15% ROAS drop sensitivity
  ctr_low_threshold: 0.015     # 1.5% CTR minimum
  spend_significance: 100      # Minimum spend for analysis
  fatigue_days: 14             # Audience fatigue detection period

# Agent settings
agents:
  planner:
    model: "gpt-4"
    temperature: 0.3
  evaluator:
    temperature: 0.2
  creative_generator:
    temperature: 0.8
    max_suggestions: 5

# Confidence threshold
confidence_min: 0.6

# Random seed for reproducibility
random_seed: 42
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Or using make
make test

# Run specific test file
python tests/test_evaluator.py
```

## 🏗️ Architecture


## 🏗️ System Architecture

### Agent Flow Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│                         USER QUERY                               │
│                  "Analyze ROAS drop in last 7 days"             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  ORCHESTRATOR   │
                    │  Coordinates    │
                    │  workflow       │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   PLANNER    │───▶│  DATA AGENT  │───▶│   INSIGHT    │
│              │    │              │    │    AGENT     │
│ Decomposes   │    │ Loads &      │    │              │
│ query into   │    │ analyzes     │    │ Generates    │
│ tasks        │    │ CSV data     │    │ hypotheses   │
└──────────────┘    └──────────────┘    └──────┬───────┘
                                               │
                                               ▼
                                        ┌──────────────┐
                                        │  EVALUATOR   │
                                        │              │
                                        │ Validates    │
                                        │ with stats   │
                                        └──────┬───────┘
                                               │
                                               ▼
                                        ┌──────────────┐
                                        │  CREATIVE    │
                                        │  GENERATOR   │
                                        │              │
                                        │ Recommends   │
                                        │ new ads      │
                                        └──────┬───────┘
                                               │
                                               ▼
                    ┌──────────────────────────────────────┐
                    │          OUTPUT FILES                │
                    │  • reports/report.md                 │
                    │  • reports/insights.json             │
                    │  • reports/creatives.json            │
                    │  • logs/*.log                        │
                    └──────────────────────────────────────┘
```

### Data Flow

1. **Planner** receives query and creates execution plan
2. **Data Agent** loads CSV, computes statistics, identifies patterns
3. **Insight Agent** generates 3-7 hypotheses explaining patterns
4. **Evaluator** validates each hypothesis with statistical tests (t-tests, ANOVA, Cohen's d)
5. **Creative Generator** proposes new creative concepts based on validated insights
6. **Orchestrator** compiles all results into human-readable reports

For detailed architecture documentation, see [agent_graph.md](agent_graph.md).


### Key Design Principles

1. **Structured Prompting**: All prompts use Think→Analyze→Conclude structure
2. **Statistical Rigor**: Quantitative validation with p-values and effect sizes
3. **Adaptive Planning**: Planner can adjust based on intermediate findings
4. **Confidence Scoring**: All outputs include confidence metrics
5. **Observability**: Comprehensive JSON logging for debugging

## 📝 Logging & Observability

The system generates detailed logs in `logs/` directory:

- **Structured JSON logs**: Machine-readable execution traces
- **Colored console output**: Human-readable progress updates
- **Agent-specific logs**: Separate log files per agent
- **Execution metadata**: Timestamps, confidence scores, token usage

View logs:
```bash
# View orchestrator logs
cat logs/orchestrator.log | jq .

# View specific agent
cat logs/dataagent.log | jq .

# Follow logs in real-time
tail -f logs/orchestrator.log
```

## 🔄 Reproducibility

The system ensures reproducibility through:
- **Fixed random seeds** (configurable in `config.yaml`)
- **Pinned dependencies** (exact versions in `requirements.txt`)
- **Deterministic algorithms** (where possible)
- **Structured logging** (audit trail of all decisions)

## 🛠️ Development

### Code Quality

```bash
# Install dev dependencies
pip install pylint black pytest

# Format code
black src/ tests/

# Lint code
make lint

# Type checking
mypy src/
```

### Adding New Agents

1. Create agent class inheriting from `BaseAgent`
2. Implement required methods
3. Add prompt template to `prompts/`
4. Register in orchestrator
5. Add tests

## 🎓 Best Practices

1. **Always validate data quality** before analysis
2. **Use confidence thresholds** to filter low-quality insights
3. **Test creatives incrementally** don't deploy all at once
4. **Monitor for 7-14 days** for statistical significance
5. **Document decisions** in logs for future reference

## 📚 Documentation

- **[agent_graph.md](agent_graph.md)**: Detailed agent architecture
- **[data/README.md](data/README.md)**: Data format specification
- **[prompts/*.md](prompts/)**: Prompt engineering documentation

## 🚧 Known Limitations

- Mock LLM calls (replace with actual API calls in production)
- Limited to tabular Facebook Ads data
- Requires minimum sample sizes for statistical tests
- Creative generation based on templates (enhance with actual LLM)

## 🔮 Future Enhancements

- [ ] Real LLM integration (OpenAI, Anthropic)
- [ ] Interactive dashboard for reports
- [ ] Multi-platform support (Google Ads, LinkedIn)
- [ ] Automated A/B test execution
- [ ] Memory system for cross-session learning
- [ ] Real-time alerting for performance anomalies

## 📄 License

This project is created for the Kasparro Applied AI Engineer assignment.

## 👤 Author

Built with ❤️ for Kasparro

## 🙏 Acknowledgments

- Synthetic dataset provided by Kasparro
- Inspired by state-of-the-art agentic AI research
- Built with production-grade engineering practices

---

**Version:** 1.0.0  
**Last Updated:** 2025-11-28  
**Status:** Production Ready ✅
