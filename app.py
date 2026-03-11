from flask import Flask, jsonify, request, render_template
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gift.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS gifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            total_qty INTEGER NOT NULL DEFAULT 0,
            remaining_qty INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            manager TEXT NOT NULL,
            client TEXT NOT NULL,
            gift_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (gift_id) REFERENCES gifts(id)
        );

        INSERT OR IGNORE INTO gifts (id, name, total_qty, remaining_qty) VALUES
            (1, '장패드',    50,  45),
            (2, '보온보냉백', 100, 68),
            (3, '수건',     200, 159),
            (4, '디퓨저',    30,  26),
            (5, '파우치',    88,  86);
    ''')
    conn.commit()
    conn.close()


# ── 재고 API ──────────────────────────────────────────────

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    conn = get_db()
    rows = conn.execute('SELECT * FROM gifts ORDER BY id').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/inventory/<int:gift_id>', methods=['PUT'])
def update_inventory(gift_id):
    data = request.get_json()
    if data is None:
        return jsonify({'error': '잘못된 요청'}), 400
    conn = get_db()
    conn.execute(
        'UPDATE gifts SET total_qty=?, remaining_qty=? WHERE id=?',
        (data['total_qty'], data['remaining_qty'], gift_id)
    )
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


# ── 반출 기록 API ─────────────────────────────────────────

@app.route('/api/records', methods=['GET'])
def get_records():
    conn = get_db()
    rows = conn.execute('''
        SELECT r.id, r.date, r.manager, r.client,
               r.gift_id, g.name AS gift_name,
               r.quantity, r.created_at
        FROM records r
        JOIN gifts g ON r.gift_id = g.id
        ORDER BY r.id DESC
    ''').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/records', methods=['POST'])
def add_record():
    data = request.get_json()
    if data is None:
        return jsonify({'error': '잘못된 요청'}), 400
    conn = get_db()

    # 잔여 수량 확인
    gift = conn.execute(
        'SELECT remaining_qty FROM gifts WHERE id=?', (data['gift_id'],)
    ).fetchone()
    if not gift or gift['remaining_qty'] < data['quantity']:
        conn.close()
        return jsonify({'error': '재고 부족'}), 400

    cursor = conn.execute(
        '''INSERT INTO records (date, manager, client, gift_id, quantity, created_at)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (data['date'], data['manager'], data['client'],
         data['gift_id'], data['quantity'], datetime.now().isoformat())
    )
    conn.execute(
        'UPDATE gifts SET remaining_qty = remaining_qty - ? WHERE id=?',
        (data['quantity'], data['gift_id'])
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': new_id, 'ok': True}), 201


@app.route('/api/records/<int:record_id>', methods=['PUT'])
def update_record(record_id):
    data = request.get_json()
    if data is None:
        return jsonify({'error': '잘못된 요청'}), 400
    conn = get_db()

    old = conn.execute(
        'SELECT gift_id, quantity FROM records WHERE id=?', (record_id,)
    ).fetchone()
    if not old:
        conn.close()
        return jsonify({'error': '기록 없음'}), 404

    # 재고 롤백 후 재적용
    conn.execute(
        'UPDATE gifts SET remaining_qty = remaining_qty + ? WHERE id=?',
        (old['quantity'], old['gift_id'])
    )
    conn.execute(
        'UPDATE gifts SET remaining_qty = remaining_qty - ? WHERE id=?',
        (data['quantity'], data['gift_id'])
    )
    conn.execute(
        '''UPDATE records
           SET date=?, manager=?, client=?, gift_id=?, quantity=?
           WHERE id=?''',
        (data['date'], data['manager'], data['client'],
         data['gift_id'], data['quantity'], record_id)
    )
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


@app.route('/api/records/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    conn = get_db()
    old = conn.execute(
        'SELECT gift_id, quantity FROM records WHERE id=?', (record_id,)
    ).fetchone()
    if not old:
        conn.close()
        return jsonify({'error': '기록 없음'}), 404

    conn.execute(
        'UPDATE gifts SET remaining_qty = remaining_qty + ? WHERE id=?',
        (old['quantity'], old['gift_id'])
    )
    conn.execute('DELETE FROM records WHERE id=?', (record_id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


@app.route('/')
def index():
    return render_template('index.html')


init_db()

if __name__ == '__main__':
    print("서버 시작: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
