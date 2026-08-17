from app.services.master_list_case import MasterListQueryService
from app.dependencies.deps import master_list_service
from app.models.enum_model import StatusMasterCheck
from fastapi import APIRouter, Depends, HTTPException

from app.shemas.shemas import MastListValid, MastListValidNoID


router = APIRouter(prefix="/masters", tags=["masters"])


@router.get("/")
async def get_all_master_they_skills(
        service: MasterListQueryService = Depends(master_list_service)
):
    """
    Получить список всем мастеров с их навыками.
    """
    result = await service.all_table()
    if result or result not in [[], {}, None, ""]:
        return result
    else:
        raise HTTPException(status_code=404, detail="Not found")


@router.get("/search")
async def search_free_masters(
        status=StatusMasterCheck.FREE,
        service: MasterListQueryService = Depends(master_list_service)
        ) -> list[MastListValid]:
    """
    Поиск свободного мастера в таблице MasterList. Без релиционных связей,
    простое обращение в таблицу.
    """
    result = await service.all_free_master(status)
    if result or result not in [[], {}, None, ""]:
        return result
    else:
        raise HTTPException(status_code=404, detail="Not found")


@router.post("/create", status_code=201)  # есть тест
async def create_master(
    data: MastListValidNoID,
    service: MasterListQueryService = Depends(master_list_service)
        ):
    """
    Добавить (создать) мастера. ДОСТУП ДОЛЖЕН БЫТЬ ОГРАНИЧЕН.
    """
    result = await service.create(name=data.name, status=data.status)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Необрабатываемая ошибка")
