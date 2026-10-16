"""Offline retrieval, provenance, and safe caching checks for the prompt library."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/creating-videos/scripts/reference_library.py'
spec = importlib.util.spec_from_file_location('reference_library', SCRIPT)
library = importlib.util.module_from_spec(spec); spec.loader.exec_module(library)


def entry(ident='demo-01', **changes):
    row = dict(slug=ident, author='Example creator', category='motion', tech_tags=['svg'],
               prompt='Reveal type through a mask and morph the outline.', prompt_partial=False,
               post_url='https://example.com/original', skillry_url=None)
    row.update(changes)
    return row


def cache(rows):
    raw = json.dumps(rows, ensure_ascii=False).encode('utf-8')
    return library.make_cache(raw, 'MIT fixture notice', library.DEFAULT_REF, 'local fixture')


class ReferenceLibraryChecks(unittest.TestCase):
    def test_source_hash_license_and_unicode_survive_cache_roundtrip(self):
        rows = [entry(prompt='A shape reveals 你好 and transforms into a path.')]
        raw = json.dumps(rows, ensure_ascii=False).encode('utf-8')
        result = library.make_cache(raw, 'MIT fixture notice', library.DEFAULT_REF, 'fixture')
        self.assertEqual(result['source_sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual(result['license_text'], 'MIT fixture notice')
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'cache.json'; p.write_text(json.dumps(result,ensure_ascii=False),encoding='utf-8')
            self.assertEqual(library.load_cache(p)['entries'][0]['prompt'],rows[0]['prompt'])

    def test_query_coverage_wins_over_a_single_word_title(self):
        data=cache([entry('one',title='UI UI UI',prompt='UI only.'),entry('three',title='Study',prompt='UI mask morph')])
        result=library.search(data,'UI mask morph')
        self.assertEqual(result['matches'][0]['id'],'three')
        self.assertEqual(result['matches'][0]['matched_term_count'],3)
        self.assertNotIn('prompt',result['matches'][0])

    def test_identical_prompt_text_is_deduplicated(self):
        data=cache([entry('one'),entry('two',prompt='  REVEAL type through a mask and morph the outline.  ')])
        self.assertEqual(len(library.search(data,'mask morph')['matches']),1)

    def test_full_only_and_category_filters_do_not_invent_missing_results(self):
        data=cache([entry('partial',prompt_partial=True),entry('game',category='interactive'),entry('full')])
        result=library.search(data,'mask',category='motion',full_only=True)
        self.assertEqual([row['id'] for row in result['matches']],['full'])
        self.assertEqual(library.search(data,'nonexistentconcept')['matches'],[])

    def test_missing_completeness_metadata_stays_uncertain(self):
        row=entry(); del row['prompt_partial']
        self.assertTrue(library.normalize([row])[0]['prompt_partial'])

    def test_unsafe_duplicate_ids_and_non_http_source_links_are_rejected(self):
        for rows in ([entry('../escape')],[entry(),entry()],[entry(post_url='javascript:alert(1)')]):
            with self.subTest(rows=rows), self.assertRaises(ValueError): library.normalize(rows)
        with self.assertRaises(ValueError): library.source_url('../main','data/videos.json')

    def test_dependency_and_context_flags_are_preserved_for_review(self):
        row=library.normalize([entry(category='interactive',prompt='Use the attached image, Remotion, Motion+ and Suno.',prompt_partial=True)])[0]
        flags=library.flags(row)
        self.assertIn('partial_prompt_or_description',flags)
        self.assertIn('interactive_state_needs_time_based_adaptation',flags)
        self.assertTrue(any('premium' in flag for flag in flags))
        self.assertTrue(any('remotion' in flag for flag in flags))
        self.assertTrue(any('assets' in flag for flag in flags))

    def test_cli_import_show_and_cache_overwrite_protection(self):
        with tempfile.TemporaryDirectory(prefix='reference library ') as tmp:
            folder=Path(tmp); source=folder/'source.json'; license_file=folder/'LICENSE'; target=folder/'cache.json'
            source.write_text(json.dumps([entry(prompt='A clear 你好 prompt')],ensure_ascii=False),encoding='utf-8')
            license_file.write_text('MIT fixture notice',encoding='utf-8')
            def run(*args): return subprocess.run([sys.executable,str(SCRIPT),*args],capture_output=True,text=True,cwd=tmp)
            imported=run('import','--cache',str(target),'--source',str(source),'--license-file',str(license_file))
            self.assertEqual(imported.returncode,0,imported.stderr)
            shown=run('show','--cache',str(target),'--id','demo-01')
            self.assertEqual(json.loads(shown.stdout)['prompt'],'A clear 你好 prompt')
            before=target.read_bytes()
            blocked=run('search','--cache',str(target),'--query','clear','--output',str(target))
            self.assertNotEqual(blocked.returncode,0)
            self.assertEqual(target.read_bytes(),before)


if __name__ == '__main__':
    unittest.main()
