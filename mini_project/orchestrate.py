"""
ORCHESTRATION SCRIPT - RUN ALL PHASES
Complete end-to-end execution: Database Setup → Feature Engineering → ML Pipeline → SQL Action Engine
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
    """Execute all phases of the Dual-Engine system."""
    
    logger.info("=" * 80)
    logger.info("STARTING DUAL-ENGINE RETAIL DEMAND FORECASTING PIPELINE")
    logger.info("=" * 80)
    
    try:
        # PHASE 1: DATABASE SETUP & MOCK DATA GENERATION
        logger.info("\n[PHASE 1] Setting up database and generating mock data...")
        logger.info("-" * 80)
        
        from database_setup import setup_database
        db_path, db_url = setup_database()
        
        logger.info(f"✓ Database initialized: {db_path}")
        logger.info("✓ Mock data generated (180 days of sales history)")
        
        # PHASE 2: MACHINE LEARNING PIPELINE
        logger.info("\n[PHASE 2] Executing ML Pipeline...")
        logger.info("-" * 80)
        
        from ml_pipeline import run_ml_pipeline
        forecast_df = run_ml_pipeline()
        
        logger.info(f"✓ ML model trained and saved")
        logger.info(f"✓ Generated {len(forecast_df)} forecast records (7-day ahead)")
        logger.info(f"✓ Model metrics: MAE, RMSE, and R² computed")
        
        # PHASE 3: SQL ACTION ENGINE
        logger.info("\n[PHASE 3] Executing SQL Action Engine...")
        logger.info("-" * 80)
        
        from sql_action_engine import execute_action_engine
        engine_results = execute_action_engine(forecast_df)
        
        alerts_df = engine_results['alerts']
        critical_actions = engine_results['critical_actions']
        watchlist = engine_results['watchlist']
        summary = engine_results['summary']
        
        logger.info(f"✓ Saved {len(forecast_df)} forecasts to database")
        logger.info(f"✓ Generated {len(alerts_df)} automated reorder alerts")
        logger.info(f"✓ Critical actions: {summary['critical_restock']}")
        logger.info(f"✓ Watchlist products: {summary['watchlist']}")
        logger.info(f"✓ Healthy products: {summary['healthy']}")
        
        # DISPLAY SUMMARY
        logger.info("\n" + "=" * 80)
        logger.info("PIPELINE EXECUTION COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        
        logger.info("\n📊 EXECUTIVE SUMMARY:")
        logger.info(f"  Total Products Monitored: {summary['total_products']}")
        logger.info(f"  Critical Restock (🔴): {summary['critical_restock']} products")
        logger.info(f"  Watchlist (🟡): {summary['watchlist']} products")
        logger.info(f"  Healthy Status (🟢): {summary['healthy']} products")
        logger.info(f"  Total 7-Day Predicted Demand: {int(summary['total_7day_demand']):,} units")
        logger.info(f"  Total Current Inventory: {int(summary['total_current_inventory']):,} units")
        logger.info(f"  Average Days of Inventory: {summary['average_days_inventory']:.1f} days")
        
        logger.info("\n🎯 NEXT STEPS:")
        logger.info("  1. Review critical restock items (see output above)")
        logger.info("  2. Launch Streamlit dashboard: streamlit run app.py")
        logger.info("  3. Monitor forecast accuracy over next 7 days")
        logger.info("  4. Re-run pipeline daily for updated forecasts")
        
        logger.info("\n✅ All phases completed successfully!")
        logger.info("=" * 80)
        
        return {
            'status': 'success',
            'database': db_path,
            'forecasts': len(forecast_df),
            'alerts': len(alerts_df),
            'critical_actions': len(critical_actions),
            'summary': summary
        }
    
    except Exception as e:
        logger.error(f"\n❌ Pipeline execution failed: {str(e)}")
        logger.error("=" * 80)
        import traceback
        traceback.print_exc()
        return {
            'status': 'failed',
            'error': str(e)
        }

if __name__ == "__main__":
    start_time = datetime.now()
    logger.info(f"Pipeline started at: {start_time}")
    
    result = run_pipeline()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info(f"\nTotal execution time: {duration:.2f} seconds ({duration/60:.2f} minutes)")
    
    if result['status'] == 'success':
        logger.info("\n🚀 System ready for operation!")
        logger.info("   Run 'streamlit run app.py' to launch the interactive dashboard")
    else:
        logger.error(f"\n⚠️  Pipeline failed with error: {result.get('error')}")
        sys.exit(1)
