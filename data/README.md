# Data Documentation

## Dataset Overview

This directory contains Facebook Ads performance data for analysis by the Kasparro Agentic FB Analyst system.

## Data Schema

### Required Columns

| Column Name | Type | Description | Example |
|------------|------|-------------|---------|
| `campaign_name` | string | Name of the advertising campaign | "Men_ComfortMax_Launch" |
| `adset_name` | string | Name of the ad set within campaign | "Adset-1 Retarget" |
| `date` | date | Date of the ad performance | "2025-01-01" |
| `spend` | float | Amount spent on ads ($) | 640.09 |
| `impressions` | integer | Number of ad impressions | 235597 |
| `clicks` | integer | Number of clicks on ads | 4313 |
| `ctr` | float | Click-through rate (0-1) | 0.0183 |
| `purchases` | integer | Number of purchases/conversions | 80 |
| `revenue` | float | Revenue generated ($) | 1514.28 |
| `roas` | float | Return on ad spend | 2.37 |
| `creative_type` | string | Type of creative asset | "Image", "Video", "UGC" |
| `creative_message` | string | Ad copy/messaging | "Breathable organic cotton..." |
| `audience_type` | string | Audience targeting type | "Broad", "Lookalike", "Retarget" |
| `platform` | string | Advertising platform | "Facebook", "Instagram" |
| `country` | string | Target country | "US", "UK", "CA" |

### Data Types

```python
{
    'campaign_name': str,
    'adset_name': str,
    'date': datetime,
    'spend': float,
    'impressions': int,
    'clicks': int,
    'ctr': float,
    'purchases': int,
    'revenue': float,
    'roas': float,
    'creative_type': str,
    'creative_message': str,
    'audience_type': str,
    'platform': str,
    'country': str
}
```

## Data Quality Requirements

### Minimum Requirements

- **Date Range**: At least 7 days of continuous data
- **Completeness**: < 5% missing values in critical columns
- **Sample Size**: Minimum 100 rows for statistical analysis
- **Spend Threshold**: Campaigns with >= $100 spend for significance

### Data Validation

The Data Agent performs automatic validation:
- Checks for missing values
- Detects outliers (ROAS > 50, CTR > 10%)
- Validates date continuity
- Ensures numeric fields are within reasonable ranges

## File Locations

### Full Dataset
```
synthetic_fb_ads_undergarments.csv
```
- Located in project root
- ~800KB, contains full performance history
- Use for production analysis

### Sample Dataset (Optional)
```
data/sample_fb_ads.csv
```
- Smaller subset for testing
- Faster iteration during development
- Configure in `config/config.yaml`

## Usage

### Load Full Dataset
```yaml
# config/config.yaml
use_sample_data: false
data_csv: "synthetic_fb_ads_undergarments.csv"
```

### Load Sample Dataset
```yaml
# config/config.yaml
use_sample_data: true
sample_data_csv: "data/sample_fb_ads.csv"
```

### Via Environment Variable
```bash
export DATA_CSV=/path/to/your/data.csv
python src/run.py "Your query"
```

## Data Preparation Tips

### If Using Your Own Data

1. **Match the schema**: Ensure all required columns present
2. **Date format**: Use ISO format (YYYY-MM-DD) or pandas-compatible
3. **Numeric formats**: Use float for decimals, int for counts
4. **Handle nulls**: Fill or drop missing values appropriately
5. **Clean text**: Remove special characters from campaign names

### Creating a Sample

```python
import pandas as pd

# Load full dataset
df = pd.read_csv('synthetic_fb_ads_undergarments.csv')

# Create sample (last 30 days, top campaigns)
df_sample = df.sort_values('date').tail(1000)

# Save sample
df_sample.to_csv('data/sample_fb_ads.csv', index=False)
```

## Example Data

```csv
campaign_name,adset_name,date,spend,impressions,clicks,ctr,purchases,revenue,roas,creative_type,creative_message,audience_type,platform,country
Men_ComfortMax_Launch,Adset-1 Retarget,2025-01-01,640.09,235597,4313,0.0183,80,1514.28,2.37,Image,"Breathable organic cotton that moves with you",Broad,Facebook,US
Men_ComfortMax_Launch,Adset-1 Retarget,2025-01-02,373.75,276194,5429,0.0197,94,4152.81,11.11,Video,"No ride-up guarantee — best-selling men briefs",Broad,Facebook,US
```

## Metrics Glossary

### Primary Metrics

- **ROAS** (Return on Ad Spend): Revenue ÷ Spend
  - Target: > 3.0 for profitable campaigns
  - < 1.0 indicates loss

- **CTR** (Click-Through Rate): Clicks ÷ Impressions
  - Benchmark: 1.5-2.0% for eCommerce
  - < 1.0% indicates creative issues

- **CPC** (Cost Per Click): Spend ÷ Clicks
  - Lower is better
  - Varies by industry and audience

- **CVR** (Conversion Rate): Purchases ÷ Clicks
  - Benchmark: 2-5% for eCommerce
  - Indicates landing page quality

### Derived Metrics

The system automatically calculates:
- **CPA** (Cost Per Acquisition): Spend ÷ Purchases
- **Revenue Per Purchase**: Revenue ÷ Purchases
- **Frequency**: Impressions ÷ Unique Reach (if available)

## Data Privacy

- All data in this project is **synthetic**
- No real customer or business data
- Safe for public repositories
- Use for demonstration and testing purposes

## Troubleshooting

### Common Issues

**"Data not found"**
```bash
# Check file exists
ls -la synthetic_fb_ads_undergarments.csv

# Use absolute path
export DATA_CSV=/full/path/to/data.csv
```

**"Invalid date format"**
```python
# Convert dates in pandas
df['date'] = pd.to_datetime(df['date'])
df.to_csv('fixed_data.csv', index=False)
```

**"Missing required columns"**
```python
# Check columns
df.columns.tolist()

# Rename if needed
df.rename(columns={'old_name': 'campaign_name'}, inplace=True)
```

## Data Sources

For production use, data typically comes from:
- **Facebook Ads Manager**: Manual export
- **Facebook Marketing API**: Automated retrieval
- **Third-party tools**: Funnel.io, Supermetrics, etc.
- **Data warehouses**: BigQuery, Snowflake, Redshift

## Related Documentation

- [Main README](../README.md): System overview
- [config.yaml](../config/config.yaml): Data configuration
- [agent_graph.md](../agent_graph.md): Data flow architecture

---

**Version**: 1.0  
**Last Updated**: 2025-11-28
