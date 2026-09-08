# flake8: noqa
import pytest
from httpx2 import ASGITransport, AsyncClient

from app.dependencies.deps import uow
from app.helper.help import Repository
from app.models.enum_model import StatusMasterCheck, StatusOrders
from app.models.models import Base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.database import settings
from app.services.orders_case import OrderCommandService
from app.main import app
from app.shemas.shemas import (
    MastListValid)
