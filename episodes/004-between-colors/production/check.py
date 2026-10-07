"""Inspect encoded output and create evidence without equating metrics with acceptance."""
from pathlib import Path
import subprocess,json,hashlib
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent.parent;v=P/'media/Between-Colors-36s-Study.mp4'
def run(args):return subprocess.run(args,check=True,capture_output=True,text=True)
probe=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(v)]).stdout)
r=run(['ffmpeg','-v','error','-threads','2','-i',str(v),'-f','null','-']);assert not r.stderr.strip(),r.stderr
l=run(['ffmpeg','-hide_banner','-nostats','-threads','2','-i',str(v),'-vn','-af','loudnorm=I=-19:TP=-3:LRA=8:print_format=json','-f','null','-']).stderr;l=json.loads(l[l.rfind('{'):l.rfind('}')+1])
times=[2,5.1,7,10,14,18,22,27,31,33,34.5,35.5];sheet=Image.new('RGB',(1280,810),(9,17,24));d=ImageDraw.Draw(sheet)
for i,t in enumerate(times):
 f=P/'qa'/f'encoded-{t:g}.jpg';run(['ffmpeg','-v','error','-threads','2','-i',str(v),'-ss',str(t),'-frames:v','1','-q:v','2','-y',str(f)])
 im=Image.open(f);im.thumbnail((320,180));x=i%4*320;y=i//4*270;sheet.paste(im,(x,y));d.text((x+12,y+187),f'{t:g} seconds',fill='white')
sheet.save(P/'qa/encoded-contact.jpg',quality=93)
video=next(s for s in probe['streams'] if s['codec_type']=='video');audio=next(s for s in probe['streams'] if s['codec_type']=='audio')
report={'file':v.name,'bytes':v.stat().st_size,'sha256':hashlib.sha256(v.read_bytes()).hexdigest(),'duration':probe['format']['duration'],'resolution':[video['width'],video['height']],'frame_rate':video['avg_frame_rate'],'audio_channels':audio['channels'],'full_decode':'passed','sound':l,'actual_frame_times':times,'acceptance':'pending_user_feedback','subjective_listening':'not claimed; technical audio analysis only'}
assert float(report['duration'])==36.0;assert report['resolution']==[1280,720];assert audio['channels']==2;assert v.stat().st_size<18000000
(P/'qa/technical-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
