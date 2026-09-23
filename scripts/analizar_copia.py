import tarfile, pathlib, json, collections, hashlib

import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'src'))
from dataloggerwavesin.paths import RAW_DIR, PROCESSED_DIR, EXTRACTED_DIR, ARCHIVE_FILE
BASE=RAW_DIR
OUT=PROCESSED_DIR
OUT.mkdir(parents=True,exist_ok=True)
dest=EXTRACTED_DIR
counts=collections.Counter(); sizes=collections.Counter(); links=[]; picked=[]; apps=[]
with tarfile.open(ARCHIVE_FILE,'r:') as tf, (OUT/'inventario.jsonl').open('w',encoding='utf-8') as inv:
    for m in tf:
        p=pathlib.PurePosixPath(m.name)
        if p.is_absolute() or '..' in p.parts: raise ValueError(m.name)
        record=dict(path=m.name,size=m.size,type=m.type.decode('ascii','replace'),link=m.linkname,mtime=m.mtime,mode=oct(m.mode),uid=m.uid,gid=m.gid)
        inv.write(json.dumps(record)+'\n')
        group='/'.join(p.parts[:3]); counts[group]+=1; sizes[group]+=m.size
        if m.issym() or m.islnk(): links.append(record)
        app=m.name.startswith('home/actemium/apps/')
        if app: apps.append(record)
        select=(app and '/backup/' not in m.name and '/ftpOut/' not in m.name and '/logs/' not in m.name and '/log/' not in m.name)
        select |= m.name.startswith(('etc/','root/','home/actemium/bin/','usr/local/etc/'))
        select |= m.name in ('home/actemium/.bash_history','usr/local/lib/node_modules/node-red/settings.js','var/lib/dpkg/status')
        if select and m.isfile():
            # Explicit regular-file copy only: never follow archive symlinks or execute content.
            parts=[x.replace(':','_COLON_') for x in p.parts]
            target=dest.joinpath(*parts)
            target.parent.mkdir(parents=True,exist_ok=True)
            data=tf.extractfile(m).read(); target.write_bytes(data)
            picked.append(m.name)
(OUT/'enlaces.json').write_text(json.dumps(links,indent=2),encoding='utf-8')
(OUT/'inventario_apps.json').write_text(json.dumps(apps,indent=2),encoding='utf-8')
(OUT/'resumen_inventario.json').write_text(json.dumps({'entries':sum(counts.values()),'regular_payload_bytes':sum(sizes.values()),'groups':{k:{'entries':counts[k],'bytes':v} for k,v in sizes.most_common()},'extracted':picked},indent=2),encoding='utf-8')
print('Entries:',sum(counts.values()),'Extracted:',len(picked))
for k,v in sizes.most_common(20): print(k,counts[k],v)
print('APP NON-BACKUP FILES')
for r in apps:
    if '/backup/' not in r['path'] and '/ftpOut/' not in r['path']: print(r['path'],r['size'],r['link'])
