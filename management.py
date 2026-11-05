"""Validated administrator settings, assignments and report definitions."""
import datetime as dt
import json
import re
import alphabet

DEFAULTS = {
 'university':alphabet.text('Alisher Navoiy nomidagi Toshkent davlat o‘zbek tili va adabiyoti universiteti'),
 'prefix':'A','daily_reset':True,'open':'00:00','close':'23:59','weekdays':[0,1,2,3,4,5,6],
 'printer_mode':'html','printer_name':'','paper_width_mm':80,'idle_seconds':60,'tv_rows':8,
}
SEED_NAMES=['Talabalarga xizmat ko‘rsatish sektori','Ilmiy va innovatsion faoliyat bo‘yicha xizmat ko‘rsatish sektori','Xalqaro aloqalar va akademik mobillik bo‘yicha xizmat ko‘rsatish sektori','Marketing va amaliyotlarni tashkil etish','Buxgalteriya bo‘yicha xizmat ko‘rsatish sektori']
EN=['Student Services Sector','Research and Innovation Services Sector','International Relations and Academic Mobility Services Sector','Marketing and Internship Coordination','Accounting Services Sector']
RU=['Сектор обслуживания студентов','Сектор научной и инновационной деятельности','Сектор международных связей и академической мобильности','Маркетинг и организация практики','Сектор бухгалтерского обслуживания']

def migrate(c):
 c.executescript('''CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
 CREATE TABLE IF NOT EXISTS windows(id INTEGER PRIMARY KEY,name TEXT NOT NULL,enabled INTEGER NOT NULL DEFAULT 1);
 CREATE TABLE IF NOT EXISTS permissions(user TEXT NOT NULL REFERENCES users(name),service INTEGER NOT NULL REFERENCES services(id),PRIMARY KEY(user,service));
 CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY,ticket INTEGER NOT NULL REFERENCES tickets(id),operation TEXT NOT NULL,user TEXT,service INTEGER NOT NULL,window INTEGER,created TEXT NOT NULL);
 CREATE TABLE IF NOT EXISTS print_jobs(id INTEGER PRIMARY KEY,ticket INTEGER NOT NULL REFERENCES tickets(id),status TEXT NOT NULL,created TEXT NOT NULL,error TEXT);
 ''')
 for table, additions in {
  'services':{'name_en':"TEXT NOT NULL DEFAULT ''",'name_ru':"TEXT NOT NULL DEFAULT ''",'enabled':'INTEGER NOT NULL DEFAULT 1'},
  'calls':{'service':'INTEGER REFERENCES services(id)'},
  'users':{'enabled':'INTEGER NOT NULL DEFAULT 1'},
  'tickets':{'lang':"TEXT NOT NULL DEFAULT 'uz'",'label':"TEXT NOT NULL DEFAULT ''",'ahead':'INTEGER NOT NULL DEFAULT 0'},
 }.items():
  existing={r[1] for r in c.execute('PRAGMA table_info('+table+')')}
  for column,definition in additions.items():
   if column not in existing:c.execute(f'ALTER TABLE {table} ADD COLUMN {column} {definition}')
 for key,value in DEFAULTS.items():c.execute('INSERT OR IGNORE INTO settings VALUES (?,?)',(key,json.dumps(value,ensure_ascii=False)))
 for n in range(1,6):c.execute('INSERT OR IGNORE INTO windows(id,name) VALUES (?,?)',(n,str(n)+'-oyna'))
 for n,ru in enumerate(RU,1):
  c.execute("UPDATE services SET name_ru=? WHERE id=? AND name_ru=''",(ru,n))
 for n,en in enumerate(EN,1):
  row=c.execute('SELECT name FROM services WHERE id=?',(n,)).fetchone()
  if row and alphabet.text(row['name'])==alphabet.text(SEED_NAMES[n-1]):c.execute("UPDATE services SET name_en=? WHERE id=? AND name_en=''",(en,n))
 c.execute('UPDATE calls SET service=(SELECT service FROM tickets WHERE tickets.id=calls.ticket) WHERE service IS NULL')
 c.execute("UPDATE tickets SET label='A'||printf('%03d',number) WHERE label=''")
 if c.execute('PRAGMA user_version').fetchone()[0]<2:
  c.execute('INSERT OR IGNORE INTO permissions SELECT users.name,services.id FROM users CROSS JOIN services')
 for row in c.execute('SELECT id,name FROM services').fetchall():
  translated=alphabet.text(row['name'])
  if translated!=row['name']:c.execute('UPDATE services SET name=? WHERE id=?',(translated,row['id']))
 university=c.execute("SELECT value FROM settings WHERE key='university'").fetchone()
 if university:c.execute("UPDATE settings SET value=? WHERE key='university'",(json.dumps(alphabet.text(json.loads(university[0])),ensure_ascii=False),))
 c.execute('PRAGMA user_version=3')

def settings(c):return {r['key']:json.loads(r['value']) for r in c.execute('SELECT * FROM settings')}

def save_settings(c,body):
 if not isinstance(body,dict) or set(body)-set(DEFAULTS):raise ValueError('Unknown setting')
 body=dict(body)
 if 'university' in body:body['university']=alphabet.text(body['university'])
 merged=settings(c)|body
 if not isinstance(merged['university'],str) or not 3<=len(merged['university'])<=300:raise ValueError('Universitet nomi 3–300 belgi')
 if not isinstance(merged['prefix'],str) or not re.fullmatch('[A-Z]{1,3}',merged['prefix']):raise ValueError('Prefiks: 1–3 katta lotin harfi')
 if type(merged['daily_reset']) is not bool:raise ValueError('Invalid numbering rule')
 for key in ('open','close'):
  if not isinstance(merged[key],str) or not re.fullmatch(r'(?:[01][0-9]|2[0-3]):[0-5][0-9]',merged[key]):raise ValueError('Vaqt HH:MM shaklida')
 if merged['open']>merged['close']:raise ValueError('Yopilish ochilishdan keyin bo‘lsin')
 days=merged['weekdays']
 if not isinstance(days,list) or not days or any(type(v) is not int or not 0<=v<=6 for v in days):raise ValueError('Ish kunlarini tanlang')
 if merged['printer_mode'] not in ('html','windows'):raise ValueError('Invalid printer mode')
 if not isinstance(merged['printer_name'],str) or len(merged['printer_name'])>200:raise ValueError('Invalid printer name')
 if merged['printer_mode']=='windows' and not merged['printer_name'].strip():raise ValueError('Windows printer nomini kiriting')
 for key,low,high in [('paper_width_mm',58,100),('idle_seconds',15,600),('tv_rows',1,20)]:
  if type(merged[key]) is not int or not low<=merged[key]<=high:raise ValueError(f'{key}: {low}–{high}')
 for key,value in body.items():c.execute('UPDATE settings SET value=? WHERE key=?',(json.dumps(value,ensure_ascii=False),key))
 return merged

def allowed(c,user):
 # Every authenticated operator serves every department; roles still protect administration.
 return [r[0] for r in c.execute('SELECT id FROM services')] if user.get('role') in ('admin','staff') else []


def report(c,start,end):
 dt.date.fromisoformat(start);dt.date.fromisoformat(end)
 if start>end:raise ValueError('Invalid date range')
 rows=c.execute('SELECT * FROM tickets WHERE day BETWEEN ? AND ? ORDER BY id',(start,end)).fetchall()
 result={'issued':len(rows),'done':0,'absent':0,'waiting':0,'services':{},'employees':{}}
 waits=[];durations=[]
 for row in rows:
  wait=(dt.datetime.fromisoformat(row['called'])-dt.datetime.fromisoformat(row['created'])).total_seconds() if row['called'] else None
  duration=(dt.datetime.fromisoformat(row['finished'])-dt.datetime.fromisoformat(row['started'])).total_seconds() if row['finished'] and row['started'] and row['status']=='done' else None
  for group,key in [(result['services'],str(row['service'])),(result['employees'],row['user'] or 'unassigned')]:
   bucket=group.setdefault(key,{'issued':0,'done':0,'absent':0,'waits':[],'durations':[]})
   bucket['issued']+=1;bucket['done']+=row['status']=='done';bucket['absent']+=row['status']=='absent'
   if wait is not None:bucket['waits'].append(wait)
   if duration is not None:bucket['durations'].append(duration)
  if wait is not None:waits.append(wait)
  if duration is not None:durations.append(duration)
  for key,state in [('done','done'),('absent','absent'),('waiting','waiting')]:result[key]+=row['status']==state
 def average(items):return round(sum(items)/len(items),1) if items else None
 result['average_wait_seconds']=average(waits);result['average_service_seconds']=average(durations)
 for group in (result['services'],result['employees']):
  for bucket in group.values():
   bucket['average_wait_seconds']=average(bucket.pop('waits'));bucket['average_service_seconds']=average(bucket.pop('durations'))
 return result
