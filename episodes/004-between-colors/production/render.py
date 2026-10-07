"""Between Colors: bounded 36s study of color intervals from a Seurat source.
All depth and movement are original digital interpretations, not historical reconstruction.
"""
from pathlib import Path
import argparse, math, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
P=Path(__file__).resolve().parent;R=P.parent;ROOT=R.parents[1]
W,H,FPS,D=1280,720,24,36
SOURCE=ROOT/'episodes/001-the-weight-of-seeing/production/assets/sideshow.jpg'
art=Image.open(SOURCE).convert('RGB');art=art.crop((26,24,art.width-25,art.height-26))
font=lambda n:ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc',n)
sans=lambda n:ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',n)
def ease(v):v=np.clip(v,0,1);return v*v*(3-2*v)
def ramp(t,a,b):return float(ease((t-a)/(b-a)))
def cover(im):
 ratio=max(W/im.width,H/im.height);im=im.resize((round(im.width*ratio),round(im.height*ratio)),Image.Resampling.LANCZOS)
 return im.crop(((im.width-W)//2,(im.height-H)//2,(im.width+W)//2,(im.height+H)//2))
COVER=cover(art);small=np.asarray(COVER.resize((320,180)))
rng=np.random.default_rng(437654)
# Stratified color samples preserve the scene, with irregular spacing, depth and scale.
x,y=np.meshgrid(np.arange(3,W,6),np.arange(3,H,6));xy=np.c_[x.ravel(),y.ravel()].astype(float)
xy+=rng.uniform(-2.1,2.1,xy.shape);n=len(xy)
c=np.asarray(COVER)[np.clip(xy[:,1].astype(int),0,H-1),np.clip(xy[:,0].astype(int),0,W-1)].astype(float)
lum=c@np.array([.2126,.7152,.0722])/255
z=(lum-.25)*330+rng.normal(0,13,n);size=rng.uniform(1.5,3.6,n)
phase=rng.uniform(0,2*np.pi,n);grain=rng.normal(0,1.0,(H,W,1))
# Three color families remain interleaved; do not replace painted color with a rainbow palette.
family=np.argmax(c,axis=1)
def original():
 im=Image.new('RGB',(W,H),(10,16,23));a=art.copy();a.thumbnail((W-190,H-110));im.paste(a,((W-a.width)//2,(H-a.height)//2+16));return im
ORIGINAL=original()

def field(t):
 # 8–16: travel into paint; 16–26: open color intervals; 26–35: gather image; 35–38: settle.
 near=ramp(t,8,17)*(1-ramp(t,26,36));separate=ramp(t,15,22)*(1-ramp(t,27,35))
 shift=ramp(t,9,16);theta=.24*math.sin((t-8)*.15)*near
 focal=np.array([640-120*near,350-80*near]);q=xy-focal
 zoom=1+1.9*near
 # Colored depth layers rotate around a shared volume, preserving local color neighborhoods.
 xx=q[:,0]*math.cos(theta)+z*math.sin(theta)*2.2
 zz=-q[:,0]*math.sin(theta)+z*math.cos(theta)
 persp=1/(1+zz*.00075*near)
 px=640+xx*zoom*persp+(family-1)*48*separate
 py=360+q[:,1]*zoom*persp+zz*.4*separate
 # The movement draws on a slow geometric opening, not a sinusoidal water filter.
 px+=(xy[:,1]-360)*.17*separate
 py+=(xy[:,0]-640)*-.11*separate
 # At close range color particles occupy distinct, irregular planes; no fake museum relief claim.
 radial=1+2.9*near
 rad=size*radial*(.85+.5*lum)
 col=np.clip(c*(1+.22*separate)+np.c_[lum*9,lum*6,lum*4]*separate,0,255).astype(np.uint8)
 # A continuous painted substrate keeps optical color relationships beneath the marks.
 cropw=W/zoom;croph=H/zoom
 substrate=COVER.crop((focal[0]-cropw/2,focal[1]-croph/2,focal[0]+cropw/2,focal[1]+croph/2)).resize((W,H),Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(10+near*8))
 im=Image.blend(Image.new('RGB',(W,H),(11,19,29)),substrate,.34);d=ImageDraw.Draw(im)
 for j in np.argsort(zz):
  x1,y1=px[j],py[j];rr=rad[j]
  if -12<x1<W+12 and -12<y1<H+12:
   # Short impasto-like lozenges replace regular schematic circles.
   cc=tuple(int(v) for v in col[j]);r2=rr*(.65+.12*math.sin(phase[j]))
   d.polygon([(x1-rr,y1-r2*.45),(x1-rr*.45,y1-r2),(x1+rr*.75,y1-r2*.8),(x1+rr,y1+r2*.4),(x1+rr*.3,y1+r2),(x1-rr*.8,y1+r2*.7)],fill=cc)
   if near>.25 and rr>4:
    highlight=tuple(min(255,int(v*1.08+2)) for v in cc)
    d.line((x1-rr*.55,y1-r2*.3,x1+rr*.5,y1-r2*.5),fill=highlight,width=1)
 # Gentle optical fusion ties the near and distant states, while preserving point edges.
 glow=im.filter(ImageFilter.GaussianBlur(8));im=Image.blend(im,glow,.12+.09*(1-near))
 return Image.fromarray(np.uint8(np.clip(np.asarray(im).astype(float)+grain*1.7,0,255)))

def label(im,t,kind):
 layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
 if kind=='source':
  d.rectangle((0,0,W,69),fill=(8,14,22,225));d.text((38,15),'乔治·修拉  /  GEORGES SEURAT',font=sans(15),fill=(228,216,181))
  d.text((38,39),'马戏团巡演  /  CIRCUS SIDESHOW · 1887–88',font=sans(14),fill=(192,195,182))
  d.text((W-35,36),'原作 / SOURCE · THE MET · CC0',font=sans(11),fill=(161,182,188),anchor='ra')
 else:
  d.text((35,26),'原作色彩采样 · 原创运动转译 / COLOR STUDY · ORIGINAL MOTION',font=sans(11),fill=(200,205,194,230))
 if 1<t<5.8:
  a=ramp(t,1,2)*(1-ramp(t,4.8,5.8));d.rectangle((830,553,1250,679),fill=(9,15,24,int(210*a)))
  d.text((1215,572),'色彩之间',font=font(35),fill=(239,223,181,int(255*a)),anchor='ra');d.text((1215,635),'BETWEEN COLORS',font=sans(15),fill=(178,198,202,int(255*a)),anchor='ra')
 if t>37:
  a=ramp(t,37,38.5)*(1-ramp(t,40.8,42));d.rectangle((0,555,W,H),fill=(9,15,24,int(185*a)))
  d.text((640,590),'色彩之间',font=font(36),fill=(239,225,191,int(255*a)),anchor='ma');d.text((640,650),'BETWEEN COLORS · A COLOR-MOTION STUDY',font=sans(13),fill=(188,204,203,int(255*a)),anchor='ma')
 im.paste(layer,(0,0),layer);return im

def frame(t):
 t=t*42/D
 if t<6:im=ORIGINAL.copy();kind='source'
 elif t<8:im=Image.blend(ORIGINAL,COVER,ramp(t,6,8));kind='study'
 elif t<10:im=Image.blend(COVER,field(t),ramp(t,8,10));kind='study'
 elif t<36:im=field(t);kind='study'
 elif t<38:im=Image.blend(field(t),COVER,ramp(t,36,38));kind='study'
 else:im=COVER.copy();kind='study'
 im=label(im,t,kind)
 fade=ramp(t,0,1)*(1-ramp(t,40.8,42));return Image.blend(Image.new('RGB',(W,H),(8,13,20)),im,fade)

def score():
 sr=48000;out=np.zeros((D*sr,2),np.float32)
 def tone(start,dur,f,amp,pan,kind):
  start=start*D/42;dur=dur*D/42
  n=min(int(dur*sr),len(out)-int(start*sr));tt=np.arange(n)/sr
  if kind=='pad':env=np.sin(np.pi*tt/dur)**1.8;v=(np.sin(2*np.pi*f*tt)+.28*np.sin(2*np.pi*f*1.0018*tt)+.12*np.sin(2*np.pi*f*2*tt))
  else:env=(1-np.exp(-tt*25))*np.exp(-tt*.68);v=np.sin(2*np.pi*f*tt+.9*np.sin(2*np.pi*f*2.001*tt)*np.exp(-tt*2))+.09*np.sin(2*np.pi*f*3*tt)
  at=int(start*sr);out[at:at+n,0]+=v*env*amp*math.sqrt((1-pan)/2);out[at:at+n,1]+=v*env*amp*math.sqrt((1+pan)/2)
 # Form: low distant resonance -> separated upper colors -> return of the opening interval.
 for start,f in [(0,110),(8,130.813),(16,146.832),(24,123.471),(32,110)]:
  for mul,amp,pan in [(1,.025,-.1),(1.5,.018,.3),(2,.008,-.4)]:tone(start,min(12,42-start),f*mul,amp,pan,'pad')
 events=[(1.8,220,.055,-.2),(5.2,329.628,.047,.2),(8.7,261.626,.04,-.4),(11.8,392,.035,.4),(14.8,523.25,.03,-.2),(17.5,293.665,.04,-.5),(19.9,440,.029,.5),(22.3,587.33,.024,-.35),(24.7,493.883,.027,.35),(27.4,369.994,.034,-.2),(30.2,246.942,.04,.2),(33.4,329.628,.045,.1),(36.8,220,.055,0)]
 for at,f,a,p in events:tone(at,min(6,42-at),f,a,p,'bell')
 for delay,gain in [(.233,.13),(.467,.075),(.787,.035)]:n=int(delay*sr);out[n:]+=out[:-n,::-1]*gain
 tm=np.arange(len(out))/sr;out*=np.minimum(tm/2,1)[:,None]*np.minimum((D-tm)/3,1)[:,None];out*=.65/abs(out).max()
 with wave.open(str(R/'media/score.wav'),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr);f.writeframes((out*32767).astype('<i2').tobytes())

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--stills',action='store_true');ap.add_argument('--frame',type=float);args=ap.parse_args()
 if args.stills:
  for t in [3,6,9,14,18,22,27,31,34]:frame(t).save(R/'qa'/f'preflight-{t:02}.jpg',quality=92)
 elif args.frame is not None:frame(args.frame).save(R/'qa'/'single.png')
 else:
  score();log=open(R/'qa/render.log','w');p=subprocess.Popen(['ffmpeg','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','23','-pix_fmt','yuv420p',str(R/'media/silent.mp4')],stdin=subprocess.PIPE,stderr=log)
  for i in range(D*FPS):
   p.stdin.write(frame(i/FPS).tobytes())
   if i%120==0:print(i,'/',D*FPS,flush=True)
  p.stdin.close();p.wait();assert p.returncode==0
  subprocess.run(['ffmpeg','-y','-i',str(R/'media/silent.mp4'),'-i',str(R/'media/score.wav'),'-c:v','libx264','-threads','2','-preset','fast','-crf','27','-af','loudnorm=I=-19:TP=-3:LRA=8','-c:a','aac','-b:a','128k','-ar','48000','-movflags','+faststart',str(R/'media/Between-Colors-36s-Study.mp4')],check=True,stderr=open(R/'qa/mux.log','w'))
