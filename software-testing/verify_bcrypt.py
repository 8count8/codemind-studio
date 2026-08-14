import bcrypt
import sys

admin_hash = b'$2b$12$lneFaHZ/E/1Fhwb9nVlI5OUhzocw8Z0YHKvorYqqfZN8JzOevcb/a'
test_hash = b'$2b$12$F9GfopyoCTNkmYc7vjEJ5.92YWums0a7NRdgrah/IPL4cXI5YZRQ6'

admin_ok = bcrypt.checkpw(b'admin123456', admin_hash)
test_ok = bcrypt.checkpw(b'test123456', test_hash)

print('admin match:', admin_ok)
print('testuser match:', test_ok)

if not admin_ok or not test_ok:
    # 重新生成
    print('\nRegenerating...')
    h1 = bcrypt.hashpw(b'admin123456', bcrypt.gensalt()).decode()
    h2 = bcrypt.hashpw(b'test123456', bcrypt.gensalt()).decode()
    # 验证
    v1 = bcrypt.checkpw(b'admin123456', h1.encode())
    v2 = bcrypt.checkpw(b'test123456', h2.encode())
    print('admin new hash:', h1, 'verified:', v1)
    print('testuser new hash:', h2, 'verified:', v2)
    sys.exit(1 if not (v1 and v2) else 0)
else:
    print('\nAll hashes valid')
