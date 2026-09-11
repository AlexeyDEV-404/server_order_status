from app.repositories.master_list_rep import MasterListRep
from app.models.enum_model import StatusMasterCheck
import pytest


async def test_add_master(asession, repo, one_master):
    # async with asession.begin_nested() as trans:
    #     print(f'ID TRANSACTION {id(trans)} and ID SESSION {id(asession)} THIS TEST')
    #     req = repo.master_list.add_master(name="Test_name", status=StatusMasterCheck.FREE)
    assert one_master.name == "Test_name"
    assert one_master.id is not None
    assert one_master.status == StatusMasterCheck.FREE

