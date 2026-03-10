"""
구글 시트 CSV → SQLite 이전 스크립트

사용법:
  1. 구글 시트 → 파일 → 다운로드 → CSV 선택
  2. 다운로드된 파일을 이 스크립트와 같은 폴더에 놓기
  3. python import_csv.py 파일명.csv
"""
import csv
import sys
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gift.db')

GIFT_NAME_MAP = {
    '장패드':    1,
    '보온보냉백': 2,
    '수건':      3,
    '디퓨저':    4,
    '파우치':    5,
}


def import_csv(filepath):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    with open(filepath, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        success, skip = 0, 0
        for row in reader:
            # 빈 행 건너뜀
            if not row.get('날짜', '').strip():
                skip += 1
                continue

            # 날짜 정규화 (1-22 → 2026-01-22)
            raw_date = row.get('날짜', '').strip()
            if len(raw_date) <= 4 and '-' in raw_date:
                m, d = raw_date.split('-')
                date = f"2026-{int(m):02d}-{int(d):02d}"
            else:
                date = raw_date

            gift_name = row.get('기프트 품목', '').strip()
            gift_id = GIFT_NAME_MAP.get(gift_name)
            if not gift_id:
                print(f"  ⚠ 알 수 없는 품목: '{gift_name}' (행 건너뜀)")
                skip += 1
                continue

            try:
                qty = int(row.get('수량', '0').strip())
            except ValueError:
                skip += 1
                continue

            conn.execute(
                '''INSERT INTO records (date, manager, client, gift_id, quantity, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (date,
                 row.get('담당자', '').strip(),
                 row.get('고객사(고객명)', '').strip(),
                 gift_id, qty,
                 datetime.now().isoformat())
            )
            success += 1

    conn.commit()
    conn.close()
    print(f"✅ 이전 완료: {success}건 성공, {skip}건 건너뜀")
    print("ℹ  재고 잔여 수량은 DB 초기값(시트 기준)을 유지합니다.")
    print("   기록 이전은 히스토리 조회용이며, 재고는 별도로 관리됩니다.")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("사용법: python import_csv.py 파일명.csv")
        sys.exit(1)
    import_csv(sys.argv[1])
