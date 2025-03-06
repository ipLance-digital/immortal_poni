import tempfile
import logging
from uuid import UUID

from app.api.auth import get_current_user
from app.models.users import Users
from app.services.storage import SupabaseStorage
from fastapi import (
    APIRouter,
    Depends,
    HTTPException, 
    UploadFile, 
    File,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: Users = Depends(get_current_user)
):
    """
        Загружает файл с привязкой к авторизации.
    """
    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=f".{file.filename.split('.')[-1] if '.' in file.filename else 'tmp'}"
        ) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        file_name = file.filename
        file_id = await SupabaseStorage.upload_file(
            tmp_path,
            file_name,
            current_user.id
        )
        logger.info(f"file_id: {file_id}")
        return {"message": f"Successful file (file_id: {file_id}) added"}
    except HTTPException as e:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка загрузки файла: {str(e)}"
        )

@router.delete("/delete/{file_uuid}")
async def delete_file(
    file_uuid: UUID,
    current_user: Users = Depends(get_current_user)
):
    """
        Удаляет файл из Supabase Storage и базы данных.
    """
    try:
        await SupabaseStorage.delete_file(file_uuid, current_user.id)
        return {
            "message": f"Successful file (file_id: {file_uuid}) deleted"
        }
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Ошибка удаления файла: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка удаления файла: {str(e)}"
        )

@router.patch("/rename/{file_uuid}")
async def rename_file(
        file_uuid: UUID,
        new_name: str,
        current_user: Users = Depends(get_current_user)
):
    """
        Переименовывает файл.
    """
    try:
        await SupabaseStorage.rename_file(
            file_uuid,
            current_user.id,
            new_name
        )
        return {"message": f"Successful rename file (file_id: {file_uuid})"}
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Ошибка переименования файла: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка переименования файла: {str(e)}"
        )
