import requests,json,pathlib
p=pathlib.Path(__file__).parent/'assets'; records=[]
for key,oid in [('retreat',39550),('melencolia',360018),('wave',45434),('sideshow',437654)]:
 d=requests.get(f'https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}',timeout=40).json();print(key,d.get('title'),d.get('isPublicDomain'),d.get('primaryImage'))
 if not d.get('isPublicDomain'): continue
 (p/(key+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2))
 r=requests.get(d['primaryImage'],timeout=60);r.raise_for_status();(p/(key+'.jpg')).write_bytes(r.content);records.append({'key':key,'id':oid,'title':d['title'],'date':d['objectDate'],'artist':d['artistDisplayName'],'url':d['objectURL'],'image':d['primaryImage'],'rights':'Public domain; The Met Open Access (CC0)','credit':d['creditLine']})
(p/'sources.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
