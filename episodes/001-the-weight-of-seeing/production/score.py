"""Original generated score. No external recordings, melodies, voices or paid APIs."""
import numpy as np, wave,pathlib
P=pathlib.Path(__file__).parent;SR=48000;D=228
rng=np.random.default_rng(923)
y=np.zeros((D*SR,2),np.float32)
def add(start,duration,f,amp=.1,pan=0,kind='bell'):
 n=int(duration*SR);t=np.arange(n,dtype=np.float32)/SR
 if kind=='bell':
  env=(1-np.exp(-t*22))*np.exp(-t*.65)
  z=np.sin(2*np.pi*f*t+1.9*np.sin(2*np.pi*f*1.997*t)*np.exp(-t*1.8))+.22*np.sin(2*np.pi*f*3*t)*np.exp(-t*1.4)
 elif kind=='pad':
  env=np.sin(np.pi*t/duration)**1.7
  z=(np.sin(2*np.pi*f*t)+.4*np.sin(2*np.pi*f*1.002*t)+.2*np.sin(2*np.pi*f*2*t))/1.6
 elif kind=='tick':
  env=np.exp(-t*80);z=np.sin(2*np.pi*f*t)+rng.normal(0,.3,n)
 else:
  env=np.sin(np.pi*t/duration)**2
  # Integrated noise, low-passed as material friction rather than loud white noise.
  w=rng.normal(0,1,n);z=np.convolve(w,np.ones(75)/75,mode='same')*3
 z=(z*env*amp).astype(np.float32);i=int(start*SR);n=min(n,len(y)-i)
 if n<=0:return
 y[i:i+n,0]+=z[:n]*np.sqrt((1-pan)/2);y[i:i+n,1]+=z[:n]*np.sqrt((1+pan)/2)
# Harmonic centers recur across material changes; no imitation of historical ethnic music.
for a,b,root in [(0,48,110),(48,84,103.826),(84,120,123.471),(120,156,110),(156,184,130.813),(184,218,110)]:
 for start in np.arange(a,b,8):
  for mul,amp in [(1,.035),(1.5,.027),(2,.018)]:add(float(start),min(12,D-start),root*mul,amp,pan=(mul-1.5)*.7,kind='pad')
notes=[220,329.628,293.665,440,246.942,329.628,196,293.665]
for i,t in enumerate(np.arange(2,47,4.8)):add(float(t),7,notes[i%8],.09,pan=np.sin(i)*.5)
for i,t in enumerate(np.arange(49,82,2.7)):
 add(float(t),4,[207.652,311.127,277.183,415.305][i%4],.07,pan=(-1)**i*.45)
 add(float(t+.4),.17,1800,.017,pan=.4,kind='tick')
for i,t in enumerate(np.arange(85,118,5)):
 add(float(t),9,[246.942,369.994,493.883,329.628][i%4],.085,pan=np.sin(i)*.6);add(float(t),7,1,.017,pan=np.sin(i)*.3,kind='noise')
for i,t in enumerate(np.arange(121,155,1.4)):
 add(float(t),3,notes[(i*3)%8]*2,.04,pan=np.sin(i*1.3)*.7)
for i,t in enumerate(np.arange(157,183,2)):
 add(float(t),3,[261.626,392,523.251,293.665][i%4],.06,pan=(-1)**i*.4)
for i,t in enumerate(np.arange(185,200,.75)):
 add(float(t),1.8,notes[(i*5)%8]*2,.027,pan=np.sin(i)*.8)
for i,t in enumerate([200,205,210,216,222]):add(t,6,[220,329.628,293.665,220,110][i],.085,pan=0)
# A short stereo room, wholly deterministic.
for delay,gain in [(0.163,.14),(.317,.1),(.631,.055)]:
 off=int(delay*SR);y[off:]+=y[:-off,::-1]*gain
fade=np.minimum(np.arange(len(y))/SR/2,1)*np.minimum((len(y)-np.arange(len(y)))/SR/3,1)
y*=fade[:,None]
peak=np.max(np.abs(y));y*=.72/max(peak,1e-6)
with wave.open(str(P/'output'/'score.wav'),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR);f.writeframes((np.clip(y,-1,1)*32767).astype('<i2').tobytes())
print('original score',D,'seconds; peak',np.max(np.abs(y)))
