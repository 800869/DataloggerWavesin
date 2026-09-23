import pathlib,tarfile,json,sqlite3,collections,datetime,re
import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'src'))
from dataloggerwavesin.paths import RAW_DIR, PROCESSED_DIR, LOG_DIR, DATABASE_FILE, ARCHIVE_FILE
B=RAW_DIR;O=PROCESSED_DIR;O.mkdir(parents=True,exist_ok=True);logs=LOG_DIR;logs.mkdir(parents=True,exist_ok=True)
DATABASE_FILE.parent.mkdir(parents=True,exist_ok=True)
db=sqlite3.connect(DATABASE_FILE);db.executescript('''
CREATE TABLE IF NOT EXISTS lecturas (unidad TEXT, epoch INTEGER, valores TEXT, origen TEXT, PRIMARY KEY(unidad,epoch,valores));
CREATE TABLE IF NOT EXISTS archivos (ruta TEXT PRIMARY KEY, tipo TEXT, unidad TEXT, registros INTEGER, primero INTEGER, ultimo INTEGER, bytes INTEGER);
''')
stats=collections.defaultdict(lambda:dict(files=0,records=0,bytes=0,errors=0));errors=[];logsum={};batch=[]
def iso(t):return datetime.datetime.fromtimestamp(t,datetime.timezone.utc).isoformat() if t else None
with tarfile.open(ARCHIVE_FILE) as tf:
 for m in tf:
  if not m.isfile() or not m.name.startswith('home/actemium/apps/xthreeconpi/'):continue
  kind=m.name.split('/')[4]
  if kind=='log':
   raw=tf.extractfile(m).read();(logs/pathlib.PurePosixPath(m.name).name).write_bytes(raw)
   lines=raw.decode('utf-8','replace').splitlines();lines=[x for x in lines if x.strip()]
   counts=collections.Counter();examples={}
   for line in lines:
    msg=re.sub(r'^.*? (INFO|ERROR|WARNING|SEVERE):\s*',r'\1: ',line)
    msg=re.sub(r'\[[0-9A-F]{12,14}\]','[UNIT]',msg)
    msg=re.sub(r'\b\d+\b','#',msg)
    counts[msg]+=1;examples.setdefault(msg,line)
   logsum[pathlib.PurePosixPath(m.name).name]={'lines':len(lines),'first':lines[:5],'last':lines[-8:],'common':[{'pattern':p,'count':n,'example':examples[p]} for p,n in counts.most_common(20)]}
  if kind not in ('backup','ftpOut'):continue
  s=stats[kind];s['files']+=1;s['bytes']+=m.size
  try:
   data=json.loads(tf.extractfile(m).read());uid=data['id'];rows=data['energyLogs'];times=[]
   for row in rows:
    ts=int(row['dateTime']);vals=row['values'];times.append(ts)
    batch.append((uid,ts,json.dumps(vals,separators=(',',':')),m.name))
   s['records']+=len(rows)
   db.execute('INSERT OR REPLACE INTO archivos VALUES (?,?,?,?,?,?,?)',(m.name,kind,uid,len(rows),min(times) if times else None,max(times) if times else None,m.size))
   if len(batch)>=10000:
    db.executemany('INSERT OR IGNORE INTO lecturas VALUES (?,?,?,?)',batch);batch=[];db.commit()
  except Exception as ex:s['errors']+=1;errors.append({'path':m.name,'error':str(ex)})
db.executemany('INSERT OR IGNORE INTO lecturas VALUES (?,?,?,?)',batch);db.commit()
units=[]
for uid,n,start,end in db.execute('SELECT unidad,count(*),min(epoch),max(epoch) FROM lecturas GROUP BY unidad'):
 times=[x[0] for x in db.execute('SELECT DISTINCT epoch FROM lecturas WHERE unidad=? ORDER BY epoch',(uid,))]
 gaps=collections.Counter(b-a for a,b in zip(times,times[1:]));lens=collections.Counter();mins=[None]*32;maxs=[None]*32;nonzero=[0]*32
 for (raw,) in db.execute('SELECT valores FROM lecturas WHERE unidad=?',(uid,)):
  vals=json.loads(raw);lens[len(vals)]+=1
  for i,x in enumerate(vals):
   if i>=32:continue
   try:v=float(x)
   except (ValueError,TypeError):continue
   mins[i]=v if mins[i] is None else min(mins[i],v);maxs[i]=v if maxs[i] is None else max(maxs[i],v);nonzero[i]+=v!=0
 units.append({'id':uid,'records':n,'unique_timestamps':len(times),'first_utc':iso(start),'last_utc':iso(end),'intervals':gaps.most_common(8),'value_lengths':dict(lens),'channel_min':mins,'channel_max':maxs,'channel_nonzero':nonzero})
conflicts=db.execute('SELECT count(*) FROM (SELECT unidad,epoch FROM lecturas GROUP BY unidad,epoch HAVING count(*)>1)').fetchone()[0]
summary={'sources':dict(stats),'units':units,'invalid_files':errors,'conflicting_timestamps':conflicts,'deduplicated_records':sum(x['records'] for x in units),'timezone_note':'UTC obtained from epoch; original filenames/logs may use local time'}
(O/'resumen_historicos.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
(O/'resumen_logs.json').write_text(json.dumps(logsum,indent=2),encoding='utf-8')
db.close()
print(json.dumps({'sources':dict(stats),'conflicting_timestamps':conflicts,'deduplicated_records':summary['deduplicated_records'],'units':[{k:v for k,v in u.items() if k in ('id','records','first_utc','last_utc')} for u in units]},indent=2))
