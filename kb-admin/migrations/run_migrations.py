"""
Migration runner for KB-Admin service
Executes SQL migration files in order
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_db_connection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migrations():
    """
    Execute all SQL migration files in order
    """
    migrations_dir = Path(__file__).parent
    migration_files = sorted([
        f for f in migrations_dir.glob("*.sql")
        if f.name.startswith(("001_", "002_", "003_", "004_"))
    ])

    if not migration_files:
        logger.warning("No migration files found")
        return

    logger.info(f"Found {len(migration_files)} migration files")

    with get_db_connection() as conn:
        cursor = conn.cursor()

        for migration_file in migration_files:
            logger.info(f"Running migration: {migration_file.name}")

            try:
                sql = migration_file.read_text()
                # Execute SQL (may contain multiple statements)
                for statement in sql.split(';'):
                    statement = statement.strip()
                    if statement:
                        cursor.execute(statement)

                conn.commit()
                logger.info(f"✓ Migration {migration_file.name} completed successfully")

            except Exception as e:
                logger.error(f"✗ Migration {migration_file.name} failed: {e}")
                conn.rollback()
                raise

    logger.info("All migrations completed successfully!")


if __name__ == "__main__":
    run_migrations()
