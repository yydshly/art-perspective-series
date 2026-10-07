"""The Weight of Seeing / 观看的重量. Deterministic procedural visual essay.
All motion, geometry, typography and sound are original. Museum reproductions
are separately identified, never presented as original film artwork.
"""
import os, sys, math, json, argparse, subprocess, pathlib, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops
P=pathlib.Path(__file__).resolve().parent
W,H=1280,720; FPS=24; DURATION=228
SER='/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc'
SAN='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
ENG='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
@functools.lru_cache(None)
def font(n,serif=False): return ImageFont.truetype(SER if serif else SAN,n)
def smooth(x): x=max(0,min(1,x)); return x*x*(3-2*x)
def fade(t,a,b,d=.7):return smooth((t-a)/d)*smooth((b-t)/d)
def mix(a,b,x): return tuple(int(a[i]*(1-x)+b[i]*x) for i in range(3))
RNG=np.random.default_rng(501)
# A stable grain field is material, not a distracting flicker filter.
noise=RNG.normal(0,1,(H,W,1))
xx=np.linspace(-1,1,W)[None,:]; yy=np.linspace(-1,1,H)[:,None]
vig=np.clip(1-.12*(xx*xx+yy*yy),.6,1)[...,None]
def paper(col,grain=1.8):return Image.fromarray(np.uint8(np.clip(np.array(col)[None,None,:]+noise*grain,0,255)))
PAPER=paper((223,219,207)); DARK=paper((12,16,20),.8)
ART={k:Image.open(P/'assets'/f'{k}.jpg').convert('RGB') for k in ['retreat','melencolia','wave','sideshow']}
for im in ART.values(): im.thumbnail((2400,2400),Image.Resampling.LANCZOS)
# Caption timings: modest reading density, held between 6 and 10 seconds.
CAP=[
(3,11,'每一种观看，都在寻找一种安放。','Every way of seeing searches for a place to belong.'),
(16,25,'山水可以是内心的居所。','A landscape can become an inward dwelling.'),
(27,36,'王蒙让密集的笔触，围住一处幽静。','Wang Meng surrounds a quiet retreat with restless brushwork.'),
(39,47,'安宁不是空无，而是纷扰中的一小块空间。','Calm is a small space held inside turbulence.'),
(52,61,'世界似乎可以被测量。','The world appears measurable.'),
(63,73,'但丢勒的《忧郁 I》，没有给出单一答案。','Yet Dürer’s Melencolia I offers no single answer.'),
(76,83,'工具越精密，人的迟疑越清晰。','The sharper our tools, the clearer our uncertainty.'),
(88,98,'在北斋的浪中，山峰缩成远处的一点。','In Hokusai’s wave, the mountain contracts into the distance.'),
(100,110,'木版让瞬间可以重复，蓝色跨过海洋。','Woodblocks repeat an instant; blue travels across oceans.'),
(112,119,'我们既渴望力量，也知道自己脆弱。','We long for power, knowing how fragile we are.'),
(124,134,'修拉把夜晚，分解为彼此相邻的色点。','Seurat breaks the night into neighboring touches of color.'),
(136,146,'人群聚集在灯下。目光，也成为一种交易。','A crowd gathers in artificial light. Attention becomes an exchange.'),
(148,155,'越是明亮，越能感到人与人之间的距离。','The brighter the spectacle, the more palpable the distance.'),
(160,170,'二十世纪的抽象，试着重新安排关系。','Twentieth-century abstraction tries to rearrange relationships.'),
(172,181,'在蒙德里安那里，平衡是一种理想。','For Mondrian, equilibrium is an ideal.'),
(186,195,'今天，每一种目光都可能被计算。','Today, every glance can become a measurement.'),
(197,205,'被看见，不等于被理解。','To be seen is not necessarily to be understood.'),
(207,216,'也许美，是把注意力重新交还给自己。','Perhaps beauty is the return of our attention to ourselves.'),
]
CH=[(12,48,'01','栖居','DWELL','约 1370 / c. 1370','retreat','王蒙 · 素庵图','Wang Meng · Simple Retreat'),(48,84,'02','尺度','MEASURE','1514','melencolia','阿尔布雷希特·丢勒 · 忧郁 I','Albrecht Dürer · Melencolia I'),(84,120,'03','临界','VULNERABILITY','约 1830–32 / c. 1830–32','wave','葛饰北斋 · 神奈川冲浪里','Katsushika Hokusai · The Great Wave'),(120,156,'04','光的市场','SPECTACLE','1887–88','sideshow','乔治·修拉 · 马戏团的巡演','Georges Seurat · Circus Sideshow'),(156,184,'05','关系','RELATIONS','1920s',None,'新造型主义的回声','An echo of Neo-Plasticism'),(184,218,'06','归还','RETURN','当下 / THE PRESENT',None,'注意力的内在风景','An inward landscape of attention')]

def text(im,xy,s,size=26,col=(235,232,223),alpha=1,anchor=None,serif=False):
 if alpha<=0:return
 d=ImageDraw.Draw(im);d.text(xy,s,font=font(size,serif),fill=tuple(int(v*alpha) for v in col),anchor=anchor)
def overlay_text(im,xy,s,size=26,col=(235,232,223),alpha=1,anchor=None,serif=False):
 layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer);d.text(xy,s,font=font(size,serif),fill=(*col,int(255*alpha)),anchor=anchor);im.paste(layer,(0,0),layer)
def cropfill(key,zoom=1,px=.5,py=.5):
 im=ART[key]; sw,sh=im.size; ar=W/H
 cw=min(sw,sh*ar)/zoom;ch=cw/ar
 cx=cw/2+(sw-cw)*px;cy=ch/2+(sh-ch)*py
 return im.crop((cx-cw/2,cy-ch/2,cx+cw/2,cy+ch/2)).resize((W,H),Image.Resampling.BICUBIC)
def art_card(key,u):
 # Preserve the complete source at the beginning; then reveal a deliberate detail.
 bg=DARK.copy(); im=ART[key].copy(); im.thumbnail((880,510),Image.Resampling.LANCZOS)
 bg.paste(im,((W-im.width)//2,(H-im.height)//2-6))
 if u>7:
  detail=cropfill(key,1.08+max(0,u-7)*.008, .57 if key=='retreat' else .49,.52 if key=='retreat' else .5)
  bg=Image.blend(bg,detail,smooth((u-7)/3))
 return bg

def ink(u):
 im=PAPER.copy(); d=ImageDraw.Draw(im)
 # Multiple autonomous contours travel at different speeds, without a single vanishing point.
 for layer in range(8):
  xs=np.linspace(-120,W+120,360); shift=u*(2+layer*.7)
  ys=H*.63+layer*25 - (110-layer*6)*np.exp(-((xs-(450+layer*65+shift)) / (200+layer*15))**2)
  ys-= (130-layer*7)*np.exp(-((xs-(930-layer*30-shift*.7))/(160+layer*12))**2)
  ys+=12*np.sin(xs*.013+layer*1.8)+8*np.sin(xs*.041+layer)
  pts=list(zip(xs.astype(int),ys.astype(int)))+[(W+120,H),(-120,H)]
  col=mix((196,198,181),(39,55,52),layer/9)
  d.polygon(pts,fill=col)
  for j in range(5):
   p=[(int(x),int(y+9*j+2*np.sin(x*.06+j))) for x,y in zip(xs,ys)]
   d.line(p,fill=mix(col,(225,220,208),.24),width=1)
 # A blank river cuts through density; it's a moving interval rather than emptiness.
 river=[]
 for y in np.linspace(320,720,140):
  frac=(y-320)/400;cx=715+90*np.sin(frac*4+u*.025);rw=6+frac**2*92
  river.append((int(cx-rw),int(y)))
 for y in np.linspace(720,320,140):
  frac=(y-320)/400;cx=715+90*np.sin(frac*4+u*.025);rw=6+frac**2*92
  river.append((int(cx+rw),int(y)))
 d.polygon(river,fill=(215,214,199))
 # Sparse calligraphic reeds; not a reconstruction of the source painting.
 for j in range(19):
  x=130+j*49; y=490+65*math.sin(j*1.9);h=18+18*(j%3)
  d.line((x,y,x+3*math.sin(u*.12+j),y-h),fill=(35,48,46),width=2)
  d.line((x,y-h*.45,x-8,y-h*.7),fill=(35,48,46),width=1)
 return im

HATCH=Image.new('L',(W,H));hd=ImageDraw.Draw(HATCH)
for hx in range(-H,W,7):hd.line((hx,0,hx+H,H),fill=110,width=1)

verts=np.array([[-1,-1,-.55],[1,-1,-.55],[1,1,-.55],[-1,1,-.55],[-.5,-.5,1.25],[.5,-.5,1.25],[.5,.5,1.25],[-.5,.5,1.25]])
faces=[[0,1,2,3],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
def geometry(u):
 im=paper((197,188,168),1);d=ImageDraw.Draw(im)
 horizon=310
 for i in range(-10,11):d.line((640+i*24,horizon,640+i*230,720),fill=(145,137,119),width=1)
 for y in [330,359,401,466,554,675]:d.line((0,y,W,y),fill=(155,146,126),width=1)
 a=u*.09+.25;b=.25+.15*math.sin(u*.05)
 R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
 vv=verts@R; vv=np.column_stack((vv[:,0],vv[:,1]*math.cos(b)-vv[:,2]*math.sin(b),vv[:,1]*math.sin(b)+vv[:,2]*math.cos(b)))
 pts=np.column_stack((640+vv[:,0]*205/(1+vv[:,1]*.12),385-vv[:,2]*190/(1+vv[:,1]*.12)))
 for f in sorted(faces,key=lambda f:np.mean(vv[f,1]),reverse=True):
  shade=int(80+80*(np.mean(vv[f,2])+1)/2);col=(shade+17,shade+8,shade-7)
  pp=[tuple(p) for p in pts[f]];d.polygon(pp,fill=col);d.line(pp+[pp[0]],fill=(54,50,45),width=2)
  # Clipped hatch lines follow each actual projected polygon, giving copperplate weight.
  mask=Image.new('L',(W,H));md=ImageDraw.Draw(mask);md.polygon(pp,fill=255)
  mask=ImageChops.multiply(mask,HATCH)
  im.paste((35,35,32),(0,0,W,H),mask);d=ImageDraw.Draw(im)
 # Orbital dividers are deliberately unable to enclose the entire form.
 rad=258+8*math.sin(u*.2)
 d.arc((640-rad,354-rad,640+rad,354+rad),int(u*3)%360,int(u*3)%360+245,fill=(70,66,58),width=1)
 for angle in range(0,360,15):
  r=math.radians(angle);x=640+rad*math.cos(r);y=354+rad*math.sin(r)
  d.line((x,y,x+7*math.cos(r),y+7*math.sin(r)),fill=(81,76,64),width=1)
 return im

def wave(u):
 im=paper((219,222,212),1);d=ImageDraw.Draw(im)
 # The tiny mountain remains fixed while layered wave contours sweep toward the viewer.
 d.polygon([(920,330),(972,269),(1032,330)],fill=(62,83,104));d.polygon([(956,289),(972,269),(987,289)],fill=(236,232,215))
 for j in range(15):
  xs=np.linspace(-120,1400,400)
  phase=xs*.006-u*.4+j*.22
  ys=397+j*20+math.sin(u*.23+j)*6+np.sin(phase)*(42+j*1.5)
  ys-= 150*np.exp(-((xs-(390+95*math.sin(u*.12)+j*8))/155)**2)*(1-j/24)
  pts=list(zip(xs.astype(int),ys.astype(int)))+[(W+120,H),(-120,H)]
  col=mix((164,185,189),(13,49,82),j/14);d.polygon(pts,fill=col)
  d.line(list(zip(xs.astype(int),ys.astype(int))),fill=(222,225,209) if j%3==0 else (87,126,147),width=2)
  if j<6:
   for k in range(9):
    x=330+j*13+k*17+70*math.sin(u*.12);y=255+j*24-22*math.sin(k*.6+u*.4)
    d.arc((x-10,y-8,x+10,y+9),30,265,fill=(235,234,219),width=2)
 return im

# A spatial point cloud sampled from the actual Seurat reproduction.
sm=ART['sideshow'].resize((112,75),Image.Resampling.LANCZOS)
SC=np.asarray(sm).reshape(-1,3)
SX,SY=np.meshgrid(np.linspace(-1,1,112),np.linspace(-.67,.67,75));SX=SX.ravel();SY=SY.ravel(); SZ=RNG.uniform(-.8,.8,len(SX))
def particles(u):
 im=DARK.copy();d=ImageDraw.Draw(im)
 expand=smooth((u-5)/17); ang=expand*.52*math.sin(u*.1)
 x=SX*math.cos(ang)+SZ*math.sin(ang)*expand;y=SY;z=-SX*math.sin(ang)+SZ*math.cos(ang)*expand
 depth=1.7+z*.65;fac=1+expand*.3
 xp=640+x*600*fac/depth;yp=355+y*600*fac/depth
 # Pixels become bodies with distinct depths, occlusion, and independent trajectories.
 xp+=np.sin(SY*12+u*.32)*expand*22;yp+=np.cos(SX*9+u*.24)*expand*17
 for idx in np.argsort(z)[::-1]:
  x1,y1=xp[idx],yp[idx];r=max(1.2,3.4/depth[idx]);c=SC[idx];cc=tuple(min(255,int(v*(1.1+expand*.35))) for v in c)
  d.ellipse((x1-r,y1-r,x1+r,y1+r),fill=cc)
 return im

def relations(u):
 im=paper((230,229,220),.6);d=ImageDraw.Draw(im)
 # An original kinetic composition, not a facsimile of any Mondrian painting.
 settle=smooth(u/13); wobble=(1-settle)*math.sin(u*.9)*80 + 9*math.sin(u*.17)
 xs=[0,238+wobble,558-wobble*.4,870+wobble*.6,1100,W]
 ys=[0,190-wobble*.4,416+wobble*.5,560,H]
 cols={(0,1):(153,33,31),(2,0):(32,60,102),(4,2):(214,176,31),(1,3):(51,52,49),(3,1):(209,210,199)}
 for (ix,iy),c in cols.items():d.rectangle((xs[ix],ys[iy],xs[ix+1],ys[iy+1]),fill=c)
 for x in xs[1:-1]:d.line((x,0,x,H),fill=(17,23,26),width=14)
 for y in ys[1:-1]:d.line((0,y,W,y),fill=(17,23,26),width=14)
 # A narrow interval refuses to close; asymmetry is a relationship, not uniformity.
 return im

def present(u):
 im=DARK.copy();d=ImageDraw.Draw(im)
 release=smooth((u-11)/19); freq=1.0-release*.83
 # Start with a crowded field of luminous frames, then return to one breathing aperture.
 for i in range(68):
  angle=i*2.39996+u*.025; radius=55+math.sqrt(i)*37+(release*420)
  x=640+math.cos(angle)*radius*1.5;y=335+math.sin(angle)*radius*.83
  bw=35+(i%5)*13;bh=bw*.65; strength=(1-release)*(.22+.3*((i%7)/7))
  c=mix((12,16,20),[(68,112,129),(164,101,65),(180,184,160)][i%3],strength)
  d.rectangle((x-bw,y-bh,x+bw,y+bh),outline=c,width=1)
  for k in range(3):d.line((x-bw+6,y+6*k-bh+8,x+bw-6,y+6*k-bh+8),fill=mix(c,(12,16,20),.5),width=1)
 # Dense generative contours inherit ink, engraving, wave and divided color.
 for j in range(48):
  tt=np.linspace(0,2*math.pi,420)
  rr=86+j*2.7 + (18+22*(1-release))*np.sin(tt*3+u*.21+j*.025)
  rr+=8*np.sin(tt*7-u*.13+j*.09)*(1-release)
  rx=rr*(1+.2*math.sin(u*.12));ry=rr*.79
  px=640+rx*np.cos(tt);py=337+ry*np.sin(tt)
  col=mix((27,44,50),(167,189,183),j/48*.68+release*.2)
  d.line(list(zip(px.astype(int),py.astype(int))),fill=col,width=1)
 # Central blank space expands with a slow respiratory rhythm.
 r=64+release*16+5*math.sin(u*math.pi/4)
 d.ellipse((640-r,337-r*.8,640+r,337+r*.8),fill=(12,16,20))
 return im


INNER=Image.open(P/'assets'/'inner-life.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
TILES=[]
for ty in range(0,H,32):
 for tx in range(0,W,32):
  seed=(tx*13+ty*37)%157
  TILES.append((tx,ty,INNER.crop((tx,ty,min(W,tx+32),min(H,ty+32))),seed))
def inner_life(u):
 im=DARK.copy();d=ImageDraw.Draw(im)
 settle=smooth((u-1)/24)
 # Tile trajectories reassemble a generated portrait, so the present moves from
 # a quantized field toward a continuous, embodied image rather than a zoom.
 for x,y,tile,seed in TILES:
  local=smooth((u-1-(seed%11)*.5)/19)
  dx=(1-local)*(120*math.sin(seed+u*.16)+(x-640)*.35)
  dy=(1-local)*(95*math.cos(seed*1.7+u*.13)+(y-360)*.2)
  if local<.08:continue
  ti=ImageEnhance.Brightness(tile).enhance(.2+.8*local)
  im.paste(ti,(int(x+dx),int(y+dy)))
 # Extremely fine moving water contours are laid over the image's lower edge.
 d=ImageDraw.Draw(im)
 for k in range(12):
  xs=np.linspace(0,W,240);ys=635+k*7+2*np.sin(xs*.018+u*.3+k)
  d.line(list(zip(xs.astype(int),ys.astype(int))),fill=(26+k,35+k,36+k),width=1)
 return im

def opening(t):
 im=present(t+19);d=ImageDraw.Draw(im)
 im=Image.blend(DARK,im,.34)
 a=fade(t,1,11,1.2)
 overlay_text(im,(640,257),'观看的重量',58,(229,231,222),a,'mm',True)
 overlay_text(im,(640,321),'THE WEIGHT OF SEEING',22,(166,190,189),a,'mm')
 overlay_text(im,(640,378),'六次观看 · 一处内心',20,(181,184,176),a,'mm')
 overlay_text(im,(640,414),'SIX WAYS OF SEEING · ONE INNER LIFE',14,(142,153,151),a,'mm')
 return im

def credits(t):
 im=DARK.copy()
 if t<222:
  a=fade(t,218,222,.6)
  for y,st,n in [(240,'观看的重量 / THE WEIGHT OF SEEING',32),(311,'Wang Meng · Albrecht Dürer · Katsushika Hokusai · Georges Seurat',19),(355,'The Metropolitan Museum of Art · Open Access / CC0',17),(430,'原创动画与电子声景 / ORIGINAL MOTION & SOUND',16)]:overlay_text(im,(640,y),st,n,(216,222,215),a,'mm')
 else:
  a=fade(t,222,228,.6)
  overlay_text(im,(640,263),'观看，仍在继续。',35,(222,231,221),a,'mm',True)
  overlay_text(im,(640,315),'KEEP LOOKING.',15,(141,172,171),a,'mm')
  overlay_text(im,(640,398),'weight-of-seeing.yydshly.chatgpt.site',22,(204,219,212),a,'mm')
  overlay_text(im,(640,444),'作品与资料 / FILM & SOURCES',14,(133,155,153),a,'mm')
 return im

def frame(t):
 if t<12:im=opening(t); light=False
 elif t>=218:return credits(t)
 else:
  c=next(c for c in CH if c[0]<=t<c[1]);start,end,num,zh,en,era,key,artist,artist_en=c;u=t-start
  fn={'01':ink,'02':geometry,'03':wave,'04':particles,'05':relations,'06':inner_life}[num]
  original=fn(max(0,u-10) if key else u)
  if key:
   a=smooth((u-12)/5)
   im=Image.blend(art_card(key,u),original,a) if a<1 else original
  else:im=original
  light=num in ['01','02','03','05'] and (not key or u>15)
  # Keep source / reinterpretation status unambiguous during transitions.
  status='原作 / SOURCE' if key and u<12 else ('转化 / TRANSITION' if key and u<17 else '原创视觉转译 / ORIGINAL INTERPRETATION')
  header_alpha=1-smooth((u-9)/3)
  top=Image.new('RGBA',(W,H));td=ImageDraw.Draw(top);td.rectangle((0,0,W,117),fill=(7,12,15,int(210*header_alpha)));im.paste(top,(0,0),top)
  overlay_text(im,(48,24),num,18,(131,158,161),header_alpha);overlay_text(im,(91,16),zh,32,(235,231,217),header_alpha,serif=True)
  overlay_text(im,(91,62),en,14,(175,191,189),header_alpha);overlay_text(im,(W-48,29),era,18,(203,208,197),header_alpha,anchor='ra')
  overlay_text(im,(W-48,62),status,13,(144,166,167),header_alpha,anchor='ra')
  if u>=12: text(im,(48,36),status,12,(56,71,72) if light else (126,150,151))
  if key and u<17:
   # Name persists long enough to read; subdued below the top bar.
   layer=Image.new('RGBA',(W,H));dd=ImageDraw.Draw(layer);dd.rectangle((36,128,680,196),fill=(8,13,17,190));im.paste(layer,(0,0),layer)
   text(im,(49,130),artist,20);text(im,(49,162),artist_en,14,(182,193,191))
  if num=='05' and u<10:
   text(im,(48,136),'借鉴历史语言的原创构成 / ORIGINAL COMPOSITION',14,(29,41,44))
  # Chapter breathing space: motivated low-amplitude dip, no flashing.
  boundary=min(smooth(u/.65),smooth((end-t)/.65)); im=Image.blend(DARK,im,boundary)
 # Consistent subtitle well, visually outside the historical image register.
 active=next((c for c in CAP if c[0]<=t<c[1]),None)
 if active:
  a=fade(t,active[0],active[1],.55)
  lay=Image.new('RGBA',(W,H));ld=ImageDraw.Draw(lay);ld.rectangle((0,603,W,H),fill=(5,10,13,int(221*a)));im.paste(lay,(0,0),lay)
  overlay_text(im,(640,635),active[2],26,(243,241,229),a,'mm',True)
  overlay_text(im,(640,676),active[3],19,(202,216,211),a,'mm')
 return im

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--sample',action='store_true');ap.add_argument('--stills',action='store_true');args=ap.parse_args()
 if args.stills:
  ts=[5,18,30,42,54,67,79,90,103,114,126,138,151,162,177,188,203,212,222]
  sheet=Image.new('RGB',(1280,math.ceil(len(ts)/3)*264),(5,10,13));sd=ImageDraw.Draw(sheet)
  for i,t in enumerate(ts):
   f=frame(t);f.save(P/'qa'/f'frame-{t:03}.jpg',quality=95);thumb=f.resize((420,236));x=(i%3)*426;y=(i//3)*264;sheet.paste(thumb,(x,y));sd.text((x+8,y+237),str(t)+'s',font=font(16),fill='white')
  sheet.save(P/'qa'/'contact-sheet.jpg',quality=92);return
 times=np.arange(0,DURATION,1/FPS) if not args.sample else np.concatenate([np.arange(a,a+4,1/FPS) for a in [20,40,76,110,149,177,208]])
 out=P/'output'/('sample-silent.mp4' if args.sample else 'film-silent.mp4')
 cmd=['ffmpeg','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','22','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=open(P/'output'/'render.log','w'))
 for i,t in enumerate(times):
  p.stdin.write(frame(float(t)).tobytes())
  if i%(FPS*4)==0:print(f'{i}/{len(times)} frames, time={t:.1f}s',flush=True)
 p.stdin.close();p.wait();assert p.returncode==0
 print(out,flush=True)
if __name__=='__main__': main()
