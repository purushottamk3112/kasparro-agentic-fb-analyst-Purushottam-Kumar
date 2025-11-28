"""
Data Agent - Loads, analyzes, and summarizes Facebook Ads data
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from .base_agent import BaseAgent


class DataAgent(BaseAgent):
    """
    Data Agent responsible for:
    - Loading and cleaning data
    - Computing summary statistics
    - Identifying trends and patterns
    - Preparing data for analysis
    """
    
    def __init__(self, config: Dict[str, Any], logger: Any):
        super().__init__("DataAgent", config, logger)
        self.prompt_template = self.load_prompt("data_agent_prompt")
        self.df: Optional[pd.DataFrame] = None
        self.data_loaded = False
    
    def load_data(self, data_path: str) -> bool:
        """Load data from CSV file"""
        try:
            self.logger.info(f"Loading data from: {data_path}")
            self.df = pd.read_csv(data_path)
            
            # Clean and prepare data
            self._clean_data()
            
            self.data_loaded = True
            self.logger.info(f"Data loaded successfully: {len(self.df)} rows")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load data: {e}")
            return False
    
    def _clean_data(self):
        """Clean and prepare data"""
        if self.df is None:
            return
        
        # Convert date column to datetime
        if 'date' in self.df.columns:
            self.df['date'] = pd.to_datetime(self.df['date'])
        
        # Fill missing spend values (assuming 0 if missing)
        if 'spend' in self.df.columns:
            self.df['spend'] = self.df['spend'].fillna(0)
        
        # Remove rows with critical missing values
        critical_cols = ['campaign_name', 'date']
        self.df = self.df.dropna(subset=critical_cols)
        
        # Calculate derived metrics if not present
        if 'ctr' not in self.df.columns and 'clicks' in self.df.columns and 'impressions' in self.df.columns:
            self.df['ctr'] = self.df['clicks'] / self.df['impressions']
            self.df['ctr'] = self.df['ctr'].fillna(0)
        
        if 'roas' not in self.df.columns and 'revenue' in self.df.columns and 'spend' in self.df.columns:
            self.df['roas'] = self.df['revenue'] / self.df['spend']
            self.df['roas'] = self.df['roas'].replace([np.inf, -np.inf], 0).fillna(0)
        
        self.logger.info(f"Data cleaned: {len(self.df)} rows, {len(self.df.columns)} columns")
    
    def analyze_data(self, task_description: str, analysis_period: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze data and generate comprehensive summary
        
        Args:
            task_description: Description of what analysis is needed
            analysis_period: Time period to focus on (e.g., 'last 7 days')
            
        Returns:
            Comprehensive data analysis results
        """
        if not self.data_loaded or self.df is None:
            self.logger.error("Data not loaded")
            return {"error": "Data not loaded"}
        
        self.logger.info(f"Analyzing data for: {task_description}")
        
        # Filter by period if specified
        df_analysis = self._filter_by_period(analysis_period) if analysis_period else self.df
        
        # Compute all analyses
        analysis_results = {
            "data_quality": self._analyze_data_quality(df_analysis),
            "summary_statistics": self._compute_summary_statistics(df_analysis),
            "trends": self._analyze_trends(df_analysis),
            "key_observations": self._identify_key_observations(df_analysis),
            "top_performers": self._identify_top_performers(df_analysis),
            "bottom_performers": self._identify_bottom_performers(df_analysis),
            "segment_analysis": self._analyze_segments(df_analysis),
            "data_ready_for_analysis": True
        }
        
        # Generate LLM-powered insights
        llm_analysis = self._generate_llm_analysis(task_description, analysis_results, analysis_period)
        if llm_analysis:
            analysis_results["llm_insights"] = llm_analysis
        
        # Log execution
        self.log_execution("analyze_data", analysis_results, {
            "task": task_description,
            "period": analysis_period,
            "rows_analyzed": len(df_analysis)
        })
        
        return analysis_results
    
    def _filter_by_period(self, period: str) -> pd.DataFrame:
        """Filter dataframe by time period"""
        if 'date' not in self.df.columns:
            return self.df
        
        max_date = self.df['date'].max()
        
        # Parse period
        if 'last' in period.lower() and 'day' in period.lower():
            days = int(''.join(filter(str.isdigit, period)))
            start_date = max_date - timedelta(days=days)
            return self.df[self.df['date'] >= start_date]
        elif 'last' in period.lower() and 'week' in period.lower():
            weeks = int(''.join(filter(str.isdigit, period)) or '1')
            start_date = max_date - timedelta(weeks=weeks)
            return self.df[self.df['date'] >= start_date]
        
        return self.df
    
    def _analyze_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data quality"""
        missing_values = df.isnull().sum().to_dict()
        missing_values = {k: int(v) for k, v in missing_values.items() if v > 0}
        
        return {
            "total_rows": len(df),
            "date_range": {
                "start": df['date'].min().strftime('%Y-%m-%d') if 'date' in df.columns else "Unknown",
                "end": df['date'].max().strftime('%Y-%m-%d') if 'date' in df.columns else "Unknown"
            },
            "missing_values": missing_values,
            "anomalies": self._detect_anomalies(df)
        }
    
    def _detect_anomalies(self, df: pd.DataFrame) -> List[str]:
        """Detect data anomalies"""
        anomalies = []
        
        # Check for negative values in metrics that should be positive
        if 'spend' in df.columns and (df['spend'] < 0).any():
            anomalies.append("Negative spend values detected")
        
        if 'revenue' in df.columns and (df['revenue'] < 0).any():
            anomalies.append("Negative revenue values detected")
        
        # Check for unrealistic ROAS values
        if 'roas' in df.columns:
            high_roas = df[df['roas'] > 50]
            if len(high_roas) > 0:
                anomalies.append(f"{len(high_roas)} rows with unusually high ROAS (>50)")
        
        # Check for unrealistic CTR values
        if 'ctr' in df.columns:
            high_ctr = df[df['ctr'] > 0.1]  # 10% CTR is very high
            if len(high_ctr) > 0:
                anomalies.append(f"{len(high_ctr)} rows with unusually high CTR (>10%)")
        
        return anomalies
    
    def _compute_summary_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Compute summary statistics"""
        overall_stats = {
            "total_spend": float(df['spend'].sum()) if 'spend' in df.columns else 0,
            "total_revenue": float(df['revenue'].sum()) if 'revenue' in df.columns else 0,
            "total_impressions": int(df['impressions'].sum()) if 'impressions' in df.columns else 0,
            "total_clicks": int(df['clicks'].sum()) if 'clicks' in df.columns else 0,
            "total_purchases": int(df['purchases'].sum()) if 'purchases' in df.columns else 0,
            "avg_roas": float(df['roas'].mean()) if 'roas' in df.columns else 0,
            "avg_ctr": float(df['ctr'].mean()) if 'ctr' in df.columns else 0
        }
        
        # By campaign
        by_campaign = []
        if 'campaign_name' in df.columns:
            campaign_groups = df.groupby('campaign_name').agg({
                'spend': 'sum',
                'revenue': 'sum',
                'roas': 'mean',
                'ctr': 'mean'
            }).round(2)
            
            for campaign, row in campaign_groups.iterrows():
                by_campaign.append({
                    "campaign_name": campaign,
                    "spend": float(row['spend']),
                    "revenue": float(row['revenue']),
                    "roas": float(row['roas']),
                    "ctr": float(row['ctr'])
                })
        
        # By creative type
        by_creative = {}
        if 'creative_type' in df.columns:
            creative_groups = df.groupby('creative_type').agg({
                'roas': 'mean',
                'ctr': 'mean',
                'spend': 'sum'
            }).round(3)
            # Convert to serializable dict
            for ctype, row in creative_groups.iterrows():
                by_creative[str(ctype)] = {
                    'roas': float(row['roas']),
                    'ctr': float(row['ctr']),
                    'spend': float(row['spend'])
                }
        
        # By audience type
        by_audience = {}
        if 'audience_type' in df.columns:
            audience_groups = df.groupby('audience_type').agg({
                'roas': 'mean',
                'ctr': 'mean',
                'spend': 'sum'
            }).round(3)
            # Convert to serializable dict
            for atype, row in audience_groups.iterrows():
                by_audience[str(atype)] = {
                    'roas': float(row['roas']),
                    'ctr': float(row['ctr']),
                    'spend': float(row['spend'])
                }
        
        return {
            "overall": overall_stats,
            "by_campaign": by_campaign[:10],  # Top 10 campaigns
            "by_creative_type": by_creative,
            "by_audience_type": by_audience
        }
    
    def _analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze trends over time"""
        if 'date' not in df.columns:
            return {"error": "No date column available"}
        
        # Group by date
        daily_stats = df.groupby('date').agg({
            'spend': 'sum',
            'revenue': 'sum',
            'roas': 'mean',
            'ctr': 'mean'
        }).sort_index()
        
        # Calculate trends
        def get_trend(series):
            if len(series) < 2:
                return "stable"
            recent = series.tail(len(series)//2).mean()
            older = series.head(len(series)//2).mean()
            if recent > older * 1.1:
                return "increasing"
            elif recent < older * 0.9:
                return "decreasing"
            return "stable"
        
        return {
            "roas_trend": get_trend(daily_stats['roas']),
            "ctr_trend": get_trend(daily_stats['ctr']),
            "spend_trend": get_trend(daily_stats['spend']),
            "time_series_summary": f"Analysis of {len(daily_stats)} days from {daily_stats.index.min().strftime('%Y-%m-%d')} to {daily_stats.index.max().strftime('%Y-%m-%d')}"
        }
    
    def _identify_key_observations(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify key observations"""
        observations = []
        
        # Check for significant ROAS variations
        if 'roas' in df.columns and 'campaign_name' in df.columns:
            campaign_roas = df.groupby('campaign_name')['roas'].mean()
            if campaign_roas.std() > 1.0:
                observations.append({
                    "observation": f"High ROAS variation across campaigns (std={campaign_roas.std():.2f})",
                    "significance": "high",
                    "metrics_affected": ["roas"]
                })
        
        # Check for low CTR campaigns
        if 'ctr' in df.columns and 'campaign_name' in df.columns:
            low_ctr_threshold = self.config.get('thresholds', {}).get('ctr_low_threshold', 0.015)
            campaign_ctr = df.groupby('campaign_name')['ctr'].mean()
            low_ctr_campaigns = campaign_ctr[campaign_ctr < low_ctr_threshold]
            if len(low_ctr_campaigns) > 0:
                observations.append({
                    "observation": f"{len(low_ctr_campaigns)} campaigns with CTR below {low_ctr_threshold*100}%",
                    "significance": "high",
                    "metrics_affected": ["ctr"]
                })
        
        return observations
    
    def _identify_top_performers(self, df: pd.DataFrame) -> Dict[str, List]:
        """Identify top performing campaigns/adsets"""
        top_performers = {}
        
        if 'campaign_name' in df.columns:
            # By ROAS
            campaign_roas = df.groupby('campaign_name').agg({
                'roas': 'mean',
                'spend': 'sum'
            })
            # Filter by minimum spend
            min_spend = self.config.get('thresholds', {}).get('spend_significance', 100)
            campaign_roas = campaign_roas[campaign_roas['spend'] >= min_spend]
            
            top_roas = campaign_roas.nlargest(5, 'roas')
            top_performers['by_roas'] = [
                {"name": name, "value": float(row['roas'])}
                for name, row in top_roas.iterrows()
            ]
            
            # By CTR
            campaign_ctr = df.groupby('campaign_name').agg({
                'ctr': 'mean',
                'spend': 'sum'
            })
            campaign_ctr = campaign_ctr[campaign_ctr['spend'] >= min_spend]
            
            top_ctr = campaign_ctr.nlargest(5, 'ctr')
            top_performers['by_ctr'] = [
                {"name": name, "value": float(row['ctr'])}
                for name, row in top_ctr.iterrows()
            ]
        
        return top_performers
    
    def _identify_bottom_performers(self, df: pd.DataFrame) -> Dict[str, List]:
        """Identify bottom performing campaigns/adsets"""
        bottom_performers = {}
        
        if 'campaign_name' in df.columns:
            min_spend = self.config.get('thresholds', {}).get('spend_significance', 100)
            
            # By ROAS
            campaign_roas = df.groupby('campaign_name').agg({
                'roas': 'mean',
                'spend': 'sum'
            })
            campaign_roas = campaign_roas[campaign_roas['spend'] >= min_spend]
            
            bottom_roas = campaign_roas.nsmallest(5, 'roas')
            bottom_performers['by_roas'] = [
                {"name": name, "value": float(row['roas'])}
                for name, row in bottom_roas.iterrows()
            ]
            
            # By CTR
            campaign_ctr = df.groupby('campaign_name').agg({
                'ctr': 'mean',
                'spend': 'sum'
            })
            campaign_ctr = campaign_ctr[campaign_ctr['spend'] >= min_spend]
            
            bottom_ctr = campaign_ctr.nsmallest(5, 'ctr')
            bottom_performers['by_ctr'] = [
                {"name": name, "value": float(row['ctr'])}
                for name, row in bottom_ctr.iterrows()
            ]
        
        return bottom_performers
    
    def _analyze_segments(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze performance by different segments"""
        segments = {}
        
        # By creative type and audience type
        if 'creative_type' in df.columns and 'audience_type' in df.columns:
            segment_analysis = df.groupby(['creative_type', 'audience_type']).agg({
                'roas': 'mean',
                'ctr': 'mean',
                'spend': 'sum'
            }).round(3)
            
            # Convert to serializable dict
            segments['creative_x_audience'] = {}
            for (ctype, atype), row in segment_analysis.iterrows():
                key = f"{ctype}_{atype}"
                segments['creative_x_audience'][key] = {
                    'roas': float(row['roas']),
                    'ctr': float(row['ctr']),
                    'spend': float(row['spend'])
                }
        
        return segments
    
    def _generate_llm_analysis(self, task: str, analysis: Dict[str, Any], period: Optional[str]) -> Optional[Dict]:
        """Generate LLM-powered insights from analysis"""
        # Format analysis summary for LLM
        summary_text = json.dumps(analysis, indent=2, default=str)
        
        prompt_vars = {
            "task_description": task,
            "data_summary": summary_text[:2000],  # Truncate if too long
            "analysis_period": period or "full dataset",
            "metrics_requested": "roas, ctr, spend, revenue"
        }
        
        prompt = self.format_prompt(self.prompt_template, prompt_vars)
        
        # For mock implementation, return None (would call LLM in production)
        # response = self.call_llm(prompt, temperature=0.1)
        # return self.parse_json_response(response)
        
        return None
    
    def get_creative_performance(self) -> List[Dict[str, Any]]:
        """Get creative performance data for creative generator"""
        if not self.data_loaded or self.df is None:
            return []
        
        creative_perf = []
        
        if 'creative_message' in self.df.columns:
            creative_groups = self.df.groupby('creative_message').agg({
                'roas': 'mean',
                'ctr': 'mean',
                'spend': 'sum',
                'revenue': 'sum',
                'creative_type': 'first',
                'campaign_name': 'first'
            }).round(3)
            
            for message, row in creative_groups.iterrows():
                creative_perf.append({
                    "creative_message": message,
                    "creative_type": row['creative_type'],
                    "campaign_name": row['campaign_name'],
                    "roas": float(row['roas']),
                    "ctr": float(row['ctr']),
                    "spend": float(row['spend']),
                    "revenue": float(row['revenue'])
                })
        
        return creative_perf
    
    def get_dataset_info(self) -> Dict[str, Any]:
        """Get basic dataset information"""
        if not self.data_loaded or self.df is None:
            return {}
        
        return {
            "schema": {col: str(dtype) for col, dtype in self.df.dtypes.items()},
            "date_range": f"{self.df['date'].min()} to {self.df['date'].max()}" if 'date' in self.df.columns else "Unknown",
            "total_rows": len(self.df),
            "campaigns": self.df['campaign_name'].nunique() if 'campaign_name' in self.df.columns else 0
        }
