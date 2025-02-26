from supabase import create_client, Client
from fastapi import HTTPException
from typing import Optional
from app.core.config import settings
from pathlib import Path

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
BUCKET_NAME = settings.BUCKET_NAME

class SupabaseStorage:
    @staticmethod
    async def upload_file(file_path: str, file_name: str) -> Optional[str]:
        """
        Загружает файл в Supabase Storage и возвращает публичную ссылку.
        
        Args:
            file_path: Путь к файлу на локальном диске.
            file_name: Имя файла в хранилище.

        Returns:
            str: Публичная ссылка на файл или None, если ошибка.
        
        Raises:
            HTTPException: Если файл не найден или загрузка не удалась.
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise HTTPException(status_code=400, detail="Файл не найден")

            with open(file_path, "rb") as file:
                response = supabase.storage.from_(BUCKET_NAME).upload(file_name, file)
            
            if response.get("status", 400) == 200:
                return f"{settings.SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{file_name}"
            raise HTTPException(status_code=500, detail="Ошибка загрузки файла")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def delete_file(file_name: str) -> bool:
        """
        Удаляет файл из Supabase Storage.
        
        Args:
            file_name: Имя файла в хранилище.

        Returns:
            bool: True, если удаление успешно, иначе False.
        """
        try:
            response = supabase.storage.from_(BUCKET_NAME).remove([file_name])
            return response.get("status", 400) == 200
        except Exception:
            return False

    @staticmethod
    async def rename_file(old_name: str, new_name: str) -> Optional[str]:
        """
        Переименовывает файл в Supabase Storage (копирует и удаляет старый).
        
        Args:
            old_name: Текушее имя файла.
            new_name: Новое имя файла.

        Returns:
            str: Публичная ссылка на переименованный файл или None, если ошибка.
        """
        try:
            # Скачиваем данные файла
            file_data = supabase.storage.from_(BUCKET_NAME).download(old_name)
            if not file_data:
                raise HTTPException(status_code=404, detail="Файл не найден")

            # Загружаем файл с новым именем
            response = supabase.storage.from_(BUCKET_NAME).upload(new_name, file_data)
            if response.get("status", 400) != 200:
                raise HTTPException(status_code=500, detail="Ошибка переименования файла")

            # Удаляем старый файл
            await SupabaseStorage.delete_file(old_name)
            return f"{settings.SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{new_name}"
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


supabase_storage = SupabaseStorage()