"""Check external-data usage and invalid-input handling through the real CLI."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'examples/line/plot.py'


class LineChartTests(unittest.TestCase):
    def controlled_inputs(self):
        data = {
            'conditions': ['A', 'B'],
            'series': [
                {'id': 'first', 'label': 'Example low', 'model': 'Example',
                 'effort': 'low', 'n': 10, 'passes': [2, 4]},
                {'id': 'latest', 'label': 'Example medium', 'model': 'Example',
                 'effort': 'medium', 'n': 10, 'passes': [6, 8]},
            ],
        }
        layout = {
            'encoding': {'color_by': 'model', 'colors': {'Example': '#4477AA'},
                         'marker_by': 'effort', 'markers': {'low': 'o', 'medium': 's'},
                         'linestyle': '-'},
            'legend_order': ['latest', 'first'],
            'annotations': {key: [{'xytext': [0, 7]}, {'xytext': [0, 7]}]
                            for key in ['first', 'latest']},
            'check_annotations': True,
        }
        return data, layout

    def test_semantic_styles_and_id_layout_survive_input_reordering(self):
        data, layout = self.controlled_inputs()
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            source, settings = work / 'input.json', work / 'layout.json'
            settings.write_text(json.dumps(layout))
            images = []
            for index in range(2):
                source.write_text(json.dumps(data))
                output = work / str(index)
                result = subprocess.run(
                    [sys.executable, str(SCRIPT), '--data', str(source),
                     '--layout', str(settings), '--output-dir', str(output)],
                    capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                rendered = json.loads((output / 'line-comparison.render.json').read_text())
                self.assertEqual(rendered['legend_order'], ['latest', 'first'])
                styles = {row['id']: row for row in rendered['series']}
                self.assertEqual(styles['first']['color'], styles['latest']['color'])
                self.assertEqual(styles['first']['marker'], 'o')
                self.assertEqual(styles['latest']['marker'], 's')
                self.assertTrue(all(row['linestyle'] == '-' for row in styles.values()))
                images.append((output / 'line-comparison.png').read_bytes())
                data['series'].reverse()
            self.assertEqual(images[0], images[1])

    def test_unapproved_styles_or_incomplete_order_are_rejected_before_writing(self):
        for problem in ['unknown_model', 'override', 'missing_order', 'duplicate_id', 'overlap']:
            with self.subTest(problem=problem), tempfile.TemporaryDirectory() as directory:
                data, layout = self.controlled_inputs()
                if problem == 'unknown_model':
                    data['series'][1]['model'] = 'Unconfigured'
                elif problem == 'override':
                    data['series'][1]['linestyle'] = '--'
                elif problem == 'missing_order':
                    layout['legend_order'] = ['latest']
                elif problem == 'duplicate_id':
                    data['series'][1]['id'] = 'first'
                else:
                    data['series'][1]['passes'] = [2, 4]
                work = Path(directory)
                source, settings = work / 'input.json', work / 'layout.json'
                source.write_text(json.dumps(data))
                settings.write_text(json.dumps(layout))
                result = subprocess.run(
                    [sys.executable, str(SCRIPT), '--data', str(source),
                     '--layout', str(settings), '--output-dir', str(work / 'figures')],
                    capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertFalse((work / 'figures').exists())

    def test_external_layout_controls_output_without_external_python(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            source, layout = work / 'input.json', work / 'layout.json'
            source.write_text(json.dumps({
                'conditions': ['A', 'B'],
                'series': [{'label': 'Example', 'n': 10, 'passes': [4, 8]}],
            }))
            layout.write_text(json.dumps({
                'y_min': .2, 'output_name': 'configured',
                'annotations': [[{'xytext': [0, 7]},
                                 {'xytext': [1, .9], 'textcoords': 'data'}]],
            }))
            result = subprocess.run(
                [sys.executable, str(SCRIPT), '--data', str(source),
                 '--layout', str(layout), '--output-dir', str(work / 'figures')],
                cwd=work, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((work / 'figures/configured.pdf').is_file())
            self.assertTrue((work / 'figures/configured.png').is_file())
            self.assertEqual(sorted(p.name for p in work.iterdir()),
                             ['figures', 'input.json', 'layout.json'])

    def test_mismatched_layout_is_rejected_before_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            layout = work / 'layout.json'
            layout.write_text(json.dumps({'annotations': []}))
            result = subprocess.run(
                [sys.executable, str(SCRIPT), '--layout', str(layout),
                 '--output-dir', str(work / 'figures')],
                cwd=work, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn('one row per data series', result.stderr)
            self.assertFalse((work / 'figures').exists())

    def test_external_data_and_variable_shape_from_another_working_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            data = {
                'conditions': ['A', 'B', 'C', 'D'],
                'series': [
                    {'label': 'Example one', 'n': 10, 'passes': [0, 3, 6, 10]},
                    {'label': 'Example two', 'n': 20, 'passes': [4, 8, 12, 16]},
                ],
            }
            source = work / 'input.json'
            source.write_text(json.dumps(data), encoding='utf-8')
            result = subprocess.run(
                [sys.executable, str(SCRIPT), '--data', str(source),
                 '--output-dir', str(work / 'figures')],
                cwd=work, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((work / 'figures/line-comparison.pdf').read_bytes().startswith(b'%PDF-'))
            self.assertTrue((work / 'figures/line-comparison.png').read_bytes().startswith(b'\x89PNG'))
            self.assertEqual(json.loads(source.read_text()), data)

    def test_invalid_counts_or_hidden_points_do_not_write_outputs(self):
        for counts, y_min in [([11, 5], '0'), ([True, 5], '0'), ([2], '0'),
                              ([2, 5], '0.3'), ([2, 5], 'nan')]:
            with self.subTest(counts=counts, y_min=y_min), tempfile.TemporaryDirectory() as directory:
                work = Path(directory)
                source = work / 'input.json'
                source.write_text(json.dumps({
                    'conditions': ['A', 'B'],
                    'series': [{'label': 'Example', 'n': 10, 'passes': counts}],
                }))
                result = subprocess.run(
                    [sys.executable, str(SCRIPT), '--data', str(source),
                     '--output-dir', str(work / 'figures'), '--y-min', y_min],
                    cwd=work, capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn('error:', result.stderr)
                self.assertFalse((work / 'figures').exists())


if __name__ == '__main__':
    unittest.main()
