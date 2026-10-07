#!/usr/bin/env python3
"""Audit an art study; build a local, source-linked review without judging aesthetics."""
import argparse, hashlib, html, json, math, subprocess, sys
from pathlib import Path
from urllib.parse import quote, urlparse

def digest(p):
    with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()

def load_study(path):
    spec=json.loads(path.read_text()); root=path.parent.resolve()
    def local(value):
        p=(root/value).resolve()
        if not p.is_relative_to(root): raise ValueError('Path escapes episode: '+value)
        if not p.is_file(): raise ValueError('Missing file: '+value)
        return p
    if spec.get('acceptance') not in ['pending_user_feedback','rejected_by_user','accepted_by_user']:
        raise ValueError('Explicit acceptance state required')
    duration=spec['duration']; fps=spec['fps']
    if not isinstance(duration,(int,float)) or not math.isfinite(duration) or duration<=0: raise ValueError('Invalid duration')
    if not isinstance(fps,(int,float)) or not math.isfinite(fps) or fps<=0: raise ValueError('Invalid fps')
    media=local(spec['media']); source=local(spec['source_manifest']); local(spec['renderer'])
    provenance=json.loads(source.read_text()); assets={}
    for a in provenance['assets']:
        for key in ['file','artist','title','date','accession','credit_line','museum_api','rights','sha256','bytes']:
            if not a.get(key): raise ValueError('Missing provenance field: '+key)
        if urlparse(a['museum_api']).scheme!='https' or not urlparse(a['museum_api']).netloc: raise ValueError('Invalid museum source URL')
        p=(source.parent/a['file']).resolve()
        if not p.is_relative_to(root): raise ValueError('Asset path escapes episode')
        if p.stat().st_size!=a['bytes'] or digest(p)!=a['sha256']: raise ValueError('Asset integrity mismatch: '+a['file'])
        assets[a['file']]=a
    cursor=0
    for shot in spec['shots']:
        start,end=shot['start'],shot['end']
        if not all(isinstance(n,(int,float)) and math.isfinite(n) for n in [start,end]): raise ValueError('Invalid shot time')
        if abs(start-cursor)>1e-6 or end<=start: raise ValueError('Timeline gap, overlap or reversed interval')
        if shot['kind'] not in ['source','detail','interpretation','transition']: raise ValueError('Unknown image status')
        if shot['kind']!='transition' and shot.get('asset') not in assets: raise ValueError('Unlinked image source')
        if not shot.get('title_zh') or not shot.get('title_en'): raise ValueError('Bilingual shot labels required')
        cursor=end
    if abs(cursor-duration)>1e-6: raise ValueError('Timeline duration mismatch')
    return spec,media,assets

def run(args):
    return subprocess.run(args,check=True,capture_output=True,text=True)

def build(path,out):
    spec,media,assets=load_study(path)
    probe=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(media)]).stdout)
    streams=probe['streams']; video=next(s for s in streams if s['codec_type']=='video'); audio=next((s for s in streams if s['codec_type']=='audio'),None)
    if not audio: raise ValueError('Missing audio stream')
    num,den=map(float,video['avg_frame_rate'].split('/')); fps=num/den
    duration=float(probe['format']['duration'])
    if abs(duration-spec['duration'])>1/spec['fps'] or abs(fps-spec['fps'])>.01: raise ValueError('Encoded timing differs from storyboard')
    decode=run(['ffmpeg','-v','error','-threads','2','-i',str(media),'-f','null','-'])
    if decode.stderr.strip(): raise ValueError('Decoder reported errors: '+decode.stderr)
    loud=run(['ffmpeg','-hide_banner','-nostats','-threads','2','-i',str(media),'-vn','-af','loudnorm=I=-19:TP=-3:LRA=9:print_format=json','-f','null','-']).stderr
    loud=json.loads(loud[loud.rfind('{'):loud.rfind('}')+1])
    out.mkdir(parents=True,exist_ok=True)
    frames=[]
    for i,shot in enumerate(spec['shots']):
        t=(shot['start']+shot['end'])/2; filename=f'shot-{i+1:02}.jpg'
        run(['ffmpeg','-v','error','-threads','2','-i',str(media),'-ss',str(t),'-frames:v','1','-vf','scale=640:-1','-y',str(out/filename)])
        frames.append({'time':t,'file':filename})
    report={'schema_version':1,'episode':spec['episode'],'acceptance':spec['acceptance'],'technical_checks':{'source_integrity':'passed','timeline':'passed','full_decode':'passed'},'media':{'sha256':digest(media),'bytes':media.stat().st_size,'duration':duration,'width':video['width'],'height':video['height'],'fps':fps},'sound':{'integrated_lufs':float(loud['input_i']),'true_peak_dbfs':float(loud['input_tp']),'loudness_range_lu':float(loud['input_lra'])},'frames':frames,'aesthetic_acceptance':'NOT determined by this tool','human_listening':'not performed by this tool'}
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    import os
    link=lambda p:quote(os.path.relpath(p,out),safe='/')
    esc=html.escape
    cards=''
    for s,f in zip(spec['shots'],frames):
        a=assets.get(s.get('asset')); attribution=(f"{a['artist']} · {a['title']} ({a['date']}) · {a['accession']}" if a else '跨画面转场 / Transition')
        source=(f'<a href="{esc(a["museum_api"],quote=True)}">博物馆记录</a>' if a else '')
        cards+=f'<article><button data-time="{f["time"]}" aria-label="跳至 {f["time"]} 秒"><img src="{f["file"]}" alt="{esc(s["title_zh"])}实际编码画面"></button><p>{s["start"]:g}–{s["end"]:g}s · {esc(s["kind"])}</p><h2>{esc(s["title_zh"])}</h2><p>{esc(s["title_en"])}</p><small>{esc(attribution)} {source}</small></article>'
    prompts=''.join('<li>'+esc(p)+'</li>' for p in spec['review_prompts'])
    state={'pending_user_feedback':'待观看反馈，未获认可','rejected_by_user':'用户已否定','accepted_by_user':'已有用户认可记录'}[spec['acceptance']]
    page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>艺术样段审查</title><style>body{margin:auto;max-width:1180px;padding:32px;background:#101c22;color:#e5e6db;font:16px/1.65 system-ui}h1{font-weight:450}p,small{color:#b9c8c8}a{color:#b4d8df}video{width:100%;max-height:70vh;background:#080f13}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:24px}article{border-top:1px solid #45565a;padding-top:16px}button{border:0;padding:0;background:transparent;cursor:pointer;width:100%}button:focus-visible{outline:3px solid #ffe2a1}img{width:100%;display:block}h2{font-size:20px}header,section{margin-bottom:36px}textarea{box-sizing:border-box;width:100%;min-height:130px;padding:14px;background:#182b32;color:white;border:1px solid #67828b;font:inherit}.action{width:auto;padding:10px 16px;background:#cce0d8;color:#12252b;margin:10px 8px 0 0}</style>'''
    page+=f'<header><p>制作审查 / PRODUCTION REVIEW · {esc(state)}</p><h1>{esc(spec["title"])}</h1><p>{esc(spec["artistic_seed"])}</p></header><video id="film" controls preload="metadata" src="{link(media)}"></video><p>点击画面跳至对应时刻。技术检查通过不代表艺术质量获认可。</p><section class="grid">{cards}</section><section><h2>观看与听审</h2><ul>{prompts}</ul><p>音量：{report["sound"]["integrated_lufs"]} LUFS；真峰值：{report["sound"]["true_peak_dbfs"]} dBFS。指标不替代实际聆听。</p><label for="notes">观看笔记（仅本浏览器保存）</label><textarea id="notes"></textarea><button class="action" id="save">保存笔记</button><button class="action" id="export">导出笔记</button><p id="notice" role="status"></p></section><a href="report.json">机器检查报告</a> · <a href="{link(path)}">镜头与来源配置</a>'
    page+='''<script>const film=document.querySelector('#film'),notes=document.querySelector('#notes'),notice=document.querySelector('#notice');const key='art-review-'+'''+json.dumps(spec['episode']).replace('<', '\\u003c')+''';try{notes.value=localStorage.getItem(key)||''}catch(e){notice.textContent='本浏览器存储不可用，可导出笔记'}document.querySelectorAll('[data-time]').forEach(b=>b.onclick=()=>{film.currentTime=Number(b.dataset.time);film.scrollIntoView({behavior:'smooth',block:'center'})});document.querySelector('#save').onclick=()=>{try{localStorage.setItem(key,notes.value);notice.textContent='已保存在本浏览器'}catch(e){notice.textContent='保存失败，请导出笔记'}};document.querySelector('#export').onclick=()=>{const url=URL.createObjectURL(new Blob([JSON.stringify({episode:'''+json.dumps(spec['episode']).replace('<', '\\u003c')+''',time:film.currentTime,notes:notes.value,acceptance:'unclassified_notes'},null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='art-review-notes.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};</script></html>'''
    (out/'index.html').write_text(page)
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('study',type=Path);parser.add_argument('--output',type=Path);parser.add_argument('--validate-only',action='store_true');args=parser.parse_args()
    try:
        if args.validate_only: load_study(args.study);print('Source integrity and timeline passed')
        else:
            if not args.output: parser.error('--output is required for review generation')
            print(json.dumps(build(args.study.resolve(),args.output.resolve()),ensure_ascii=False,indent=2))
    except (ValueError,KeyError,OSError,subprocess.CalledProcessError) as e:
        print('Review failed: '+str(e),file=sys.stderr);sys.exit(1)
