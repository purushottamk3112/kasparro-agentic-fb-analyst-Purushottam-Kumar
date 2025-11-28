# Installation & Setup Guide

## Prerequisites

- **Python**: 3.10 or higher
- **pip**: Latest version
- **Operating System**: Linux, macOS, or Windows

## Step 1: Download the Project

Extract the ZIP file to your desired location:
```bash
unzip kasparro-agentic-fb-analyst.zip
cd kasparro-agentic-fb-analyst
```

## Step 2: Create Virtual Environment

### On Linux/macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### On Windows:
```cmd
python -m venv .venv
.venv\Scripts\activate
```

## Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed pandas-2.1.4 numpy-1.26.3 ...
```

## Step 4: Verify Installation

```bash
python src/run.py --help
```

**Expected output:**
```
usage: run.py [-h] [--config CONFIG] [--data DATA] [--verbose] query

Kasparro Agentic Facebook Performance Analyst
...
```

## Step 5: Run Your First Analysis

```bash
python src/run.py "Analyze ROAS drop in last 7 days"
```

**Expected output:**
```
======================================================================
KASPARRO AGENTIC FB ANALYST
======================================================================
Query: Analyze ROAS drop in last 7 days

[00:00:00] INFO     Orchestrator initialized with all agents
[00:00:00] INFO     === Starting Agentic Analysis ===
[00:00:00] INFO     Loading data from: synthetic_fb_ads_undergarments.csv
[00:00:01] INFO     Data loaded successfully: 4500 rows
...
======================================================================
ANALYSIS COMPLETE
======================================================================

Output files generated:
  - reports/insights.json
  - reports/creatives.json
  - reports/report.md
```

## Step 6: Review Results

```bash
# View the human-readable report
cat reports/report.md

# View structured insights (requires jq)
cat reports/insights.json | jq .

# View creative recommendations
cat reports/creatives.json | jq .
```

## Troubleshooting

### Issue: "No module named 'pandas'"
**Solution:** Activate virtual environment and reinstall dependencies
```bash
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: "Data not found"
**Solution:** Ensure CSV file exists in project root
```bash
ls -la synthetic_fb_ads_undergarments.csv
# If missing, check data/ directory or use sample:
export DATA_CSV=data/sample_fb_ads.csv
```

### Issue: Permission denied (Linux/macOS)
**Solution:** Make run.py executable
```bash
chmod +x src/run.py
```

### Issue: Import errors
**Solution:** Ensure you're in project root directory
```bash
pwd  # Should show /path/to/kasparro-agentic-fb-analyst
python src/run.py "Your query"  # Not: python run.py
```

## Using Make (Optional)

If you have `make` installed:

```bash
# Setup environment
make setup

# Run analysis
make run

# Run tests
make test

# Clean generated files
make clean
```

## Configuration

Edit `config/config.yaml` to customize:

```yaml
# Use sample data for testing
use_sample_data: true  # Set to false for full dataset

# Adjust thresholds
thresholds:
  roas_drop_threshold: 0.15
  ctr_low_threshold: 0.015

# Modify agent parameters
agents:
  creative_generator:
    max_suggestions: 10  # Generate more recommendations
```

## Next Steps

1. **Read the Documentation**:
   - [README.md](README.md) - Complete user guide
   - [agent_graph.md](agent_graph.md) - Architecture details
   - [data/README.md](data/README.md) - Data format specification

2. **Try Different Queries**:
   ```bash
   python src/run.py "Why is CTR declining?"
   python src/run.py "Which campaigns are underperforming?"
   python src/run.py "Analyze creative performance"
   ```

3. **Use Your Own Data**:
   ```bash
   export DATA_CSV=/path/to/your/facebook_ads_data.csv
   python src/run.py "Your custom query"
   ```

4. **Explore Outputs**:
   - Check `reports/` directory for analysis results
   - Review `logs/` directory for detailed execution traces
   
5. **Run Tests**:
   ```bash
   python tests/test_evaluator.py
   # Or with pytest:
   pytest tests/ -v
   ```

## Support

For issues or questions:
1. Check [README.md](README.md) - FAQ section
2. Review log files in `logs/` directory
3. Verify data format matches specification in `data/README.md`

## System Requirements

**Minimum:**
- Python 3.10+
- 500MB free disk space
- 2GB RAM

**Recommended:**
- Python 3.11+
- 1GB free disk space
- 4GB RAM
- SSD for faster data processing

---

**Version**: 1.0.0  
**Last Updated**: 2025-11-28
