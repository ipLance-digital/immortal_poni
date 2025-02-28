import subprocess
import os
import sys
import logging
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()


def run_migrations(alembic_ini: str = "alembic.ini"):
    """
        Запускает миграции с автоматическим откатом и повторным применением
    """
    if not os.path.exists(alembic_ini):
        logger.error(f"Файл {alembic_ini} не найден.")
        sys.exit(1)

    logger.info("Генерация миграции...")
    try:
        subprocess.run(
            [
                "alembic",
                "-c",
                alembic_ini,
                "revision",
                "--autogenerate",
                "-m",
                "auto migration",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка при генерации миграции: {e}")
        sys.exit(1)

    logger.info("\nПредварительный просмотр SQL миграции:")
    try:
        subprocess.run([
            "alembic", "-c", alembic_ini, "upgrade", "head", "--sql"
        ], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка при просмотре SQL миграции: {e}")
        sys.exit(1)

    confirm = input("\nПрименить миграцию? [y/N]: ").strip().lower()
    if confirm not in ("y", "yes"):
        logger.info("Миграция отменена.")
        return

    logger.info("\nПрименение миграции...")
    try:
        subprocess.run([
            "alembic", "-c",
            alembic_ini,
            "upgrade",
            "head"
        ], check=True)
        logger.info("Миграция успешно применена!")
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка при применении миграции: {e}")
        logger.info("Попытка отката и повторного применения миграции...")

        try:
            logger.info("Откат миграции...")
            subprocess.run([
                "alembic", "-c",
                alembic_ini,
                "downgrade",
                "base"
            ], check=True)
            logger.info("Повторное применение миграции...")
            subprocess.run([
                "alembic",
                "-c", alembic_ini,
                "upgrade",
                "head"
            ], check=True)
            logger.info("Миграция успешно применена после отката!")
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка при откате и повторном применении миграции: {e}")
            sys.exit(1)


def main():
    try:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("Переменная окружения DATABASE_URL не найдена.")

        logger.info(f"Используется база данных: {db_url}")
        run_migrations()

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
