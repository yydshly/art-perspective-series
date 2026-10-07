"""Within the Surface: 36s art-led study. Source art stays distinct from interpretation.
Patch surfaces are interpretive constructions, not a reconstruction of Monet's working method.
"""
from pathlib import Path
import math,subprocess,wave,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageEnhance
P=Path(__file__).resolve().parent;R=P.parent;W,H,FPS,D=1280,720,24,36
F='/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc';S='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
FONT=lambda n:ImageFont.truetype(F,n);SANS=lambda n:ImageFont.truetype(S,n)
ART=[Image.open(P/'assets'/n).convert('RGB') for n in ['pond-1900-reference.jpg','lilies-1906-reference.jpg']]
rng=np.random.default_rng(19001906)
def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
def gate(t,a,b,edge=.8):return ease((t-a)/edge)*ease((b-t)/edge)
def fill(im):
 w,h=im.size;hh=w*H/W;y=(h-hh)*.6
 return im.crop((0,y,w,y+hh)).resize((W,H),Image.Resampling.LANCZOS)
FILL=[fill(im) for im in ART]
BG=(8,19,27)

def lettering(im,t,index,status,opening=False):
 lay=Image.new('RGBA',(W,H));d=ImageDraw.Draw(lay)
 if status=='SOURCE':
  d.rectangle((0,0,W,89),fill=(5,12,16,214))
  d.text((42,19),'克劳德·莫奈  /  CLAUDE MONET',font=SANS(15),fill=(211,222,211,255))
  nm,dt=('睡莲池  /  WATER LILY POND','1900') if index==0 else ('睡莲  /  WATER LILIES','1906')
  d.text((42,48),nm,font=FONT(22),fill=(238,235,219,255));d.text((W-42,33),dt,font=SANS(21),fill=(217,224,214,255),anchor='ra')
  d.text((W-42,66),'原作 / SOURCE · ART INSTITUTE OF CHICAGO',font=SANS(11),fill=(143,174,173,255),anchor='ra')
 elif status=='TRANSITION':
  d.rectangle((29,25,350,57),fill=(5,12,16,175));d.text((41,30),'视觉转场 / TRANSITION',font=SANS(12),fill=(223,232,219,255))
 elif status=='DETAIL':
  d.rectangle((29,25,407,57),fill=(5,12,16,180));d.text((41,30),'原作局部 / SOURCE DETAIL',font=SANS(12),fill=(223,232,219,255))
 else:
  d.rectangle((29,25,430,57),fill=(5,12,16,175));d.text((41,30),'材质运动转译 / MATERIAL MOTION STUDY',font=SANS(12),fill=(223,232,219,255))
 if opening:
  a=gate(t,.5,5.6,.7)
  d.text((W-66,578),'水面之内',font=FONT(37),fill=(230,239,222,int(a*255)),anchor='ra')
  d.text((W-66,634),'WITHIN THE SURFACE',font=SANS(15),fill=(176,202,200,int(a*255)),anchor='ra')
 im.paste(lay,(0,0),lay);return im

# Source-only framing preserves the original whole image, then offers a fixed intentional detail.
def source(index,t,label=True):
 im=Image.new('RGB',(W,H),BG);art=ART[index].copy();art.thumbnail((W-150,H-120),Image.Resampling.LANCZOS)
 im.paste(art,((W-art.width)//2,(H-art.height)//2+20))
 return lettering(im,t,index,'SOURCE',index==0) if label else im

# Build irregular, textured paint tesserae. These retain sampled paint variation,
# and overlap rather than becoming uniform circles, blank geometry, or a fluid filter.
PATCH=[];COORD=[];DEPTH=[];UNDER=[]
for idx,art in enumerate(FILL):
 arr=np.asarray(art);lum=np.mean(arr,axis=2)/255;layer=[];coords=[];depth=[]
 base=ImageEnhance.Color(art).enhance(.96);base=ImageEnhance.Brightness(base).enhance(.96);UNDER.append(base.filter(ImageFilter.GaussianBlur(.7)))
 padded=Image.fromarray(np.pad(arr,((100,100),(100,100),(0,0)),mode='edge'))
 for gy in range(-20,H+21,15):
  for gx in range(-20,W+21,18):
   x=gx+rng.uniform(-8,8);y=gy+rng.uniform(-7,7);ix=int(np.clip(x,0,W-1));iy=int(np.clip(y,0,H-1))
   c=arr[iy,ix];chroma=(float(c.max())-float(c.min()))/255
   pw=int(rng.uniform(24,58));ph=int(rng.uniform(12,31))
   # Most marks follow the horizontal pond surface; vertical reflected foliage survives in darker strata.
   if idx==0 and y<310 and chroma>.16:pw,ph=ph,pw
   tile=padded.crop((int(x-pw/2)+100,int(y-ph/2)+100,int(x+pw/2)+100,int(y+ph/2)+100)).convert('RGBA')
   mask=Image.new('L',tile.size);md=ImageDraw.Draw(mask);tw,th=tile.size
   pts=[(0,th*.34),(tw*.13,th*.11),(tw*.43,0),(tw*.66,th*.13),(tw*.98,th*.24),(tw*.88,th*.66),(tw,th*.84),(tw*.68,th*.9),(tw*.38,th),(tw*.17,th*.83),(0,th*.68)]
   md.polygon(pts,fill=248);mask=mask.filter(ImageFilter.GaussianBlur(.7));tile.putalpha(mask)
   layer.append(tile);coords.append((x,y));depth.append((lum[iy,ix]-.43)*1.1+chroma*.9+rng.uniform(-.06,.06))
 PATCH.append(layer);COORD.append(np.array(coords));DEPTH.append(np.array(depth))

def paint_space(idx,u):
 coords=COORD[idx];z=DEPTH[idx];x=(coords[:,0]-640)/640;y=(coords[:,1]-360)/360
 # The 1900 construction opens around the bridge; the 1906 field places the eye inside color.
 amount=ease(u/4)
 if idx==0:
  theta=(-.10+.17*math.sin(u*.23))*amount
  X=x*np.cos(theta)+z*np.sin(theta)*.40; Z=-x*np.sin(theta)+z*np.cos(theta)
  sx=640+X*640*(1+.12*amount)/(1+Z*.085*amount)
  sy=360+y*350+Z*amount*35+np.sin(x*3+u*.19)*amount*5
 else:
  theta=.07*math.sin(u*.19)
  X=x*np.cos(theta)+z*np.sin(theta)*.42;Z=-x*np.sin(theta)+z*np.cos(theta)
  sx=640+X*640*(1+.18*amount)/(1+Z*.10*amount)
  sy=355+y*350+Z*amount*55+np.sin(x*2.5+u*.13)*amount*3
 im=UNDER[idx].copy()
 # Shadow follows actual tessera depth; the overall tonal field stays rich and continuous.
 for j in np.argsort(z):
  patch=PATCH[idx][j];px=int(sx[j]-patch.width/2);py=int(sy[j]-patch.height/2)
  im.paste(patch,(px,py),patch)
 return im.crop((40,40,W-40,H-40)).resize((W,H),Image.Resampling.BICUBIC)

def frame(t):
 if t<7:im=source(0,t)
 elif t<9:
  a=ease((t-7)/2);im=Image.blend(source(0,t,False),FILL[0].copy(),a);im=lettering(im,t,0,'DETAIL')
 elif t<15:
  u=t-9;a=ease(u/1.4);im=Image.blend(FILL[0],paint_space(0,u),a);im=lettering(im,t,0,'INTERPRETATION')
 elif t<16.2:
  im=Image.blend(paint_space(0,6),source(1,t,False),ease((t-15)/1.2));im=lettering(im,t,1,'TRANSITION')
 elif t<23:im=source(1,t)
 elif t<25:
  im=Image.blend(source(1,t,False),FILL[1].copy(),ease((t-23)/2));im=lettering(im,t,1,'DETAIL')
 else:
  u=t-25;im=Image.blend(FILL[1],paint_space(1,u),ease(u/1.4));im=lettering(im,t,1,'INTERPRETATION')
  if t>33:
   l=Image.new('RGBA',(W,H));d=ImageDraw.Draw(l);a=gate(t,33,36,.6)
   d.rectangle((0,575,W,H),fill=(5,15,25,int(a*140)))
   d.text((640,614),'水面之内',font=FONT(35),fill=(230,238,220,int(a*255)),anchor='mm');d.text((640,657),'WITHIN THE SURFACE',font=SANS(16),fill=(186,208,204,int(a*255)),anchor='mm');im.paste(l,(0,0),l)
 return im

def score():
 sr=48000;out=np.zeros((D*sr,2),np.float32);rnd=np.random.default_rng(8844)
 def add(at,f,dur,amp,pan=0,pad=False):
  n=int(dur*sr);tt=np.arange(n)/sr
  if pad:
   z=(np.sin(2*np.pi*f*tt)+.33*np.sin(2*np.pi*f*1.0018*tt)+.11*np.sin(2*np.pi*f*2*tt));env=np.sin(np.pi*tt/dur)**1.5
  else:
   z=np.sin(2*np.pi*f*tt+1.1*np.sin(2*np.pi*f*2.002*tt)*np.exp(-tt*1.6))+.16*np.sin(2*np.pi*f*3*tt);env=(1-np.exp(-tt*40))*np.exp(-tt*.68)
  st=int(at*sr);n=min(n,len(out)-st);a=z[:n]*env[:n]*amp
  out[st:st+n,0]+=a*math.sqrt((1-pan)/2);out[st:st+n,1]+=a*math.sqrt((1+pan)/2)
 # One timbral family with changing spacing and register, not a stock water-sound loop.
 for at,f in [(0,110),(7,123.47),(15,110),(23,130.81),(29,110)]:add(at,f,min(10,D-at),.020,0,True);add(at,f*1.5,min(10,D-at),.012,.3,True)
 for at,f,pan,amp in [(1,220,-.2,.07),(4.7,329.63,.3,.058),(8,293.66,-.3,.045),(9.8,440,.5,.03),(12.1,369.99,-.4,.035),(16.8,246.94,.1,.059),(20.7,329.63,-.3,.053),(24,261.63,-.15,.043),(25.6,392,.5,.028),(27.7,329.63,-.5,.033),(30.3,293.66,.2,.04),(33,220,0,.06)]:add(at,f,min(5.5,D-at),amp,pan)
 for delay,g in [(.211,.14),(.467,.075),(.821,.03)]:n=int(delay*sr);out[n:]+=out[:-n,::-1]*g
 fade=np.minimum(np.arange(len(out))/sr,1)*np.minimum((len(out)-np.arange(len(out)))/sr/1.2,1);out*=fade[:,None];out*=.58/np.max(abs(out))
 with wave.open(str(R/'media/study-score.wav'),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr);f.writeframes((out*32767).astype('<i2').tobytes())

if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--stills',action='store_true',help='Render the established preflight frames only')
 parser.add_argument('--frame',type=float,help='Render one frame at a time in seconds (0 <= t < 36)')
 parser.add_argument('--output-dir',type=Path,help='Separate output root; original assets remain read-only')
 args=parser.parse_args()
 if args.frame is not None and (not math.isfinite(args.frame) or not 0<=args.frame<D):parser.error('--frame must be between 0 and 36 (exclusive)')
 if args.output_dir:R=args.output_dir.resolve()
 (R/'qa').mkdir(parents=True,exist_ok=True);(R/'media').mkdir(parents=True,exist_ok=True)
 if args.frame is not None:
  target=R/'qa'/f'frame-{args.frame:g}.png';frame(args.frame).save(target);print(target);sys.exit()
 if args.stills:
  for t in [3,8,12,18,24,28,32,34]:frame(t).save(R/'qa'/f'preflight-{t:02}.jpg',quality=95)
  print('preflight frames ready');sys.exit()
 score();p=subprocess.Popen(['ffmpeg','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r','24','-i','-','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','21','-pix_fmt','yuv420p',str(R/'media/study-silent.mp4')],stdin=subprocess.PIPE,stderr=open(R/'qa/render.log','w'))
 for n in range(D*FPS):
  p.stdin.write(frame(n/FPS).tobytes())
  if n%96==0:print(n,'/',D*FPS,flush=True)
 p.stdin.close();p.wait();assert p.returncode==0
 subprocess.run(['ffmpeg','-y','-i',str(R/'media/study-silent.mp4'),'-i',str(R/'media/study-score.wav'),'-c:v','copy','-af','loudnorm=I=-19:TP=-3:LRA=9','-c:a','aac','-ar','48000','-b:a','128k','-movflags','+faststart',str(R/'media/Within-the-Surface-36s-Study.mp4')],check=True,stderr=open(R/'qa/mux.log','w'))
 print('36-second study complete')
