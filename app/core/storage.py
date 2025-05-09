from datetime import datetime
from uuid import UUID
import uuid

from sqlalchemy import delete, select
from supabase import create_client, Client
from fastapi import HTTPException
from typing import Optional
from app.core.database import PgSingleton
from app.models.files import Files
import logging
from dotenv import load_dotenv
import os

load_dotenv()
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY"),
)
bucket_name = os.getenv("BUCKET_NAME")


class SupabaseStorage:
    @staticmethod
    async def upload_file(
        file_obj,
        file_name: str,
        user_id: uuid.UUID,
        file_size,
        content_type: str = "application/octet-stream",
    ) -> Optional[str]:
        try:
            file_id = str(uuid.uuid4())
            supabase.storage.from_(bucket_name).upload(
                path=file_id,
                file=file_obj,
                file_options={"content-type": content_type, "upsert": False},
            )
            async with PgSingleton().session as db:
                file_record = Files(
                    id=uuid.UUID(file_id),
                    file_name=file_name,
                    file_size=file_size,
                    created_by=user_id,
                    created_at=datetime.now(),
                )
                db.add(file_record)
                await db.commit()

            return file_id

        except Exception as e:
            print(f"Error uploading file: {str(e)}")
            return None

    @staticmethod
    async def delete_file(file_uuid: UUID, user_id: UUID):
        """
        Удаляет файл из Supabase Storage и базы данных.
        """
        try:
            async with PgSingleton().session as db:
                file_record = await db.execute(
                    select(Files).where(
                        Files.id == file_uuid, Files.created_by == user_id
                    )
                )
                file_record = file_record.scalars().first()
                if not file_record:
                    return False
                supabase.storage.from_(bucket_name).remove([str(file_uuid)])
                stmt = delete(Files).where(Files.id == file_uuid)
                await db.execute(stmt)
                await db.commit()

        except Exception as e:
            logging.error(f"Ошибка при удалении файла: {e}")
            return False

    @staticmethod
    async def rename_file(
        file_uuid: UUID, user_id: UUID, new_name: str
    ) -> Optional[str]:
        """
        Переименовывает файл
        """
        try:
            async with PgSingleton().session as db:
                file_record = await db.execute(
                    select(Files).where(
                        Files.id == file_uuid, Files.created_by == user_id
                    )
                )
                file_record = file_record.scalars().first()
                if not file_record:
                    raise HTTPException(status_code=404, detail="Файл не найден")
                file_record.file_name = new_name
                db.add(file_record)
                await db.commit()
                await db.refresh(file_record)
                return new_name

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
