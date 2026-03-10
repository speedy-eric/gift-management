import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app as flask_app


@pytest.fixture
def client(tmp_path):
    """각 테스트마다 임시 DB 사용"""
    test_db = str(tmp_path / 'test.db')
    flask_app.DB_PATH = test_db
    flask_app.app.config['TESTING'] = True
    flask_app.init_db()
    with flask_app.app.test_client() as c:
        yield c


# ── 재고 조회 ──────────────────────────────────────────

def test_get_inventory_returns_5_items(client):
    res = client.get('/api/inventory')
    data = res.get_json()
    assert res.status_code == 200
    assert len(data) == 5


def test_inventory_has_correct_names(client):
    res = client.get('/api/inventory')
    names = [g['name'] for g in res.get_json()]
    assert '장패드' in names
    assert '보온보냉백' in names
    assert '수건' in names
    assert '디퓨저' in names
    assert '파우치' in names


# ── 반출 기록 추가 ─────────────────────────────────────

def test_add_record_success(client):
    payload = {
        'date': '2026-03-10',
        'manager': '이기룡',
        'client': '테스트고객사',
        'gift_id': 3,   # 수건 (잔여 159)
        'quantity': 2
    }
    res = client.post('/api/records', json=payload)
    assert res.status_code == 201
    assert res.get_json()['ok'] is True


def test_add_record_reduces_inventory(client):
    # 수건 잔여: 159 → 154
    before = next(g for g in client.get('/api/inventory').get_json() if g['id'] == 3)
    client.post('/api/records', json={
        'date': '2026-03-10', 'manager': '홍성민',
        'client': '다이노즈', 'gift_id': 3, 'quantity': 5
    })
    after = next(g for g in client.get('/api/inventory').get_json() if g['id'] == 3)
    assert after['remaining_qty'] == before['remaining_qty'] - 5


def test_add_record_fails_on_insufficient_stock(client):
    res = client.post('/api/records', json={
        'date': '2026-03-10', 'manager': '홍성민',
        'client': '다이노즈', 'gift_id': 1, 'quantity': 9999
    })
    assert res.status_code == 400
    assert 'error' in res.get_json()


# ── 반출 기록 수정 ─────────────────────────────────────

def test_update_record(client):
    # 먼저 등록
    add = client.post('/api/records', json={
        'date': '2026-03-10', 'manager': '전현준',
        'client': '임직원배포', 'gift_id': 3, 'quantity': 2
    })
    rec_id = add.get_json()['id']

    # 수정 (수량 2 → 1)
    res = client.put(f'/api/records/{rec_id}', json={
        'date': '2026-03-10', 'manager': '전현준',
        'client': '임직원배포', 'gift_id': 3, 'quantity': 1
    })
    assert res.status_code == 200
    assert res.get_json()['ok'] is True

    # 재고 확인: 초기 159, -2 → 157, 수정 후 +2-1 = 158
    inv = next(g for g in client.get('/api/inventory').get_json() if g['id'] == 3)
    assert inv['remaining_qty'] == 158


# ── 반출 기록 삭제 ─────────────────────────────────────

def test_delete_record_restores_inventory(client):
    add = client.post('/api/records', json={
        'date': '2026-03-10', 'manager': '이기룡',
        'client': '예별손해보험', 'gift_id': 2, 'quantity': 3
    })
    rec_id = add.get_json()['id']
    before = next(g for g in client.get('/api/inventory').get_json() if g['id'] == 2)

    client.delete(f'/api/records/{rec_id}')

    after = next(g for g in client.get('/api/inventory').get_json() if g['id'] == 2)
    assert after['remaining_qty'] == before['remaining_qty'] + 3


def test_delete_nonexistent_record(client):
    res = client.delete('/api/records/99999')
    assert res.status_code == 404


# ── 기록 목록 조회 ─────────────────────────────────────

def test_get_records_includes_gift_name(client):
    client.post('/api/records', json={
        'date': '2026-03-10', 'manager': '홍성민',
        'client': '유비온', 'gift_id': 4, 'quantity': 1
    })
    res = client.get('/api/records')
    records = res.get_json()
    assert len(records) >= 1
    assert 'gift_name' in records[0]
    assert records[0]['gift_name'] == '디퓨저'
