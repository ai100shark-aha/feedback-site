# 학번 자동 수정 스크립트 v2 (이름 기반 - 전체 반 검색)
# 번호 오류(155건) 포함, 전체 반에서 이름으로 학번을 찾아 수정합니다.

import openpyxl
import gspread
from google.oauth2.service_account import Credentials
import os, sys

# ── 설정 ─────────────────────────────────────────────────────────
_BASE            = os.path.dirname(os.path.abspath(__file__))
XLSX_PATH        = os.path.join(_BASE, '그룹명단 (1).xlsx')
CREDENTIALS_PATH = os.path.join(_BASE, 'credentials.json')
SHEET_KEY        = '1A7awsXWOu-WPiRjY6vk8rPEhBh8PpGiTp3pGAlellsM'
DRY_RUN          = False   # True → 목록만 출력, 실제 변경 없음
# ─────────────────────────────────────────────────────────────────

CLASS_NAME_TO_CODE = {
    '8반': '108', '9반': '109', '10반': '110',
    '11반': '111', '12반': '112', '13반': '113',
}

VALID_IDS = set(
    f'{cls}{num:02d}'
    for cls, count in [('108', 30), ('109', 30), ('110', 30),
                       ('111', 30), ('112', 29), ('113', 29)]
    for num in range(1, count + 1)
)


def get_class_code_from_title(title):
    for name, code in CLASS_NAME_TO_CODE.items():
        if name in str(title):
            return code
    return None


def load_name_map(xlsx_path):
    """
    두 가지 딕셔너리 반환:
      class_map : (class_code, 이름) → 학번
      all_map   : 이름 → [학번, ...]  (전체 반 검색용)
    """
    wb = openpyxl.load_workbook(xlsx_path)
    ws = wb.active
    class_map = {}
    all_map   = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        sid, name = row
        if not sid or not name or not isinstance(sid, int):
            continue
        sid_str    = str(sid)
        class_code = sid_str[:3]
        name_str   = str(name).strip()
        class_map[(class_code, name_str)] = sid_str
        all_map.setdefault(name_str, []).append(sid_str)
    print(f"✓ 학생 명단 로드: {len(class_map)}명")
    return class_map, all_map


def find_correct_id(class_map, all_map, class_code, student_name, entered_id):
    """
    올바른 학번 탐색 순서:
    1. (수업반, 이름) → 같은 반 학생
    2. (입력학번 앞3자리 반, 이름) → 학생이 자기 반 ID를 입력한 경우
    3. 전체 반에서 이름 검색 (유일하면 확정)
    반환: (correct_id, 비고) 또는 (None, 비고)
    """
    # 1. 같은 반에서 이름 검색
    sid = class_map.get((class_code, student_name))
    if sid:
        return sid, '같은 반'

    # 2. 입력 학번 앞 3자리로 반 추정
    if len(entered_id) >= 3:
        hint_code = entered_id[:3]
        if hint_code in CLASS_NAME_TO_CODE.values():
            sid = class_map.get((hint_code, student_name))
            if sid:
                return sid, f'입력학번 기준 ({hint_code}반)'

    # 3. 전체 반 검색
    matches = all_map.get(student_name, [])
    if len(matches) == 1:
        return matches[0], '전체반 검색(유일)'
    elif len(matches) > 1:
        # 중복 이름: 입력된 학번과 가장 유사한 것 선택
        if entered_id in matches:
            return entered_id, None  # 이미 맞음
        # 입력 학번 앞 3자리 일치하는 것 우선
        for m in matches:
            if m[:3] == entered_id[:3]:
                return m, f'중복이름-앞자리 일치({m})'
        return None, f'중복이름 구분불가: {matches}'

    return None, '명단에 없는 이름'


def get_sheet():
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=scope)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_KEY).sheet1


def main():
    global XLSX_PATH

    print("=" * 65)
    print("학번 자동 수정 스크립트 v2 (전체 반 이름 검색)")
    print(f"DRY_RUN = {DRY_RUN}")
    print("=" * 65)

    # 파일 경로 확인
    if not os.path.isfile(XLSX_PATH):
        print(f"\n[오류] 엑셀 파일 없음: {XLSX_PATH}")
        path_input = input("그룹명단 엑셀 전체 경로 입력: ").strip().strip('"')
        if not os.path.isfile(path_input):
            print(f"[오류] 파일이 없습니다: {path_input}")
            sys.exit(1)
        XLSX_PATH = path_input

    if not os.path.isfile(CREDENTIALS_PATH):
        print(f"[오류] credentials.json 없음: {CREDENTIALS_PATH}")
        sys.exit(1)

    # 1. 명단 로드
    class_map, all_map = load_name_map(XLSX_PATH)

    # 2. 시트 읽기
    print("\n구글 시트 연결 중...")
    sheet     = get_sheet()
    all_rows  = sheet.get_all_values()
    data_rows = all_rows[1:] if len(all_rows) > 1 else []
    print(f"✓ 전체 행 수: {len(data_rows)}행")

    # 3. 각 행 검사
    # 시트 컬럼: [0]날짜 [1]수업명 [2]학번 [3]번호 [4]이름 [5..]피드백
    fixes        = []   # 수정 가능
    ambiguous    = []   # 이름 중복 등으로 확정 불가
    not_in_list  = []   # 명단에 없는 이름

    for i, row in enumerate(data_rows, start=2):
        if len(row) < 5:
            continue
        title        = row[1].strip()
        entered_id   = row[2].strip()
        student_num  = row[3].strip()
        student_name = row[4].strip()

        if not entered_id or not student_name:
            continue

        class_code = get_class_code_from_title(title)
        if not class_code:
            continue

        # 번호 기반 예상 학번
        expected_by_num = None
        try:
            n = int(student_num)
            candidate = f'{class_code}{n:02d}'
            if candidate in VALID_IDS:
                expected_by_num = candidate
        except Exception:
            pass

        # 이미 정상인 경우 건너뜀
        if entered_id == expected_by_num:
            continue

        # 학번이 유효 학번 집합에 있고 수업반과 일치하면 정상
        if entered_id in VALID_IDS and entered_id[:3] == class_code:
            continue

        # 이름으로 올바른 학번 탐색
        correct_id, note = find_correct_id(
            class_map, all_map, class_code, student_name, entered_id
        )

        if correct_id is None:
            if note and '중복' in note:
                ambiguous.append({'row': i, 'title': title, 'name': student_name,
                                  'entered': entered_id, 'note': note})
            else:
                not_in_list.append({'row': i, 'title': title, 'name': student_name,
                                    'entered': entered_id})
            continue

        if correct_id == entered_id:
            continue   # 이미 맞음

        fixes.append({
            'row':    i,
            'title':  title,
            'name':   student_name,
            'old_id': entered_id,
            'new_id': correct_id,
            'note':   note,
        })

    # 4. 결과 출력
    print(f"\n{'='*65}")
    print(f"수정 가능:   {len(fixes):>4}건")
    print(f"중복이름:    {len(ambiguous):>4}건 (수동 확인 필요)")
    print(f"명단 없음:   {len(not_in_list):>4}건 (이름 잘못 입력 등)")
    print(f"{'='*65}")

    if fixes:
        print(f"\n[수정 대상]")
        print(f"{'행':<5} {'차시':<16} {'이름':<8} {'기존학번':<10} {'→'} {'정정학번':<8} 비고")
        print("-" * 68)
        for f in fixes:
            print(f"  {f['row']:<4} {f['title']:<16} {f['name']:<8} "
                  f"{f['old_id']:<10} → {f['new_id']:<8} ({f['note']})")

    if ambiguous:
        print(f"\n[중복 이름 - 수동 확인]")
        for a in ambiguous:
            print(f"  행{a['row']} {a['name']} ({a['title']}): {a['note']}")

    if not_in_list:
        print(f"\n[명단에 없는 이름 - 확인 필요]")
        for n in not_in_list:
            print(f"  행{n['row']} '{n['name']}' ({n['title']}) 입력학번={n['entered']}")

    # 5. 실제 수정
    if not fixes:
        print("\n✅ 자동 수정할 항목이 없습니다.")
        return

    if DRY_RUN:
        print(f"\n[DRY_RUN] 실제 수정 안 함. DRY_RUN=False 후 재실행하세요.")
        return

    confirm = input(f"\n{len(fixes)}건을 수정하시겠습니까? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("취소되었습니다.")
        return

    print("\n수정 중...")
    for f in fixes:
        sheet.update_cell(f['row'], 3, f['new_id'])   # C열 = 학번
        print(f"  ✓ 행{f['row']} {f['name']}: {f['old_id']} → {f['new_id']}")

    print(f"\n✅ 완료: {len(fixes)}건 수정되었습니다.")
    if ambiguous or not_in_list:
        print(f"⚠  {len(ambiguous)+len(not_in_list)}건은 수동 확인이 필요합니다.")


if __name__ == '__main__':
    main()
