"""
SIMPLE ORCHESTRATION SCRIPT
Set up the database and generate lightweight inventory alerts without the old ML pipeline.
"""

import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_pipeline():
    """Set up the database and generate lightweight alerts directly from recent sales history."""

    logger.info("=" * 80)
    logger.info("STARTING SIMPLE RETAIL DEMO SETUP")
    logger.info("=" * 80)

    try:
        from database_setup import setup_database
        from sql_action_engine import execute_action_engine

        logger.info("\n[STEP 1] Setting up database and generating mock data...")
        db_path, _ = setup_database()
        logger.info(f"✓ Database initialized: {db_path}")

        logger.info("\n[STEP 2] Generating simple forecasts and alerts...")
        engine_results = execute_action_engine()
        alerts_df = engine_results['alerts']
        summary = engine_results['summary']

        logger.info(f"✓ Generated {len(alerts_df)} simple reorder alerts")
        logger.info(f"✓ Critical actions: {summary['critical_restock']}")
        logger.info(f"✓ Watchlist products: {summary['watchlist']}")
        logger.info(f"✓ Healthy products: {summary['healthy']}")

        logger.info("\n✅ Simple setup completed successfully!")
        logger.info("   Run 'streamlit run app.py' to launch the dashboard")

        return {
            'status': 'success',
            'database': db_path,
            'alerts': len(alerts_df),
            'summary': summary,
        }

    except Exception as e:
        logger.error(f"\n❌ Setup failed: {str(e)}")
        logger.error("=" * 80)
        import traceback
        traceback.print_exc()
        return {
            'status': 'failed',
            'error': str(e)
        }

if __name__ == "__main__":
    start_time = datetime.now()
    logger.info(f"Setup started at: {start_time}")

    result = run_pipeline()

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    logger.info(f"\nTotal execution time: {duration:.2f} seconds ({duration/60:.2f} minutes)")

    if result['status'] == 'success':
        logger.info("\n🚀 System ready for operation!")
    else:
        logger.error(f"\n⚠️  Setup failed with error: {result.get('error')}")
        sys.exit(1)
