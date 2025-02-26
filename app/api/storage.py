import tempfile
import logging
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
    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=f".{file.filename.split('.')[-1] if '.' in file.filename else 'tmp'}"
        ) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        file_name = file.filename
        await SupabaseStorage.upload_file(tmp_path, file_name, current_user.id)        
        return {"message": "Successful file added"}
    except HTTPException as e:
        raise 
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Ошибка загрузки файла: {str(e)}"
        )

# @router.delete("/delete/{file_name}")
# async def delete_file(file_name: str = Path(..., title="Имя файла для удаления", description="Имя файла, который нужно удалить")):
#     """
#     Удаляет файл из Supabase Storage.

#     Args:
#         file_name: Имя файла в хранилище.

#     Returns:
#         dict: Подтверждение успешного удаления.

#     Raises:
#         HTTPException: Если файл не найден или удаление не удалось.
#     """
#     try:
#         success = await SupabaseStorage.delete_file(file_name)
#         if not success:
#             logger.warning(f"Попытка удалить несуществующий файл: {file_name}")
#             raise HTTPException(status_code=404, detail="Файл не найден или ошибка удаления")
#         logger.info(f"Файл {file_name} успешно удалён")
#         return {"message": "Файл успешно удалён"}
#     except HTTPException as e:
#         raise
#     except Exception as e:
#         logger.error(f"Неизвестная ошибка при удалении файла {file_name}: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Ошибка удаления файла: {str(e)}")

@router.post("/rename")
async def rename_file(old_name: str, new_name: str):
    """
    Переименовывает файл в Supabase Storage.

    Args:
        old_name: Текушее имя файла.
        new_name: Новое имя файла.

    Returns:
        dict: Публичная ссылка на переименованный файл.

    Raises:
        HTTPException: Если переименование не удалось.
    """
    try:
        public_url = await SupabaseStorage.rename_file(old_name, new_name)
        if not public_url:
            logger.warning(f"Попытка переименовать несуществующий файл: {old_name}")
            raise HTTPException(status_code=404, detail="Ошибка переименования файла")
        logger.info(f"Файл переименован: {old_name} -> {new_name}, URL: {public_url}")
        return {"url": public_url}
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Неизвестная ошибка при переименовании файла {old_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка переименования файла: {str(e)}")