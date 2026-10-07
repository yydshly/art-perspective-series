"""Episode 002: a 20-second original motion/sound study, not the final film.
No historical images, purchased assets, external APIs or model-generated claims.
"""
from pathlib import Path
import math,subprocess,wave,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
P=Path(__file__).resolve().parent;ROOT=P.parent
W,H,FPS,D=1280,720,24,20
FONT='/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc';SANS='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
rng=np.random.default_rng(224)
def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
def window(t,a,b):return ease((t-a)/.8)*ease((b-t)/.8)
base=rng.normal(0,.8,(H,W,1));x=np.linspace(-1,1,W)[None,:];y=np.linspace(-1,1,H)[:,None]
shade=(-4*(x*x+y*y))[...,None]
PAPER=np.clip(np.array([222,223,211])[None,None,:]+base+shade,0,255).astype('uint8')
# Fine fibers are fixed to the material; no random frame-to-frame noise.
fibers=[]
for i in range(1100):
 xx=float(rng.uniform(0,W));yy=float(rng.uniform(0,H));fibers.append((xx,yy,xx+float(rng.uniform(1,5)),yy+float(rng.uniform(-1,1))))
font=lambda n:ImageFont.truetype(FONT,n)
sans=lambda n:ImageFont.truetype(SANS,n)
def frame(t):
 release=ease((t-4)/8)
 im=Image.fromarray(PAPER.copy());d=ImageDraw.Draw(im)
 for l in fibers:d.line(l,fill=(207,212,202),width=1)
 # The line starts obedient to a periodic grid, then acquires a slower independent rhythm.
 xs=np.linspace(-100,W+100,520)
 for k in range(43):
  phase=xs*.010-t*(.83*(1-release)+.10)
  pulse=(np.sin(phase)*13+np.sin(xs*.022+t*.7)*3)*(1-release)
  breath=math.sin((t-6)*math.pi/6)
  center=650+16*math.sin(t*.06)
  organic=(28+breath*4)*np.sin((xs-center)*.006+.8)*np.exp(-((xs-center)/300)**2)
  yy=385+(k-21)*1.8 + pulse + release*(organic+(k-21)*.65*np.exp(-((xs-center)/250)**2))
  col=(int(99-k*.45),int(125-k*.48),int(123-k*.45))
  d.line(list(zip(xs.astype(int),yy.astype(int))),fill=col,width=1)
 # Measurement remains at the margins; responsibility isn't magically erased.
 for i in range(37):
  xx=70+i*32
  strength=(1-release)*.65 + (0.18 if i in [0,36] else 0)
  col=tuple(int(PAPER[0,0,j]*(1-strength)+[90,108,105][j]*strength) for j in range(3))
  top=218+12*math.sin(i*.5+t*.5)*(1-release)
  bottom=460+15*math.sin(i*.4+t*.5)*(1-release)
  d.line((xx,top,xx,bottom),fill=col,width=1)
 # At the center, the rhythm opens into a materially empty interval.
 gap=ease((t-6)/7)*94
 if gap>0:
  mask=Image.new('L',(W,H));md=ImageDraw.Draw(mask);md.ellipse((640-gap,359-gap*.36,640+gap,399+gap*.36),fill=255)
  mask=mask.filter(ImageFilter.GaussianBlur(22));im.paste(Image.fromarray(PAPER),(0,0),mask)
 layer=Image.new('RGBA',(W,H));ld=ImageDraw.Draw(layer)
 a=window(t,0,4)
 ld.text((55,40),'暂停的权利',font=font(29),fill=(38,58,57,int(a*255)))
 ld.text((56,88),'THE RIGHT TO PAUSE',font=sans(13),fill=(71,91,88,int(a*255)))
 ld.text((1225,47),'002 · 20秒声画短样 / MOTION STUDY',font=sans(12),fill=(91,109,103,200),anchor='ra')
 if 1<=t<6:
  a=window(t,1,6)
  ld.text((640,565),'连停下来，也像需要一个理由。',font=font(27),fill=(31,50,47,int(a*255)),anchor='mm')
  ld.text((640,608),'Even stopping seems to require a reason.',font=sans(18),fill=(63,84,78,int(a*255)),anchor='mm')
 if 10<=t<17.5:
  a=window(t,10,17.5)
  ld.text((640,565),'有些重要的事，不会立刻变成结果。',font=font(27),fill=(31,50,47,int(a*255)),anchor='mm')
  ld.text((640,608),'Some important things do not become results immediately.',font=sans(18),fill=(63,84,78,int(a*255)),anchor='mm')
 im.paste(layer,(0,0),layer)
 return im

def audio():
 sr=48000;out=np.zeros((D*sr,2),dtype=np.float32)
 def note(start,f,dur,amp,pan=0,click=False):
  n=int(dur*sr);t=np.arange(n)/sr
  env=(1-np.exp(-t*40))*np.exp(-t*(22 if click else 1.15))
  z=(np.sin(2*np.pi*f*t)+.25*np.sin(2*np.pi*f*2.01*t))*env*amp
  st=int(start*sr);n=min(n,len(out)-st)
  out[st:st+n,0]+=z[:n]*math.sqrt((1-pan)/2);out[st:st+n,1]+=z[:n]*math.sqrt((1+pan)/2)
 for i,a in enumerate([.4,1.2,2,2.8,3.6,4.5,5.7]):note(a,190+i*8,.35,.12,(-1)**i*.3,True)
 # The pause at 7–8 seconds is part of the composition, not missing audio.
 for a,f,amp in [(0,110,.045),(3,165,.03),(8.2,220,.055),(11.6,329.628,.042),(15.2,220,.038)]:note(a,f,5.5,amp,.1)
 out*=np.minimum(np.arange(len(out))/sr,1)[:,None]*np.minimum((len(out)-np.arange(len(out)))/sr/2,1)[:,None]
 out*=.42/max(np.max(np.abs(out)),1e-6)
 with wave.open(str(ROOT/'media'/'sample-score.wav'),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr);f.writeframes((out*32767).astype('<i2').tobytes())

if __name__=='__main__':
 (ROOT/'media').mkdir(exist_ok=True);(ROOT/'qa').mkdir(exist_ok=True)
 audio()
 p=subprocess.Popen(['ffmpeg','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r','24','-i','-','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','22','-pix_fmt','yuv420p',str(ROOT/'media'/'sample-silent.mp4')],stdin=subprocess.PIPE,stderr=open(ROOT/'qa'/'render.log','w'))
 for n in range(D*FPS):p.stdin.write(frame(n/FPS).tobytes())
 p.stdin.close();p.wait();assert p.returncode==0
 for t in [2,7,12,18]:frame(t).save(ROOT/'qa'/f'sample-{t:02}.jpg',quality=94)
 subprocess.run(['ffmpeg','-y','-i',str(ROOT/'media'/'sample-silent.mp4'),'-i',str(ROOT/'media'/'sample-score.wav'),'-c:v','copy','-af','loudnorm=I=-20:TP=-3:LRA=10','-c:a','aac','-b:a','128k','-ar','48000','-movflags','+faststart',str(ROOT/'media'/'The-Right-to-Pause-20s-Study.mp4')],check=True,stderr=open(ROOT/'qa'/'mux.log','w'))
 print('20-second study rendered')
