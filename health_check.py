#!/usr/bin/env python3
"""
Health check script for UEPA Bot
Verifies if the bot is running properly and can connect to Discord
"""

import asyncio
import sqlite3
import os
import sys
import logging
from datetime import datetime, timedelta
import aiohttp

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('HealthCheck')

# Configuration
DATABASE_FILE = os.getenv('DATABASE_FILE', 'data/uepa_bot.db')
UEPA_EDITAIS_URL = os.getenv('UEPA_EDITAIS_URL', 'https://www.uepa.br/pt-br/editais')
MAX_LOG_AGE_HOURS = 24

def check_database():
    """Check if database is accessible and has recent activity"""
    try:
        if not os.path.exists(DATABASE_FILE):
            logger.error(f"Database file not found: {DATABASE_FILE}")
            return False
        
        conn = sqlite3.connect(DATABASE_FILE, timeout=5)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        expected_tables = {'all_editais', 'guild_settings', 'guild_roles', 'bot_logs'}
        existing_tables = {table[0] for table in tables}
        
        if not expected_tables.issubset(existing_tables):
            logger.error(f"Missing database tables. Expected: {expected_tables}, Found: {existing_tables}")
            conn.close()
            return False
        
        # Check for recent activity (logs in the last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=MAX_LOG_AGE_HOURS)
        cursor.execute(
            "SELECT COUNT(*) FROM bot_logs WHERE timestamp > ?",
            (cutoff_time.isoformat(),)
        )
        recent_logs = cursor.fetchone()[0]
        
        conn.close()
        
        if recent_logs == 0:
            logger.warning("No recent activity in bot logs")
            # This is a warning, not a failure - bot might be idle
        
        return True
        
    except Exception as e:
        logger.error(f"Database check failed: {e}")
        return False

async def check_uepa_website():
    """Check if UEPA website is accessible"""
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get(UEPA_EDITAIS_URL) as response:
                if response.status == 200:
                    return True
                else:
                    logger.error(f"UEPA website returned status {response.status}")
                    return False
    except Exception as e:
        logger.error(f"UEPA website check failed: {e}")
        return False

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ['DISCORD_TOKEN']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        return False
    
    return True

def check_file_permissions():
    """Check if the application has proper file permissions"""
    try:
        # Check if we can write to data directory
        data_dir = os.path.dirname(DATABASE_FILE)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
        
        # Test write permissions
        test_file = os.path.join(data_dir, '.health_check_test')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        
        return True
        
    except Exception as e:
        logger.error(f"File permissions check failed: {e}")
        return False

async def main():
    """Main health check function"""
    checks = [
        ("Environment Variables", check_environment()),
        ("File Permissions", check_file_permissions()),
        ("Database", check_database()),
        ("UEPA Website", await check_uepa_website()),
    ]
    
    failed_checks = []
    
    for check_name, result in checks:
        if result:
            logger.info(f"✅ {check_name}: OK")
        else:
            logger.error(f"❌ {check_name}: FAILED")
            failed_checks.append(check_name)
    
    if failed_checks:
        logger.error(f"Health check failed. Failed checks: {', '.join(failed_checks)}")
        return False
    
    logger.info("✅ All health checks passed")
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        logger.info("Health check interrupted")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Health check error: {e}")
        sys.exit(1) 