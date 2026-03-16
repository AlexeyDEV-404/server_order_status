from database.doman_rules import rowcount_examinator, free_status_master_examination_0, chek_fetchone_master_order_count, chek_select_fetchone
import pytest

@pytest.mark.parametrize("rowcount, excepted", [
    (1,  "Обновление успешно"),
    (3,  "Обновление успешно"),
    (10,  "Обновление успешно")
])
def test_rowcount_examinator(rowcount, excepted):
    result = rowcount_examinator(rowcount)
    assert result == excepted

@pytest.mark.parametrize("rowcount", [0, -1, -20])
def test_rowcount_examinator_raise(rowcount):
    with pytest.raises(ValueError):
        rowcount_examinator(rowcount)

@pytest.mark.parametrize("data, excepted", [(("FREE",), "FREE")])
def test_free_status_master_examination_0(data, excepted):
    result = free_status_master_examination_0(data)
    assert result == excepted

@pytest.mark.parametrize("data", [("NEW",)])
def test_free_status_master_examination_0_raise(data):
    with pytest.raises(ValueError):
        free_status_master_examination_0(data)

@pytest.mark.parametrize("fetchone", [None])
def test_chek_select_fetchone_raise(fetchone):
    with pytest.raises(ValueError):
        chek_select_fetchone(fetchone) 

@pytest.mark.parametrize("fetchone", [("aaaa"), ("bbbb"), ("cccc")])
def test_chek_select_fetchone_tru(fetchone):
    assert chek_select_fetchone(fetchone) 

@pytest.mark.parametrize("fetchone", [1, 5, 20])
def test_chek_fetchone_master_order(fetchone):
    with pytest.raises(ValueError):
        chek_fetchone_master_order_count(fetchone)

def test_chek_fetchone_master_order_free():
    chek_fetchone_master_order_count(0) 

