import json

p = '/home/eduleocosta/Sistema_Emprel/database/sqlite_core.py'
with open(p, 'r', encoding='utf-8') as f:
    s = f.read()

old1 = '        dados.get("vans_permitidas", "")'
new1 = '        str(dados.get("vans_permitidas", ""))'
old2 = '        dados.get("van_ativa", "")'
new2 = '        str(dados.get("van_ativa", ""))'

if old1 in s:
    s = s.replace(old1, new1)
if old2 in s:
    s = s.replace(old2, new2)

with open(p, 'w', encoding='utf-8') as f:
    f.write(s)

print('patched')
