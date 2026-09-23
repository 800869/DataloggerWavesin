"""Static Java class-file inspector. Does not load or execute archived Java code."""
import pathlib,struct,zipfile,json
import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'src'))
from dataloggerwavesin.paths import PROCESSED_DIR, EXTRACTED_DIR, JAVA_DIR
B=PROCESSED_DIR
class R:
 def __init__(self,b): self.b=b;self.p=0
 def take(self,n): v=self.b[self.p:self.p+n];self.p+=n;return v
 def u1(self): return self.take(1)[0]
 def u2(self): return int.from_bytes(self.take(2),'big')
 def u4(self): return int.from_bytes(self.take(4),'big')

names='nop aconst_null iconst_m1 iconst_0 iconst_1 iconst_2 iconst_3 iconst_4 iconst_5 lconst_0 lconst_1 fconst_0 fconst_1 fconst_2 dconst_0 dconst_1 bipush sipush ldc ldc_w ldc2_w iload lload fload dload aload iload_0 iload_1 iload_2 iload_3 lload_0 lload_1 lload_2 lload_3 fload_0 fload_1 fload_2 fload_3 dload_0 dload_1 dload_2 dload_3 aload_0 aload_1 aload_2 aload_3 iaload laload faload daload aaload baload caload saload istore lstore fstore dstore astore istore_0 istore_1 istore_2 istore_3 lstore_0 lstore_1 lstore_2 lstore_3 fstore_0 fstore_1 fstore_2 fstore_3 dstore_0 dstore_1 dstore_2 dstore_3 astore_0 astore_1 astore_2 astore_3 iastore lastore fastore dastore aastore bastore castore sastore pop pop2 dup dup_x1 dup_x2 dup2 dup2_x1 dup2_x2 swap iadd ladd fadd dadd isub lsub fsub dsub imul lmul fmul dmul idiv ldiv fdiv ddiv irem lrem frem drem ineg lneg fneg dneg ishl lshl ishr lshr iushr lushr iand land ior lor ixor lxor iinc i2l i2f i2d l2i l2f l2d f2i f2l f2d d2i d2l d2f i2b i2c i2s lcmp fcmpl fcmpg dcmpl dcmpg ifeq ifne iflt ifge ifgt ifle if_icmpeq if_icmpne if_icmplt if_icmpge if_icmpgt if_icmple if_acmpeq if_acmpne goto jsr ret tableswitch lookupswitch ireturn lreturn freturn dreturn areturn return getstatic putstatic getfield putfield invokevirtual invokespecial invokestatic invokeinterface invokedynamic new newarray anewarray arraylength athrow checkcast instanceof monitorenter monitorexit wide multianewarray ifnull ifnonnull goto_w jsr_w breakpoint'.split()

def parse(data):
 r=R(data);assert r.u4()==0xcafebabe
 minor=r.u2();major=r.u2(); count=r.u2();cp=[None]*count;i=1
 while i<count:
  tag=r.u1()
  if tag==1: v=r.take(r.u2()).decode('utf-8','replace')
  elif tag in (3,4): v=struct.unpack('>i' if tag==3 else '>f',r.take(4))[0]
  elif tag in (5,6): v=struct.unpack('>q' if tag==5 else '>d',r.take(8))[0]
  elif tag in (7,8,16,19,20): v=r.u2()
  elif tag in (9,10,11,12,17,18): v=(r.u2(),r.u2())
  elif tag==15:v=(r.u1(),r.u2())
  else:raise ValueError(tag)
  cp[i]=(tag,v);i+=2 if tag in (5,6) else 1
 def val(i):
  if not i:return ''
  tag,v=cp[i]
  if tag==1:return v
  if tag in (3,4,5,6):return str(v)
  if tag in (7,8,16,19,20):return val(v)
  if tag in (9,10,11,12):return val(v[0])+'.'+val(v[1])
  return str(v)
 def attrs(rr):
  out=[]
  for _ in range(rr.u2()):out.append((val(rr.u2()),rr.take(rr.u4())))
  return out
 access=r.u2();cn=val(r.u2());sup=val(r.u2());interfaces=[val(r.u2()) for _ in range(r.u2())]
 fields=[];methods=[]
 for target in (fields,methods):
  for _ in range(r.u2()):
   ac=r.u2();n=val(r.u2());desc=val(r.u2());a=attrs(r);target.append((ac,n,desc,a))
 ca=attrs(r)
 lines=[f'CLASS {cn} extends {sup} VERSION {major}.{minor}',f'INTERFACES {interfaces}','FIELDS']
 for ac,n,d,a in fields:lines.append(f'{ac:04x} {n} {d} '+str([(k,val(int.from_bytes(v,"big"))) for k,v in a if k=='ConstantValue']))
 for ac,n,d,aa in methods:
  lines.append(f'\nMETHOD {ac:04x} {n}{d}')
  for k,v in aa:
   if k!='Code':continue
   cr=R(v);stack=cr.u2();locals_=cr.u2();code=cr.take(cr.u4());br=R(code)
   while br.p<len(code):
    off=br.p;op=br.u1();arg='';name=names[op] if op<len(names) else str(op)
    if op in (18,19,20,178,179,180,181,182,183,184,187,189,192,193):
     ix=br.u1() if op==18 else br.u2();arg=f'#{ix} '+val(ix)
    elif op in (185,186): ix=br.u2();arg=f'#{ix} '+val(ix)+' '+str(list(br.take(2)))
    elif op in (16,17):arg=str(int.from_bytes(br.take(1 if op==16 else 2),'big',signed=True))
    elif op in (21,22,23,24,25,54,55,56,57,58,169,188):arg=str(br.u1())
    elif op==132:arg=str(br.u1())+' '+str(int.from_bytes(br.take(1),'big',signed=True))
    elif 153<=op<=168 or op in (198,199,200,201):arg='->'+str(off+int.from_bytes(br.take(4 if op in (200,201) else 2),'big',signed=True))
    elif op in (170,171):
     while br.p%4:br.u1()
     default=off+int.from_bytes(br.take(4),'big',signed=True)
     if op==170:
      low=int.from_bytes(br.take(4),'big',signed=True);high=int.from_bytes(br.take(4),'big',signed=True)
      pairs=[(x,off+int.from_bytes(br.take(4),'big',signed=True)) for x in range(low,high+1)]
     else:
      pairs=[(int.from_bytes(br.take(4),'big',signed=True),off+int.from_bytes(br.take(4),'big',signed=True)) for _ in range(br.u4())]
     arg=f'default->{default} '+str(pairs)
    elif op==196:
     sub=br.u1();arg=names[sub]+' '+str(br.u2())
     if sub==132:arg+=' '+str(int.from_bytes(br.take(2),'big',signed=True))
    elif op==197:arg=val(br.u2())+' '+str(br.u1())
    lines.append(f'{off:5} {name:20} {arg}')
   exceptions=[(cr.u2(),cr.u2(),cr.u2(),val(cr.u2())) for _ in range(cr.u2())]
   lines.append('EXCEPTIONS '+str(exceptions))
   for ak,av in attrs(cr):
    if ak=='LocalVariableTable':
     ar=R(av);vs=[]
     for _ in range(ar.u2()):vs.append((ar.u2(),ar.u2(),val(ar.u2()),val(ar.u2()),ar.u2()))
     lines.append('LOCALS '+str(vs))
 strings=[v for x in cp if x for tag,v in [x] if tag==1]
 return cn,'\n'.join(lines),strings

out=JAVA_DIR;out.mkdir(parents=True,exist_ok=True)
jar=EXTRACTED_DIR/'home/actemium/apps/xthreeconpi/xthreeconpi.jar'
with zipfile.ZipFile(jar) as z:
 for name in z.namelist():
  if name.endswith('.class'):
   cn,dis,strings=parse(z.read(name));stem=cn.replace('/','_')
   (out/(stem+'.txt')).write_text(dis,encoding='utf-8')
   (out/(stem+'.strings.json')).write_text(json.dumps(strings,indent=2),encoding='utf-8')
print('Classes inspected:',len(list(out.glob('*.txt'))))
