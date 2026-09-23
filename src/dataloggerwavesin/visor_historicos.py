"""Visor local de la copia. SQLite en solo lectura; sin conexiones al equipo ni a Internet."""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlparse,parse_qs
import pathlib,json,sqlite3,datetime,math

from dataloggerwavesin.paths import UNITS_FILE, SUMMARY_FILE, DATABASE_FILE, HTML_FILE
UNITS=[]
for line in UNITS_FILE.read_text().splitlines():
 if not line.strip():continue
 p=line.split(';');UNITS.append(dict(id=p[0],nombre=p[1],tipo=int(p[3]),repetidores=[r for r in p[4:7] if r],modbus=p[7]=='true',mapa=p[8]))
SUMMARY=json.loads(SUMMARY_FILE.read_text())
for u in UNITS:u.update(next(x for x in SUMMARY['units'] if x['id']==u['id']))
UIDS={u['id'] for u in UNITS}
def db():return sqlite3.connect(DATABASE_FILE.as_uri()+'?mode=ro',uri=True)

class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def send(self,code,data,ctype='application/json; charset=utf-8'):
  raw=data if isinstance(data,bytes) else json.dumps(data,ensure_ascii=False,allow_nan=False).encode()
  self.send_response(code);self.send_header('Content-Type',ctype);self.send_header('Content-Length',str(len(raw)))
  self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(raw)
 def do_GET(self):
  p=urlparse(self.path);q=parse_qs(p.query)
  try:
   if p.path=='/':return self.send(200,HTML_FILE.read_bytes(),'text/html; charset=utf-8')
   if p.path=='/api/unidades':return self.send(200,{'unidades':UNITS,'total':SUMMARY['deduplicated_records'],'conflictos':SUMMARY['conflicting_timestamps']})
   if p.path!='/api/serie':return self.send(404,{'error':'Ruta no disponible'})
   uid=q.get('unidad',[''])[0];channel=int(q.get('canal',['14'])[0])
   if uid not in UIDS or not 0<=channel<32:raise ValueError('Unidad o canal no valido')
   params=[uid];sql='SELECT epoch,valores,origen FROM lecturas WHERE unidad=?'
   for key,op in [('desde','>='),('hasta','<')]:
    if q.get(key,[''])[0]:
     dt=datetime.datetime.strptime(q[key][0],'%Y-%m-%d').replace(tzinfo=datetime.timezone.utc)
     if key=='hasta':dt+=datetime.timedelta(days=1)
     sql+=' AND epoch '+op+' ?';params.append(int(dt.timestamp()))
   sql+=' ORDER BY epoch,valores'
   with db() as c:rows=c.execute(sql,params).fetchall()
   pts=[];recent=[];variants={}
   for t,raw,src in rows:
    vals=json.loads(raw);v=float(vals[channel]);v=v if math.isfinite(v) else None
    pts.append([t,v]);variants[t]=variants.get(t,0)+1
   # Preserve peaks in each time-ordered bin; raw latest rows remain unmodified.
   shown=pts
   if len(pts)>3000:
    step=math.ceil(len(pts)/1200);shown=[]
    for i in range(0,len(pts),step):
     bin_=pts[i:i+step];valid=[(j,x) for j,x in enumerate(bin_) if x[1] is not None]
     indices={0,len(bin_)-1}
     if valid:indices.update([min(valid,key=lambda a:a[1][1])[0],max(valid,key=lambda a:a[1][1])[0]])
     shown.extend(bin_[j] for j in sorted(indices))
   for t,raw,src in rows[-100:]:recent.append({'epoch':t,'valores':json.loads(raw),'origen':src,'variantes':variants[t]})
   values=[p[1] for p in pts if p[1] is not None]
   return self.send(200,dict(unidad=uid,canal=channel,total=len(rows),fechas=len(variants),conflictos=sum(n>1 for n in variants.values()),min=min(values) if values else None,max=max(values) if values else None,puntos=shown,ultimos=recent))
  except (ValueError,KeyError,IndexError) as e:return self.send(400,{'error':str(e)})

if __name__=='__main__':
 print('Visor de copia en solo lectura: http://127.0.0.1:8765/',flush=True)
 ThreadingHTTPServer(('127.0.0.1',8765),Handler).serve_forever()
