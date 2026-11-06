"""Private operator-to-administrator problem referrals and immutable outcomes."""
import datetime as dt

STATUSES={'pending':'Kutilmoqda','resolved':'Hal qilindi','unresolved':'Hal qilinmadi'}
HEADERS=['Çipta','Bölim','Yönaltirgan xodim / oyna','Muammo izohi','Yuborilgan vaqt','Holat','Natija izohi','Admin','Yakun vaqti']
WIDTHS=[48,92,74,146,68,78,126,64,66]

def migrate(c):
    c.executescript('''
    CREATE TABLE IF NOT EXISTS referrals(
      id INTEGER PRIMARY KEY,ticket INTEGER NOT NULL UNIQUE REFERENCES tickets(id),
      label TEXT NOT NULL,service INTEGER NOT NULL REFERENCES services(id),
      service_name TEXT NOT NULL,operator TEXT NOT NULL,window INTEGER NOT NULL,
      comment TEXT NOT NULL,created TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'pending'
      CHECK(status IN ('pending','resolved','unresolved')),
      resolution TEXT NOT NULL DEFAULT '',resolved_by TEXT,resolved_at TEXT);
    CREATE TABLE IF NOT EXISTS referral_history(
      id INTEGER PRIMARY KEY,referral INTEGER NOT NULL REFERENCES referrals(id),
      status TEXT NOT NULL,comment TEXT NOT NULL,user TEXT NOT NULL,created TEXT NOT NULL);
    CREATE INDEX IF NOT EXISTS referrals_created ON referrals(created);
    ''')

def note(value):
    if not isinstance(value,str) or not 1<=len(value.strip())<=1000 or any(ord(ch)<32 and ch not in '\n\r\t' for ch in value):
        raise ValueError('Izoh majburiy: 1–1000 belgi')
    return value.strip()

def create(c,user,ticket,comment,now):
    comment=note(comment)
    existing=c.execute('SELECT * FROM referrals WHERE ticket=?',(ticket['id'],)).fetchone()
    if existing:
        if existing['operator']==user['name'] and existing['comment']==comment:return dict(existing)
        raise ValueError('Bu chipta administratorga yuborilgan')
    if ticket['user']!=user['name'] or ticket['window']!=user['window'] or ticket['status'] not in ('called','serving'):
        raise ValueError('Faqat joriy o‘zingizga biriktirilgan chiptani yuboring')
    name=c.execute('SELECT name FROM services WHERE id=?',(ticket['service'],)).fetchone()[0]
    row=c.execute('INSERT INTO referrals(ticket,label,service,service_name,operator,window,comment,created) VALUES (?,?,?,?,?,?,?,?)',
                  (ticket['id'],ticket['label'],ticket['service'],name,user['name'],user['window'],comment,now))
    c.execute("INSERT INTO referral_history(referral,status,comment,user,created) VALUES (?,'pending',?,?,?)",(row.lastrowid,comment,user['name'],now))
    # Free the operator window without printing a new ticket or rejoining the queue.
    c.execute("UPDATE tickets SET status='referred',window=NULL,started=NULL WHERE id=?",(ticket['id'],))
    return dict(c.execute('SELECT * FROM referrals WHERE id=?',(row.lastrowid,)).fetchone())

def resolve(c,user,identifier,status,comment,now):
    if user['role']!='admin':raise ValueError('Faqat administrator natijani saqlaydi')
    if type(identifier) is not int or identifier<=0:raise ValueError('Murojaat IDsi noto‘g‘ri')
    if status not in ('resolved','unresolved'):raise ValueError('Natija: hal qilindi yoki hal qilinmadi')
    comment=note(comment)
    row=c.execute('SELECT * FROM referrals WHERE id=?',(identifier,)).fetchone()
    if not row:raise ValueError('Murojaat topilmadi')
    if row['status']!='pending':
        if row['status']==status and row['resolution']==comment and row['resolved_by']==user['name']:return dict(row)
        raise ValueError('Murojaat natijasi allaqachon saqlangan')
    ticket=c.execute('SELECT status FROM tickets WHERE id=?',(row['ticket'],)).fetchone()
    if not ticket or ticket['status']!='referred':raise ValueError('Chipta holati murojaatga mos emas')
    c.execute('UPDATE referrals SET status=?,resolution=?,resolved_by=?,resolved_at=? WHERE id=?',(status,comment,user['name'],now,identifier))
    c.execute('INSERT INTO referral_history(referral,status,comment,user,created) VALUES (?,?,?,?,?)',(identifier,status,comment,user['name'],now))
    # Only an actually resolved case is a completed service, credited to its resolver.
    c.execute('UPDATE tickets SET status=?,user=?,finished=? WHERE id=?',('done' if status=='resolved' else 'unresolved',user['name'],now,row['ticket']))
    c.execute('INSERT INTO events(ticket,operation,user,service,window,created) VALUES (?,?,?,?,NULL,?)',(row['ticket'],'admin_'+status,user['name'],row['service'],now))
    return dict(c.execute('SELECT * FROM referrals WHERE id=?',(identifier,)).fetchone())

def listing(c,operator=None,status=None):
    clauses=[];parameters=[]
    if operator is not None:clauses.append('operator=?');parameters.append(operator)
    if status:
        if status not in STATUSES:raise ValueError('Murojaat holati noto‘g‘ri')
        clauses.append('status=?');parameters.append(status)
    return [dict(r) for r in c.execute('SELECT * FROM referrals'+(' WHERE '+' AND '.join(clauses) if clauses else '')+" ORDER BY CASE status WHEN 'pending' THEN 0 ELSE 1 END,id DESC",parameters)]

def report(c,start,end):
    # Separate cohort: the date the operator submitted the problem, not ticket issue date.
    rows=[dict(r) for r in c.execute('SELECT * FROM referrals WHERE substr(created,1,10) BETWEEN ? AND ? ORDER BY id',(start,end))]
    return {'rows':rows,'total':len(rows),**{status:sum(r['status']==status for r in rows) for status in STATUSES}}

def display_time(value):
    return dt.datetime.fromisoformat(value).astimezone(dt.timezone(dt.timedelta(hours=5))).strftime('%d.%m.%Y %H:%M') if value else '—'

def export_rows(rows):
    return [[r['label'],r['service_name'],r['operator']+' / '+str(r['window'])+'-oyna',r['comment'],display_time(r['created']),STATUSES[r['status']],r['resolution'] or '—',r['resolved_by'] or '—',display_time(r['resolved_at'])] for r in rows]
