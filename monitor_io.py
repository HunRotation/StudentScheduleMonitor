import pymysql
from functools import partial
import b_tree
from collections import defaultdict

conn = pymysql.connect(host='dev.gsa.hs.kr', port=18001, user='s18004', passwd='1111', db='s18004', charset='utf8')
cur = conn.cursor(pymysql.cursors.DictCursor)

schedule = defaultdict(dict)
schedule_tree = defaultdict(lambda: b_tree.BTree(3))

#학년, 반, 번호 4자리 및 이름으로 그 학생의 자습 내역을 탐색 / student_info_only가 true면 자습 내역을 제외한 학생 정보만 반환
def search(sno4=None, name=None, student_info_only=False):
    if student_info_only:
        sql = "select grade, class, num, name from students where 1=1"
    else:
        sql = "select grade, class, num, name, s, t, w, z, h from students, checklist where checklist.sno = students.sno"
    if sno4 is not None and len(sno4) == 4:
        try:
            print(int(sno4))
        except:
            return []
        grade, classnum, stunum = sno4[0], sno4[1], sno4[2:]
        if int(grade) != 0:
            sql += " and grade=%s" % grade
        if int(classnum) != 0:
            sql += " and class=%s" % classnum
        if int(stunum) != 0:
            sql += " and num=%s" % stunum
    elif sno4 is not None:
        return []
    if name is not None:
        sql += " and name like '%%%s%%'" % name
    cur.execute(sql)
    result = cur.fetchall()
    for row in result:
        print(row)
    return result

#학번으로 그 학생의 모든 자습 메모 내역을 조회
def get_memo(name):
    sql = "select id, type, note, memo_time from memo, students where memo.sno = students.sno and name=%s"
    cur.execute(sql, (name))
    result = cur.fetchall()
    for row in result:
        print(row)
    return result

# 새로운 메모를 추가
def insert_memo(name, checktype, memo):
    if name is None or memo is None:
        return False
    sql = "select sno from students where name=%s"
    cur.execute(sql, (name))
    res = cur.fetchone()
    if not res:
        return False
    sno = res['sno']
    sql = "insert into memo (sno, type, note) values (%s, %s, %s)"
    cur.execute(sql, (sno, checktype, memo))
    conn.commit()
    if checktype in ['s', 't', 'w', 'z', 'h']:
        sql = "update checklist set %s = %s + 1 where sno=%s" % (checktype, checktype, sno)
        cur.execute(sql)
        conn.commit()
    return True

# 메모 리스트에서 메모를 삭제
def delete_memo(id):
    print(id)
    sql = "select sno, type from memo where id=%s"
    cur.execute(sql, (id))
    check = cur.fetchone()
    checktype, sno = check['type'], check['sno']
    sql = "delete from memo where id=%s"
    cur.execute(sql, (id))
    conn.commit()
    if checktype in ['s', 't', 'w', 'z', 'h']:
        sql = "update checklist set %s = %s - 1 where sno=%s and %s > 0" % (checktype, checktype, sno, checktype)
        cur.execute(sql)
        conn.commit()

# 각 사람의 스케줄을 시간 순서대로 해당 사람의 B 트리에 저장
def schedule_init():
    sql = "select * from schedules"
    cur.execute(sql)
    res = cur.fetchall()
    for row in res:
        del row['id']
        start_key = row['start_time']
        end_key = row['end_time']
        schedule[row['sno']][(start_key, end_key)] = row
        schedule_tree[row['sno']].insert((start_key, end_key))
# 원하는 사람의 스케줄 중 기간 안에 속하는 스케줄을 찾아 반환
def view_schedule(name, _from, _to, all=1):
    sql = "select sno from students where name=%s"
    cur.execute(sql, (name))
    rel = cur.fetchone()
    if not rel:
        return None
    sno = rel['sno']
    get = schedule_tree[sno].traverse()
    res = []
    if all:
        for key in get:
            if key[2]:
                res.append(schedule[sno][(key[0], key[1])])
    else:
        for key in get:
            if _from <= key[0] and key[1] <= _to and key[2]:
                res.append(schedule[sno][(key[0], key[1])])
    return res

# B 트리을 이용해 한 사람의 스케줄 리스트에 새로운 스케줄을 추가(DB에도)
# 단 다른 스케줄과 시간이 겹치지 않도록 검사해야 함
def insert_schedule(name, place, reason, start, end):
    if start > end or place is None or reason is None:
        return False
    sql = "select sno from students where name=%s"
    cur.execute(sql, (name))
    res = cur.fetchone()
    if not res:
        return None
    sno = res['sno']
    newrow = {'sno': sno, 'place': place, 'reason': reason, 'start_time':start, 'end-time':end}
    success = schedule_tree[sno].insert((start, end))
    print(success)
    if success:
        sql = "insert into schedules (sno, place, reason, start_time, end_time) values (%s, %s, %s, %s, %s)"
        cur.execute(sql, (sno, place, reason, start, end))
        conn.commit()
        schedule[sno][(start, end)] = newrow
    return success

# 스케줄 트리에서 없애고자 하는 스케줄을 무효화(해당하는 튜플의 index 2 원소를 True에서 False로 바꿈)
'''
def cancel_schedule(sno, point):
    sch = schedule_tree[sno].search(point)
    if sch is None:
        return False
    view_btree()
    (sch[0], sch[1], False)
    del schedule[sno][(sch[0], sch[1])]
    sql = "delete from schedules where start_time=%s and end_time=%s"
    cur.execute(sql, (sch[0], sch[1]))
    conn.commit()
    return True
'''

# B-Tree가 제대로 구성되었는지 확인하기 위한 용도
def view_btree():
    for key in schedule_tree.keys():
        print(key)
        schedule_tree[key].print_order()
