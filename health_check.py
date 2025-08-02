#!/usr/bin/env python3
"""
Health check: Verifies if the bot is running properly and can connect to Discord
"""

import asyncio
import os
import sys
import logging
from datetime import datetime, timedelta
import aiohttp
from sqlalchemy import create_engine, text, exc
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HealthCheck")

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/uepa_bot.db")
UEPA_EDITAIS_URL = os.getenv("UEPA_EDITAIS_URL", "https://www.uepa.br/pt-br/editais")
MAX_LOG_AGE_HOURS = 24


def check_database():
    """Verifica a conexão com o banco de dados e a integridade das tabelas"""
    try:
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Check if tables exist
        expected_tables = {
            "all_editais",
            "guild_settings",
            "guild_roles",
            "bot_logs",
        }
        with engine.connect() as connection:
            table_check_result = connection.execute(
                text(
                    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
                )
            )
            existing_tables = {row[0] for row in table_check_result}

        if not expected_tables.issubset(existing_tables):
            logger.error(
                "Missing database tables. Expected: %s, Found: %s",
                expected_tables,
                existing_tables,
            )
            session.close()
            return False

        # Check for recent activity
        cutoff_time = datetime.now() - timedelta(hours=MAX_LOG_AGE_HOURS)
        stmt = text("SELECT count(1) FROM bot_logs WHERE timestamp > :cutoff")
        recent_logs = session.execute(stmt, {"cutoff": cutoff_time}).scalar_one()

        session.close()

        if recent_logs == 0:
            logger.warning("No recent activity in bot logs")

        return True

    except exc.SQLAlchemyError as e:
        logger.error("Database check failed: %s", e)
        return False


async def check_uepa_website():
    """Check if UEPA website is accessible"""
    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            async with session.get(UEPA_EDITAIS_URL) as response:
                if response.status == 200:
                    return True
                else:
                    logger.error("UEPA website returned status %s", response.status)
                    return False
    except aiohttp.ClientError as e:
        logger.error("UEPA website check failed: %s", e)
        return False


def check_environment():
    """Check if required environment variables are set"""
    required_vars = ["DISCORD_TOKEN"]
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        logger.error("Missing required environment variables: %s", missing_vars)
        return False

    return True


def check_file_permissions():
    """Check if the application has proper file permissions"""
    try:
        db_path = DATABASE_URL.replace("sqlite:///", "")
        data_dir = os.path.dirname(db_path)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)

        test_file = os.path.join(data_dir, ".health_check_test")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("test")
        os.remove(test_file)

        return True

    except IOError as e:
        logger.error("File permissions check failed: %s", e)
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

    for check_name, check_result in checks:
        if check_result:
            logger.info("✅ %s: OK", check_name)
        else:
            logger.error("❌ %s: FAILED", check_name)
            failed_checks.append(check_name)

    if failed_checks:
        logger.error("Health check failed. Failed checks: %s", ", ".join(failed_checks))
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
        logger.error("Health check error: %s", e)
        sys.exit(1)
