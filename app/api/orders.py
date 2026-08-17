from fastapi import APIRouter, Depends, HTTPException
from app.core.exception import MasterStatusError
from app.models.enum_model import StatusOrders
from app.shemas.shemas import (
    ParamsLifeCycle)
from app.services.orders_case import (
    OrderQueryService,
    OrderCommandService)
from app.dependencies.deps import (
    order_query_service,
    order_command_service,
    params_life_cycle)


router = APIRouter(prefix="/order", tags=["order"])


@router.get("/{order_id}")
async def get_order(
    order_id: int,
    service: OrderQueryService = Depends(order_query_service)
        ):
    """
    Получить информацию об одном заказе
    """
    result = await service.get_inf_order(order_id=order_id)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Informations not found.")


@router.post("/create", status_code=201)
async def create_order(
    skill_id: int, description: str,
    service: OrderQueryService = Depends(order_query_service)
        ):
    """
    Создать один заказ
    """
    result = await service.post_in_db(
        skill_id=skill_id, description=description)
    if result:
        return result
    else:
        raise HTTPException(status_code=422, detail="Failed to create order")


@router.patch("/assign")
async def assign(
        params: ParamsLifeCycle = Depends(params_life_cycle),
        service: OrderCommandService = Depends(order_command_service)
        ):
    """
    Перевести заказ из новых в "назначенный". Данный статус, означает
    что мастер уже назначен на заказ.
    """
    try:
        return await service.order_lifecycle(
            new_status=StatusOrders.ASSIGNED,
            order_id=params.order_id, master_id=params.master_id)
    except MasterStatusError:
        raise HTTPException(
            status_code=409,
            detail="Error: The master is busy and cannot take order")


@router.patch("/in_progress")
async def in_progress(
    params: ParamsLifeCycle = Depends(params_life_cycle),
    service: OrderCommandService = Depends(order_command_service)
        ):
    """
    Заказ находится в процессе выполнения и поэтому получает статус
    IN_PROGRESS.
    """
    result = await service.order_lifecycle(
        new_status=StatusOrders.IN_PROGRESS,
        order_id=params.order_id, master_id=params.master_id)
    if result:
        return result
    else:
        raise HTTPException(status_code=500, detail="Непредвиденная ошибка")


@router.patch("/completed")
async def completed(
    params: ParamsLifeCycle = Depends(params_life_cycle),
    service: OrderCommandService = Depends(order_command_service)
        ):
    """
    Заказ полностью выполнен.
    """
    try:
        return await service.order_lifecycle(
            new_status=StatusOrders.COMPLETED,
            order_id=params.order_id, master_id=params.master_id)
    except MasterStatusError:
        raise HTTPException(
            status_code=409, detail="Error: Master status already FREE")


@router.patch("/cancel")
async def cancel(
    params: ParamsLifeCycle = Depends(params_life_cycle),
    service: OrderCommandService = Depends(order_command_service)
        ):
    """
    Заказ отменен и получает статус "cancel". Отменить заказ можно только если:
    это "новый" или "назначен" мастер, со статуса "в процессе выполнение"
    отмена запрещена.
    """
    result = await service.order_lifecycle(
        new_status=StatusOrders.CANCEL,
        order_id=params.order_id, master_id=params.master_id)
    if result:
        return result
    else:
        raise HTTPException(status_code=404)


@router.delete("/delete")
async def delete_order(
    order_id: int,
    service: OrderCommandService = Depends(order_command_service)
        ):
    """
    Удаление заказа с базы данный.
    ОГРАНИЧЕННЫЙ ДОСТУП!!!    """
    return await service.delete(order_id)
