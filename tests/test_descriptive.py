"""Check scientific input invariants and the two new runnable synthetic examples."""
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'examples' / name / 'plot.py')
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


class DescriptiveInputs(unittest.TestCase):
    def check_rejects(self, name, record):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'data.json'
            path.write_text(json.dumps(record))
            with self.assertRaises(ValueError):
                module(name).load_data(path)

    def test_zero_denominator_rejected(self):
        self.check_rejects('paired', {'series': [{'id': 'x', 'label': 'X', 'n': 0, 'fp': 0, 'pf': 0}]})

    def test_disjoint_transition_counts(self):
        self.check_rejects('paired', {'series': [{'id': 'x', 'label': 'X', 'n': 10, 'fp': 8, 'pf': 3}]})

    def test_matrix_shape(self):
        self.check_rejects('matrix', {'rows': ['A'], 'columns': ['X', 'Y'], 'values': [[1]]})

    def test_missing_not_zero(self):
        plot = module('matrix')
        data = plot.load_data(ROOT / 'examples/matrix/data.json')
        self.assertIsNone(data['values'][1][1])
        fig = plot.render(data, {'vmin': -40, 'vmax': 40, 'center': 0})
        self.assertTrue(fig.axes[0].images[0].get_array().mask[1, 1])
        plot.plt.close(fig)

    def test_scale_cannot_clip_data(self):
        plot = module('matrix')
        with self.assertRaises(ValueError):
            plot.render({'rows': ['A'], 'columns': ['X'], 'values': [[50]]}, {'vmin': 0, 'vmax': 40})
        plot.plt.close('all')

    def test_synthetic_exports(self):
        import sys
        for name, stem in [('paired', 'paired-transitions'), ('matrix', 'annotated-matrix')]:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as d:
                result = subprocess.run([sys.executable, str(ROOT / 'examples' / name / 'plot.py'),
                                         '--output-dir', d], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                for ext in ('pdf', 'png', 'render.json'):
                    self.assertGreater((Path(d) / f'{stem}.{ext}').stat().st_size, 100)
                self.assertTrue((Path(d) / f'{stem}.pdf').read_bytes().startswith(b'%PDF'))


if __name__ == '__main__':
    unittest.main()
