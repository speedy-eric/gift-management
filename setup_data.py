"""
DB 초기화 + 기존 구글 시트 데이터 입력 스크립트
실행: python setup_data.py
"""
import sqlite3, os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gift.db')

# DB 삭제 후 재생성
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("기존 DB 삭제 완료")

conn = sqlite3.connect(DB_PATH)
conn.executescript('''
    CREATE TABLE gifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        total_qty INTEGER NOT NULL DEFAULT 0,
        remaining_qty INTEGER NOT NULL DEFAULT 0
    );
    CREATE TABLE records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        manager TEXT NOT NULL,
        client TEXT NOT NULL,
        gift_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (gift_id) REFERENCES gifts(id)
    );
    -- 재고: 스프레드시트 기준 정확한 수량
    INSERT INTO gifts (id, name, total_qty, remaining_qty) VALUES
        (1, '장패드',    50,  45),
        (2, '보온보냉백', 100, 68),
        (3, '수건',     200, 159),
        (4, '디퓨저',    30,  26),
        (5, '파우치',    88,  86);
''')

# gift_id: 1=장패드 2=보온보냉백 3=수건 4=디퓨저 5=파우치
records = [
    # No.1
    ('2026-01-22', '전현준', '임직원 배포',     3, 9),
    # No.2
    ('2026-01-22', '이기룡', '글로브포인트',    3, 2),
    # No.3
    ('2026-01-22', '이기룡', '글로브포인트',    2, 2),
    # No.4
    ('2026-01-28', '이기룡', '예별손해보험',    3, 2),
    # No.5
    ('2026-01-28', '이기룡', '예별손해보험',    2, 2),
    # No.6
    ('2026-01-28', '홍성민', '유비온',          3, 1),
    # No.7
    ('2026-01-28', '홍성민', '유비온',          2, 1),
    # No.8
    ('2026-01-29', '홍성민', '다이노즈/키즐판사', 2, 2),
    # No.9
    ('2026-01-29', '홍성민', '다이노즈/키즐판사', 3, 2),
    # No.10
    ('2026-01-29', '이기룡', 'E1',              3, 2),
    # No.11
    ('2026-01-29', '이기룡', 'E1',              2, 2),
    # No.12
    ('2026-01-29', '이기룡', 'E1',              4, 2),
    # No.13
    ('2026-01-29', '이기룡', 'E1',              5, 2),
    # No.14
    ('2026-01-30', '이기룡', '지란지교시큐리티',  3, 1),
    # No.15
    ('2026-01-30', '이기룡', '지란지교시큐리티',  2, 1),
    # No.16
    ('2026-01-30', '이기룡', '넥스젠어쏘시에이트', 3, 1),
    # No.17
    ('2026-01-30', '이기룡', '넥스젠어쏘시에이트', 2, 1),
    # No.18
    ('2026-02-02', '이기룡', '지란지교시큐리티',  3, 2),
    # No.19
    ('2026-02-02', '이기룡', '지란지교시큐리티',  2, 2),
    # No.20
    ('2026-02-02', '이기룡', '지란지교시큐리티',  4, 2),
    # No.21
    ('2026-02-03', '이기룡', '농정원',           3, 2),
    # No.22
    ('2026-02-03', '이기룡', '농정원',           2, 2),
    # No.23
    ('2026-02-03', '이기룡', '농정원',           1, 2),
    # No.24
    ('2026-02-03', '이기룡', '인터모프',         3, 2),
    # No.25
    ('2026-02-03', '이기룡', '인터모프',         2, 2),
    # No.26
    ('2026-02-03', '이기룡', '인터모프',         1, 2),
    # No.27
    ('2026-02-09', '이기룡', '브레인즈컴퍼니',   2, 1),
    # No.28
    ('2026-02-09', '이기룡', '브레인즈컴퍼니',   1, 1),
    # No.29
    ('2026-02-10', '이기룡', 'NHN클라우드',      2, 2),
    # No.30
    ('2026-02-10', '이기룡', 'NHN클라우드',      3, 2),
    # No.31
    ('2026-02-10', '이기룡', '소원엔티',         2, 2),
    # No.32
    ('2026-02-10', '이기룡', '소원엔티',         3, 2),
    # No.33
    ('2026-02-10', '이기룡', '소원엔티',         2, 2),
    # No.34
    ('2026-02-10', '대포님', '일제',             3, 5),
    # No.35
    ('2026-02-10', '대포님', '일제',             2, 5),
    # No.36
    ('2026-02-24', '전현준', 'Fasty',            3, 2),
    # No.37
    ('2026-02-24', '전현준', 'Fasty',            2, 1),
    # No.38
    ('2026-02-24', '홍성민', '상상소료리',        3, 1),
    # No.39
    ('2026-03-04', '홍성민', '상상소료리',        3, 2),
    # No.40
    ('2026-03-04', '홍성민', '티모깃',           3, 2),
    # No.41
    ('2026-03-04', '홍성민', '티모깃',           2, 2),
]

ts = datetime.now().isoformat()
for r in records:
    conn.execute(
        'INSERT INTO records (date, manager, client, gift_id, quantity, created_at) VALUES (?, ?, ?, ?, ?, ?)',
        (r[0], r[1], r[2], r[3], r[4], ts)
    )

conn.commit()
conn.close()
print(f"완료: {len(records)}건 입력됨")
print("재고: 장패드 45/50, 보온보냉백 68/100, 수건 159/200, 디퓨저 26/30, 파우치 86/88")
