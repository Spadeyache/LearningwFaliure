"""Check isolation, legacy compatibility and readable combined sheets."""
import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
from robot_adaptation.analysis.plots import plot
from robot_adaptation.analysis.plots.combine_plots import combine


class DensePlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / 'runs/failure_collection/dense_single_pair_fixed40g/manifest.json').read_text())
        cls.conditions = {f'C{i:02d}': c for i, c in enumerate(cls.manifest['conditions'], 1)}
        cls.rows = [dict(condition=k) for k in cls.conditions]

    def test_every_collected_condition_has_an_isolated_plot(self):
        _, requests = plot.read_requests(ROOT / 'robot_adaptation/analysis/plots/plots_dense.md')
        self.assertEqual(len(requests), 307)
        covered = set()
        for request in requests:
            selected, nominal = plot.select(request, self.conditions, self.rows)
            self.assertEqual(nominal, 1)
            self.assertLessEqual(len(request['variables']), 2)
            covered.update(r['condition'] for r in selected)
        self.assertEqual(covered, set(self.conditions))

    def test_pair_cannot_be_hidden_in_single_variable_plot(self):
        cid = next(k for k, c in self.conditions.items() if set(c['changed_factors']) == {'mass', 'object_friction'})
        request = dict(name='bad', variables=['object_friction'], conditions=[cid], reference=True)
        with self.assertRaisesRegex(ValueError, 'unlisted variables'):
            plot.select(request, self.conditions, self.rows)

    def test_legacy_markdown_still_parses(self):
        _, requests = plot.read_requests(ROOT / 'robot_adaptation/analysis/plots/plots.md')
        self.assertEqual(len(requests), 46)
        self.assertIn('com_only', [r['name'] for r in requests])

    def test_long_condition_ids_and_ranges(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / 'plan.md'
            p.write_text('## Plots\n\n| Plot | Variables | Conditions | Reference | Title |\n'
                         '| --- | --- | --- | --- | --- |\n| test | mass | C2981-C2983 | yes | Test |\n')
            _, requests = plot.read_requests(p)
            self.assertEqual(requests[0]['conditions'], ['C2981', 'C2982', 'C2983'])


class CombinedViewTests(unittest.TestCase):
    def test_large_plan_keeps_every_tile_in_one_viewer(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)
            Image.new('RGB', (50, 50), 'white').save(p / 'example.png')
            rows = [dict(name=f'plot{i}', title=f'Plot {i}', file='example.png') for i in range(307)]
            (p / 'selections.json').write_text(json.dumps(rows))
            result = combine(p, tile_width=300)
            layout = json.loads((p / 'combined_layout.json').read_text())
            self.assertEqual(sum(len(page['tiles']) for page in layout['pages']), 307)
            self.assertGreater(result['sheets'], 1)
            self.assertTrue(all(page['height'] <= 24000 for page in layout['pages']))
            for page in layout['pages']:
                with Image.open(p / page['file']) as image:
                    self.assertEqual(image.size, (page['width'], page['height']))
            self.assertTrue((p / 'combined.html').exists())

    def test_small_plan_retains_one_combined_png(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)
            Image.new('RGB', (50, 50), 'white').save(p / 'example.png')
            (p / 'selections.json').write_text(json.dumps([dict(name='mass_only', title='Mass', file='example.png')]))
            result = combine(p, tile_width=300)
            self.assertEqual(result['file'], 'combined.png')
            self.assertTrue((p / 'combined.png').exists())


if __name__ == '__main__':
    unittest.main()
