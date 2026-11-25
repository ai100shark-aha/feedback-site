"""연구용 학생 설문 (사전·사후)

- 학생: /survey/  → 학번·번호·이름 확인 후 5점 척도 15문항 + 서술 2문항, 차수(사전/사후)당 1회 제출
- 교사: /survey/teacher/ → 설문 열기(사전/사후)·닫기, 반별 응답 수, 문항별 평균 비교
- 저장: 스프레드시트 '설문' 탭(응답), '설문설정' 탭(A2 = 현재 열린 차수)
- 개인정보 분리: 학번·이름은 본인 확인에만 쓰고, 시트에는 이름 없이 학번을 바꾼 '응답코드'만 저장한다.
  같은 학번은 항상 같은 코드가 되므로 사전·사후 짝짓기와 중복 방지는 그대로 된다.
  (완전 익명은 아님: 비밀값을 아는 사람은 학번으로 코드를 다시 계산해 볼 수 있다.)
"""
import hashlib
import hmac
import os
import threading
from collections import defaultdict

from django.shortcuts import render, redirect

from . import views as V

SURVEY_SHEET = '설문'
SETTING_SHEET = '설문설정'
ROUNDS = ['사전', '사후']
CLOSED = '닫힘'

SCALE = [(1, '전혀 아니다'), (2, '아니다'), (3, '보통이다'), (4, '그렇다'), (5, '매우 그렇다')]

# (영역, 문항, 역문항 여부)
QUESTIONS = [
    ('수업 몰입', '정보 수업 시간에 수업 내용에 집중한다.', False),
    ('수업 몰입', '정보 수업 시간이 빨리 지나간다고 느낀다.', False),
    ('수업 몰입', '정보 수업에서 배우는 내용이 재미있다.', False),
    ('수업 시작', '정보실에 오면 수업 시작 전까지 수업과 관계없는 웹 서핑이나 동영상을 본다.', True),
    ('수업 시작', '수업이 시작되기 전에 지난 시간에 배운 내용을 떠올려 본다.', False),
    ('수업 시작', '수업 시작종이 울릴 때 수업을 들을 준비가 되어 있다.', False),
    ('복습·자기점검', '지난 시간에 배운 내용을 기억하고 있다.', False),
    ('복습·자기점검', '내가 무엇을 모르는지 스스로 알고 있다.', False),
    ('복습·자기점검', '모르는 내용이 있으면 교과서나 자료를 다시 찾아본다.', False),
    ('피드백 순환', '수업일지에 쓴 나의 질문이나 어려움이 수업에 반영된다고 느낀다.', False),
    ('피드백 순환', '‘지난주 돌아보기’가 배운 내용을 정리하는 데 도움이 된다.', False),
    ('피드백 순환', '수업일지를 쓰면 그날 배운 내용이 정리된다.', False),
    ('매일방탈출', '매일방탈출 덕분에 수업 시작 전에 복습하게 된다.', False),
    ('매일방탈출', '매일방탈출 문제는 내가 어려워했던 내용을 다룬다.', False),
    ('매일방탈출', '매일방탈출의 순위와 시상이 참여하고 싶은 마음을 만든다.', False),
]
OPEN_QUESTIONS = [
    '정보 수업이 시작되기 전, 정보실에서 주로 무엇을 하나요?',
    '수업일지·지난주 돌아보기·매일방탈출에서 좋았던 점이나 바꾸고 싶은 점을 자유롭게 적어 주세요.',
]
HEADER = (['제출시각(KST)', '차수', '응답코드', '반']
          + [f'Q{i}' for i in range(1, len(QUESTIONS) + 1)]
          + [f'서술{i}' for i in range(1, len(OPEN_QUESTIONS) + 1)])

N_META = 4   # 제출시각, 차수, 응답코드, 반
_lock = threading.Lock()
_round_cache = {'value': None}
_migrated = {'done': False}


def response_code(student_id):
    """학번 → 응답코드(10자리). 비밀값은 환경변수 SURVEY_SALT, 없으면 Django SECRET_KEY.
    ※ 운영 중에 비밀값을 바꾸면 사전·사후 코드가 달라져 짝짓기가 끊기므로 바꾸지 말 것."""
    from django.conf import settings
    salt = os.environ.get('SURVEY_SALT') or settings.SECRET_KEY
    return hmac.new(salt.encode(), str(student_id).strip().encode(), hashlib.sha256).hexdigest()[:10]


# ── 시트 ────────────────────────────────────────────────────────
def _ws(name, header):
    ss = V.get_sheet().spreadsheet
    try:
        return ss.worksheet(name)
    except Exception:
        ws = ss.add_worksheet(title=name, rows=1000, cols=max(len(header), 2))
        ws.append_row(header)
        return ws


def _survey_ws():
    ws = _ws(SURVEY_SHEET, HEADER)
    if not _migrated['done']:
        _migrate_identified_rows(ws)
        _migrated['done'] = True
    return ws


def _migrate_identified_rows(ws):
    """예전 형식(학번·번호·이름 저장) 응답이 있으면 이름을 지우고 응답코드로 바꿔 시트 전체를 다시 쓴다."""
    try:
        values = ws.get_all_values()
        if not values or len(values[0]) < 3 or values[0][2] != '학번':
            return
        new_rows = [HEADER]
        for r in values[1:]:
            if len(r) < 6:
                continue
            new_rows.append([r[0], r[1], response_code(r[2]), r[5]] + r[6:])
        ws.clear()
        ws.update(range_name='A1', values=new_rows)
        print(f"설문 응답 {len(new_rows) - 1}건을 응답코드 형식으로 변환함", flush=True)
    except Exception as e:
        print(f"설문 형식 변환 오류: {e}", flush=True)


def _setting_ws():
    return _ws(SETTING_SHEET, ['현재차수'])


def current_round():
    """현재 열린 차수('사전'/'사후') 또는 '닫힘'. 시트 값을 캐시해 둔다."""
    if _round_cache['value'] is not None:
        return _round_cache['value']
    value = CLOSED
    try:
        vals = _setting_ws().get_all_values()
        if len(vals) >= 2 and vals[1] and vals[1][0] in ROUNDS:
            value = vals[1][0]
    except Exception as e:
        print(f"설문설정 읽기 오류: {e}", flush=True)
    _round_cache['value'] = value
    return value


def set_round(value):
    ws = _setting_ws()
    ws.update(range_name='A2', values=[[value]])
    _round_cache['value'] = value


def _rows():
    try:
        return _survey_ws().get_all_values()[1:]
    except Exception as e:
        print(f"설문 시트 읽기 오류: {e}", flush=True)
        return None


# ── 학생 ────────────────────────────────────────────────────────
def survey_start(request):
    rnd = current_round()
    def qlist(post=None):
        return [{'no': i, 'area': a, 'text': t,
                 'sel': (post.get(f'q{i}', '') if post else '')}
                for i, (a, t, _r) in enumerate(QUESTIONS, 1)]
    ctx = {'round': rnd, 'questions': qlist(), 'scale': [(str(v), lab) for v, lab in SCALE],
           'open_questions': list(enumerate(OPEN_QUESTIONS, 1)), 'closed': rnd not in ROUNDS}
    if rnd not in ROUNDS or request.method != 'POST':
        return render(request, 'feedback/survey.html', ctx)

    p = request.POST
    sid, snum, sname = p.get('student_id', '').strip(), p.get('student_num', '').strip(), p.get('student_name', '').strip()
    ctx['form'] = p
    ctx['questions'] = qlist(p)
    ctx['texts'] = [p.get(f't{i}', '') for i in range(1, len(OPEN_QUESTIONS) + 1)]
    error = V._escape_validate(sid, snum, sname)
    class_name = V._class_from_student_id(sid) if not error else ''
    if not error and class_name not in V._ESCAPE_CLASSES:
        error = '이 설문은 2학기 정보 수업(1~5반) 학생만 참여할 수 있어요.'

    answers = []
    if not error:
        for i in range(1, len(QUESTIONS) + 1):
            v = p.get(f'q{i}', '')
            if v not in {'1', '2', '3', '4', '5'}:
                error = f'{i}번 문항에 답하지 않았어요. 모든 문항에 답해 주세요.'
                break
            answers.append(int(v))
    texts = [p.get(f't{i}', '').strip()[:500] for i in range(1, len(OPEN_QUESTIONS) + 1)]

    if not error:
        code = response_code(sid)
        with _lock:
            rows = _rows()
            if rows is None:
                error = '잠시 후 다시 시도해 주세요. (저장소 연결 오류)'
            elif any(len(r) > 2 and r[1] == rnd and r[2] == code for r in rows):
                return render(request, 'feedback/survey.html', {**ctx, 'already': True})
            else:
                row = [V._kst_now().strftime('%Y-%m-%d %H:%M:%S'), rnd, code, class_name] + answers + texts
                try:
                    _survey_ws().append_row(row)
                except Exception as e:
                    print(f"설문 저장 오류: {e}", flush=True)
                    error = '저장 중 오류가 났어요. 다시 제출해 주세요.'
    if error:
        ctx['error'] = error
        return render(request, 'feedback/survey.html', ctx)
    return render(request, 'feedback/survey.html', {**ctx, 'done': True, 'name': sname})


# ── 교사 ────────────────────────────────────────────────────────
def survey_teacher(request):
    if not request.session.get('teacher_auth'):
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action in ROUNDS + [CLOSED]:
            try:
                set_round(action)
            except Exception as e:
                print(f"설문설정 저장 오류: {e}", flush=True)
        return redirect('survey_teacher')

    rows = _rows() or []
    nq = len(QUESTIONS)
    # 같은 차수·학번이 여러 번 있으면 첫 제출만 사용
    seen, data = set(), []
    for r in rows:
        if len(r) < N_META + nq or (r[1], r[2]) in seen:
            continue
        seen.add((r[1], r[2]))
        try:
            data.append({'round': r[1], 'class': r[3], 'id': r[2],
                         'ans': [int(x) for x in r[N_META:N_META + nq]]})
        except ValueError:
            continue

    counts = {c: {rd: 0 for rd in ROUNDS} for c in V._ESCAPE_CLASSES}
    for d in data:
        if d['class'] in counts and d['round'] in ROUNDS:
            counts[d['class']][d['round']] += 1
    count_rows = [{'class': c, 'pre': counts[c]['사전'], 'post': counts[c]['사후']} for c in V._ESCAPE_CLASSES]
    total = {'pre': sum(r['pre'] for r in count_rows), 'post': sum(r['post'] for r in count_rows)}
    both = len({d['id'] for d in data if d['round'] == '사전'} & {d['id'] for d in data if d['round'] == '사후'})

    sums = {rd: [0] * nq for rd in ROUNDS}
    ns = {rd: 0 for rd in ROUNDS}
    for d in data:
        if d['round'] in ROUNDS:
            ns[d['round']] += 1
            for i, v in enumerate(d['ans']):
                sums[d['round']][i] += v
    item_rows = []
    for i, (area, text, rev) in enumerate(QUESTIONS):
        pre = round(sums['사전'][i] / ns['사전'], 2) if ns['사전'] else None
        post = round(sums['사후'][i] / ns['사후'], 2) if ns['사후'] else None
        diff = round(post - pre, 2) if pre is not None and post is not None else None
        item_rows.append({'no': i + 1, 'area': area, 'text': text, 'rev': rev,
                          'pre': pre, 'post': post, 'diff': diff})

    return render(request, 'feedback/survey_teacher.html', {
        'round': current_round(), 'rounds': ROUNDS, 'count_rows': count_rows, 'total': total,
        'both': both, 'item_rows': item_rows,
    })
