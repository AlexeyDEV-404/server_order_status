from fastapi import APIRouter, Depends, HTTPException

from app.core.exception import SkillsError
from app.dependencies.deps import skills_service_orm, skills_service
from app.services.skills_case import SkillsService, SkillsServiceORM
from app.shemas.shemas import SkillsValidNoID


router = APIRouter(prefix="/catalog_skills", tags=["catalog_skills"])


@router.post("/add", status_code=201)  # есть тест
async def add(
    data: SkillsValidNoID,
    service_deps: SkillsServiceORM = Depends(skills_service_orm)
        ):
    """
    Добавить категорию и услугу в каталог выполняемых работ
    """
    try:
        return await service_deps.add(
            category=data.category, service=data.service)
    except SkillsError:
        raise HTTPException(
            status_code=409, detail="Error: Skills already exists")


@router.get("/all_table")  # есть тест
async def all_table(
    service: SkillsService = Depends(skills_service)
):
    """
    Получить каталог всех выполняемых услуг/видов работ.
    """
    result = await service.get_all_table()

    if result or result not in [[], {}, None, ""]:
        return result
    else:
        raise HTTPException(status_code=404, detail="Data not Found")
