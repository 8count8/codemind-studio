import sys
sys.path.insert(0, '.')
from app.models.db import get_create_statements

with open('database/init_db.sql', 'r', encoding='utf-8') as f:
    sql = f.read()

stmts = get_create_statements()
print('Code table count:', len(stmts))
all_ok = True
for s in stmts:
    tname = s.split('CREATE TABLE IF NOT EXISTS')[1].strip().split('(')[0].strip()
    key = 'CREATE TABLE IF NOT EXISTS ' + tname
    in_sql = key in sql
    status = 'OK' if in_sql else 'MISSING'
    if not in_sql:
        all_ok = False
    print('  %-25s code=OK sql=%s' % (tname, status))

key2 = 'CREATE TABLE IF NOT EXISTS ability_submissions'
in_sql2 = key2 in sql
if not in_sql2:
    all_ok = False
print('  %-25s code=OK(model) sql=%s' % ('ability_submissions', 'OK' if in_sql2 else 'MISSING'))

print()
print('Seed data:')
print('  problems INSERT count:', sql.count('INSERT INTO problems'))
print('  test_cases INSERT count:', sql.count('INSERT INTO test_cases'))
print('  admin user present:', 'admin' in sql)

print()
if all_ok:
    print('ALL CHECKS PASSED')
else:
    print('SOME CHECKS FAILED')
