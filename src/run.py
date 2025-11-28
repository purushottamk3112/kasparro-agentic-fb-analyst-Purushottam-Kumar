#!/usr/bin/env python3
"""
Main entry point for Kasparro Agentic FB Analyst

Usage:
    python src/run.py "Analyze ROAS drop in last 7 days"
    python src/run.py "Why is CTR declining?"
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import load_config, setup_logger
from src.orchestrator.orchestrator import AgenticOrchestrator


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Kasparro Agentic Facebook Performance Analyst",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/run.py "Analyze ROAS drop in last 7 days"
  python src/run.py "Why is CTR declining?"
  python src/run.py "Which campaigns are underperforming?"
        """
    )
    
    parser.add_argument(
        'query',
        type=str,
        help='Analytical query to process'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to config file (default: config/config.yaml)'
    )
    
    parser.add_argument(
        '--data',
        type=str,
        default=None,
        help='Path to data CSV file'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    try:
        config = load_config(args.config)
        
        if args.verbose:
            config['logging']['level'] = 'DEBUG'
        
        logger = setup_logger("Main", config)
        logger.info("=" * 70)
        logger.info("KASPARRO AGENTIC FB ANALYST")
        logger.info("=" * 70)
        logger.info(f"Query: {args.query}")
        logger.info("")
        
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)
    
    # Initialize orchestrator
    try:
        orchestrator = AgenticOrchestrator(config)
    except Exception as e:
        logger.error(f"Failed to initialize orchestrator: {e}")
        sys.exit(1)
    
    # Run analysis
    try:
        results = orchestrator.run(args.query, args.data)
        
        if 'error' in results:
            logger.error(f"Analysis failed: {results['error']}")
            sys.exit(1)
        
        logger.info("")
        logger.info("=" * 70)
        logger.info("ANALYSIS COMPLETE")
        logger.info("=" * 70)
        logger.info("")
        logger.info("Output files generated:")
        logger.info("  - reports/insights.json")
        logger.info("  - reports/creatives.json")
        logger.info("  - reports/report.md")
        logger.info("")
        logger.info("Review reports/ directory for detailed findings.")
        
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
