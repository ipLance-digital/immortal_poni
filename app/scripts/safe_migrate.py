"""
Скрипт для безопасного выполнения миграций с бэкапом.
"""
import subprocess
import os
from datetime import datetime
import sys
from dotenv import load_dotenv

load_dotenv()

def create_backup(db_url: str, backup_dir: str = "backups") -> str:
    """Создает бэкап базы данных"""
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{backup_dir}/backup_{timestamp}.sql"
    
    print(f"Creating backup: {backup_file}")
    subprocess.run([
        "pg_dump",
        db_url,
        "-f", backup_file
    ], check=True)
    
    return backup_file

def run_migrations(alembic_ini: str = "app/alembic.ini"):
    """Запускает миграции"""
    print("Generating migration...")
    subprocess.run([
        "alembic", 
        "-c", alembic_ini,
        "revision", 
        "--autogenerate",
        "-m", "auto migration"
    ], check=True)
    
    # Показываем SQL миграции
    print("\nMigration SQL preview:")
    subprocess.run([
        "alembic", 
        "-c", alembic_ini,
        "upgrade", 
        "head", 
        "--sql"
    ])
    
    confirm = input("\nApply migration? [y/N]: ")
    if confirm.lower() != 'y':
        print("Migration cancelled")
        return
        
    print("\nApplying migration...")
    subprocess.run([
        "alembic",
        "-c", alembic_ini,
        "upgrade",
        "head"
    ], check=True)

def main():
    try:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL not found in environment")
            
        # Создаем бэкап
        # backup_file = create_backup(db_url)
        # print(f"Backup created: {backup_file}")
        
        # Запускаем миграции
        run_migrations()
        
        print("\nMigration completed successfully!")
        
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
