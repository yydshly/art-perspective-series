"""002 v2, original painterly diptych animated as a 20s cinematic study.
Illustrated fictional adult, not documentary footage. v1 was rejected.
"""
from pathlib import Path
import math,subprocess,wave,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageEnhance
P=Path(__file__).resolve().parent;R=P.parent;W,H,FPS,D=1280,720,24,20
F='/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc';S='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
A=Image.open(P/'assets-v2/before-dawn.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
B=Image.open(P/'assets-v2/morning-pause.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
AA=np.asarray(A).astype(np.float32);BB=np.asarray(B).astype(np.float32)
rng=np.random.default_rng(22319)
xx=np.arange(W)[None,:];yy=np.arange(H)[:,None]
# Atmospheric movement is spatially restricted to the window, without deforming the figure.
WINDOW=np.clip((xx-940)/200,0,1)*np.clip((440-yy)/100,0,1)
LAMP=np.exp(-((xx-205)/190)**2-((yy-320)/240)**2)
DUST=[(float(rng.uniform(915,1230)),float(rng.uniform(60,425)),float(rng.uniform(.6,1.7)),float(rng.uniform(0,6))) for _ in range(45)]
def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
def w(t,a,b):return ease((t-a)/.6)*ease((b-t)/.6)
def text_layer(im,t):
 l=Image.new('RGBA',(W,H));d=ImageDraw.Draw(l)
 d.text((1240,30),'002 · 重做短样 V2 / REVISED STUDY',font=ImageFont.truetype(S,12),fill=(203,217,210,185),anchor='ra')
 cap=None
 if 1<t<5.8:cap=('那些未完成的事，仍在桌上。','The unfinished work is still on the desk.',w(t,1,5.8))
 if 11.5<t<16.5:cap=('这一刻，她先望向窗外。','For this moment, she looks toward the window.',w(t,11.5,16.5))
 if cap:
  zh,en,a=cap;d.rectangle((0,603,W,H),fill=(5,12,17,int(172*a)))
  d.text((640,637),zh,font=ImageFont.truetype(F,27),fill=(243,237,220,int(255*a)),anchor='mm')
  d.text((640,679),en,font=ImageFont.truetype(S,18),fill=(217,226,220,int(255*a)),anchor='mm')
 if 17<t<20:
  a=w(t,17,20);d.text((1130,571),'暂停的权利',font=ImageFont.truetype(F,37),fill=(245,234,210,int(255*a)),anchor='ra');d.text((1130,623),'THE RIGHT TO PAUSE',font=ImageFont.truetype(S,15),fill=(208,221,217,int(255*a)),anchor='ra')
 im.paste(l,(0,0),l);return im

def wide(t,after=False):
 arr=(BB if after else AA).copy()
 phase=math.sin(t*.31)
 if after:
  # Window reflection travels across existing paper edges and the surface of the desk.
  center=1150-95*ease((t-12)/8)
  strip=np.exp(-((xx-center)/155)**2)*np.clip((yy-460)/130,0,1)
  light=WINDOW*(.018+.01*phase)+strip*.045
  arr+=light[...,None]*np.array([130,105,67])[None,None,:]
 else:
  arr+=(LAMP*.013*math.sin(t*.8))[...,None]*np.array([120,80,38])[None,None,:]
 im=Image.fromarray(np.clip(arr,0,255).astype('uint8'))
 # Printed architectural planes compress toward the figure, then settle; not a whole-image pan/zoom.
 if not after:
  amount=1-ease((t-3)/3)
  for x0,x1,y0,y1,phase in [(40,230,20,205,0),(640,820,30,400,1),(890,990,15,450,2)]:
   dx=int(math.sin(t*.5+phase)*7*amount)
   patch=A.crop((x0,y0,x1,y1));patch=ImageEnhance.Brightness(patch).enhance(.86+.14*ease(t/5))
   im.paste(patch,(x0+dx,y0))
 else:
  layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
  for x,y,s,p in DUST:
   x+=math.sin(t*.22+p)*6;y=(y-(t-12)*(1.2+s))%390+20
   a=int((.4+.6*math.sin(p+t*.14)**2)*67);d.ellipse((x-s,y-s,x+s,y+s),fill=(226,220,183,a))
  im.paste(layer,(0,0),layer)
 return im

def detail(t,after):
 # A matched close-up of the same unfinished paper, hand and cup gives the transition a human anchor.
 src=B if after else A
 crop=src.crop((480,388,1050,708)).resize((W,H),Image.Resampling.LANCZOS)
 # Fine paper fibers drift only in the lower paper region, like a dissolving print impression.
 l=Image.new('RGBA',(W,H));d=ImageDraw.Draw(l)
 a=(1-ease((t-7)/4))*.25 if not after else ease((t-9)/3)*.13
 for j in range(36):
  x=70+j*32;y=478+16*math.sin(j*.73+t*.19)
  d.line((x,y,x+23,y-5),fill=(218,212,175,int(a*130)),width=1)
 crop.paste(l,(0,0),l);return crop

def frame(t):
 if t<6:im=wide(t,False)
 elif t<8.9:im=detail(t,False)
 elif t<10.1:im=Image.blend(detail(t,False),detail(t,True),ease((t-8.9)/1.2))
 elif t<12:im=detail(t,True)
 else:im=wide(t,True)
 return text_layer(im,t)

def score():
 sr=48000;out=np.zeros((D*sr,2),np.float32);rnd=np.random.default_rng(89)
 def add(at,f,dur,amp,pan=0,kind='felt'):
  n=int(dur*sr);t=np.arange(n)/sr
  if kind=='paper':
   z=np.convolve(rnd.normal(0,1,n),np.ones(31)/31,mode='same')*np.sin(np.pi*t/dur)**2;env=np.ones(n)
  elif kind=='wood':z=np.sin(2*np.pi*f*t)+.23*np.sin(2*np.pi*f*2.71*t);env=np.exp(-t*28)*(1-np.exp(-t*150))
  else:z=np.sin(2*np.pi*f*t+.9*np.sin(2*np.pi*f*2.003*t)*np.exp(-t*2))+.14*np.sin(2*np.pi*f*3*t);env=(1-np.exp(-t*35))*np.exp(-t*.82)
  z=z*env*amp;st=int(at*sr);n=min(n,len(out)-st);out[st:st+n,0]+=z[:n]*math.sqrt((1-pan)/2);out[st:st+n,1]+=z[:n]*math.sqrt((1+pan)/2)
 # An unresolved, close interval first; after the hand releases, it opens into a quieter fifth.
 for at,f,a in [(0,164.81,.075),(.16,174.61,.035),(3.8,164.81,.055),(8.8,146.83,.035),(12.1,196,.075),(12.35,293.66,.055),(16.4,196,.055)]:add(at,f,5.5,a)
 for j,at in enumerate([.8,1.8,2.9,4.1,5.5]):add(at,390+j*13,.28,.023,(-1)**j*.35,'wood')
 add(6.4,1,1.2,.034,-.25,'paper');add(10.2,1,.65,.013,.2,'paper')
 # Soft air at the window is newly possible after the shift in attention.
 add(12,1,7,.009,.4,'paper')
 for delay,gain in [(.17,.12),(.39,.075)]:n=int(delay*sr);out[n:]+=out[:-n,::-1]*gain
 out*=np.minimum(np.arange(len(out))/sr/.6,1)[:,None]*np.minimum((len(out)-np.arange(len(out)))/sr/1.4,1)[:,None]
 out*=.55/max(np.max(np.abs(out)),1e-6)
 with wave.open(str(R/'media/v2-score.wav'),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr);f.writeframes((out*32767).astype('<i2').tobytes())

if __name__=='__main__':
 score();p=subprocess.Popen(['ffmpeg','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r','24','-i','-','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','21','-pix_fmt','yuv420p',str(R/'media/v2-silent.mp4')],stdin=subprocess.PIPE,stderr=open(R/'qa/v2/render.log','w'))
 for n in range(D*FPS):p.stdin.write(frame(n/FPS).tobytes())
 p.stdin.close();p.wait();assert p.returncode==0
 subprocess.run(['ffmpeg','-y','-i',str(R/'media/v2-silent.mp4'),'-i',str(R/'media/v2-score.wav'),'-c:v','copy','-af','loudnorm=I=-20:TP=-3:LRA=10','-c:a','aac','-ar','48000','-b:a','128k','-movflags','+faststart',str(R/'media/The-Right-to-Pause-20s-v2.mp4')],check=True,stderr=open(R/'qa/v2/mux.log','w'))
 print('v2 render complete')
