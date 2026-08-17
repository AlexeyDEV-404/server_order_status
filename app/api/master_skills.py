from fastapi import APIRouter, Depends, HTTPException

from app.dependencies.deps import master_skills_service
from app.services.master_skills_case import MasterSkillsQueryService
from app.shemas.shemas import MasterSkillValid

router = APIRouter(prefix="/master_skills", tags=["master_skills"])


@router.post("/add", status_code=201)  # есть тест
async def add_skills(
    data: MasterSkillValid,
    service: MasterSkillsQueryService = Depends(master_skills_service)
        ):
    """
    Добавить мастеру навыки/виды выполняемых им, работ.
    ОГРАНИЧЕННЫЙ ДОСТУП!!!
    """
    try:
        return await service.add(
            master_id=data.master_id, skill_id=data.skill_id)
    except ValueError:
        HTTPException(
            status_code=409, detail="Такая связь мастер-навык уже существует")
