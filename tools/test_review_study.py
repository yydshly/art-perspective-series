"""Failure cases protect audit trust: gaps, false provenance, unsafe paths, no acceptance."""
import copy,json,tempfile,unittest
from pathlib import Path
from review_study import load_study
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'episodes/003-within-the-surface/study.json'
class AuditTests(unittest.TestCase):
 def test_asset_tampering(self):
  source=PATH.parent/'production/assets/SOURCES.json'
  data=json.loads(source.read_text());data['assets'][0]['sha256']='0'*64
  with tempfile.NamedTemporaryFile(mode='w',suffix='.json',dir=source.parent,delete=False) as f:
   json.dump(data,f);p=Path(f.name)
  try:self.check_bad(lambda d:d.update(source_manifest=str(p.relative_to(PATH.parent))),'integrity mismatch')
  finally:p.unlink()
 def test_real_study(self):
  spec,_,assets=load_study(PATH);self.assertEqual(len(assets),2);self.assertEqual(spec['acceptance'],'pending_user_feedback')
 def check_bad(self,change,pattern):
  data=json.loads(PATH.read_text());change(data)
  # A temporary config beside the real inputs exercises paths without copying media.
  with tempfile.NamedTemporaryFile(mode='w',suffix='.json',dir=PATH.parent,delete=False) as f:
   json.dump(data,f);p=Path(f.name)
  try:
   with self.assertRaisesRegex(ValueError,pattern):load_study(p)
  finally:p.unlink()
 def test_gap(self):self.check_bad(lambda d:d['shots'][1].update(start=7.1),'gap')
 def test_overlap(self):self.check_bad(lambda d:d['shots'][1].update(start=6.9),'overlap')
 def test_unlinked_source(self):self.check_bad(lambda d:d['shots'][0].update(asset='invented.jpg'),'Unlinked')
 def test_escape(self):self.check_bad(lambda d:d.update(media='../../README.md'),'escapes')
 def test_acceptance(self):self.check_bad(lambda d:d.update(acceptance='probably_good'),'acceptance')
 def test_nan(self):self.check_bad(lambda d:d['shots'][0].update(end=float('nan')),'Invalid shot')
 def test_end_mismatch(self):self.check_bad(lambda d:d['shots'][-1].update(end=37),'duration mismatch')
 def test_missing_bilingual(self):self.check_bad(lambda d:d['shots'][0].update(title_en=''),'Bilingual')
if __name__=='__main__':unittest.main()
