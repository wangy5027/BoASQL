import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest


SOURCE_ROOT = Path(__file__).resolve().parents[1]


class RelocatedProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="boa paths ")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "renamed project with spaces"
        shutil.copytree(
            SOURCE_ROOT, self.root,
            ignore=shutil.ignore_patterns(".git", "__pycache__", ".venv", "spider", "test_suite_database"),
        )
        self.cwd = self.base / "unrelated working directory"
        self.cwd.mkdir()

    def run_code(self, code):
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
        result = subprocess.run(
            [sys.executable, "-c", textwrap.dedent(code), str(self.root)],
            cwd=self.cwd, env=env, capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def test_data_output_and_initializer_paths(self):
        self.run_code('''
            from pathlib import Path
            import json, sys
            root = Path(sys.argv[1])
            sys.path.insert(0, str(root))
            from Tree_Running.Tools import test_file_related as io
            from Tree_Running.paths import PROJECT_ROOT
            assert PROJECT_ROOT == root.resolve(), (PROJECT_ROOT, root)
            db = root / 'spider' / 'test_database' / 'sample'
            db.mkdir(parents=True)
            (root / 'spider' / 'dev.json').write_text('[{"db_id": "sample"}]')
            schema = 'CREATE TABLE "sample" ("id" INTEGER, PRIMARY KEY ("id"));'
            (db / 'schema.sql').write_text(schema)
            assert io.get_test_queries_data() == [{'db_id': 'sample'}]
            assert 'CREATE TABLE' in io.get_sql_schema('sample')
            assert io.change_kg('sample')
            for rel in ['DB-KG-Initialization', 'Tree_Running/Agents/Tools',
                        'Tree_Running/Tree_Building/Agents/Tools']:
                assert 'sample' in (root / rel / 'Database_kg.txt').read_text()
                assert 'sample' in (root / rel / 'CREATE_TABLE_MESSAGE.txt').read_text()
            io.write_gold_txt_file('SELECT 1', 'sample')
            io.write_predict_txt_file('SELECT 1')
            io.write_question_txt_file(0, 'example')
            assert (root / 'DEV_gold.txt').read_text() == 'SELECT 1\\tsample\\n'
            assert (root / 'DEV_predict.txt').exists()
            assert (root / 'DEV_question.txt').exists()
            assert not (Path.cwd() / 'DEV_gold.txt').exists()
        ''')

    def test_both_database_helpers_open_sqlite_not_schema(self):
        self.run_code('''
            from pathlib import Path
            import importlib, sqlite3, sys, types
            root = Path(sys.argv[1]); sys.path.insert(0, str(root))
            pandas = types.ModuleType('pandas')
            pandas.DataFrame = lambda rows, columns: (rows, columns)
            sys.modules['pandas'] = pandas
            folder = root / 'spider' / 'test_database' / 'sample'
            folder.mkdir(parents=True)
            with sqlite3.connect(folder / 'sample.sqlite') as conn:
                conn.execute('CREATE TABLE sample (id INTEGER)')
                conn.execute('INSERT INTO sample VALUES (7)')
            (folder / 'schema.sql').write_text('This is not a SQLite database.')
            for name in ['Tree_Running.Agents.Tools.KG_DB_foundamental_functions',
                         'Tree_Running.Tree_Building.Agents.Tools.KG_DB_foundamental_functions']:
                module = importlib.import_module(name)
                assert module.get_data_from_database('sample', 'SELECT id FROM sample') == ([(7,)], ['id'])
        ''')

    def test_corrected_evaluators_write_separate_difficulty_directories(self):
        self.run_code('''
            from pathlib import Path
            import csv, runpy, sqlite3, sys, types
            root = Path(sys.argv[1])
            class Frame:
                def __init__(self, rows, columns): self.rows, self.columns = rows, columns
                def to_csv(self, path, index=False):
                    with open(path, 'w', newline='') as f:
                        writer = csv.writer(f); writer.writerow(self.columns); writer.writerows(self.rows)
            pandas = types.ModuleType('pandas'); pandas.DataFrame = Frame
            sys.modules['pandas'] = pandas
            timeout = types.ModuleType('func_timeout'); timeout.func_set_timeout = lambda *a: (lambda f: f)
            sys.modules['func_timeout'] = timeout
            parser = types.ModuleType('process_sql')
            parser.get_schema = lambda path: {}; parser.Schema = lambda value: value
            parser.get_sql = lambda *a: {}
            sys.modules['process_sql'] = parser
            sys.modules['chardet'] = types.ModuleType('chardet')
            table = types.ModuleType('tabulate'); table.tabulate = lambda *a, **k: ''
            sys.modules['tabulate'] = table
            folder = root / 'spider' / 'test_database' / 'sample'; folder.mkdir(parents=True)
            with sqlite3.connect(folder / 'sample.sqlite') as conn:
                conn.execute('CREATE TABLE sample (id INTEGER)')
                conn.execute('INSERT INTO sample VALUES (7)')
            gold = root / 'gold.txt'; pred = root / 'pred.txt'
            gold.write_text('SELECT id FROM sample\\tsample\\n' * 2)
            pred.write_text('SELECT id FROM sample\\nSELECT missing FROM sample\\n')
            for name in ['evaluation', 'correctified_evaluation']:
                ns = runpy.run_path(str(root / 'correctified_official_evaluation' / (name + '.py')))
                fn = ns['obtain_predict_csv']; fn.__globals__['eval_hardness'] = lambda sql: 'easy'
                if name == 'evaluation': fn(str(gold), str(pred), name)
                else: fn(str(pred), str(gold), name)
                outputs = root / 'correctified_official_evaluation' / (name + '_predict_ouput') / 'easy'
                assert (outputs / '0_easy_target_output.csv').exists()
                assert (outputs / '1_easy_txt_output.txt').exists()
                assert not (Path.cwd() / (name + '_predict_ouput')).exists()
        ''')

    def test_single_question_entry_help_from_other_directory(self):
        self.run_code('''
            from pathlib import Path
            import subprocess, sys
            root = Path(sys.argv[1])
            result = subprocess.run([sys.executable, str(root / 'Tree_Running' / 'Run.py'), '--help'],
                                    capture_output=True, text=True)
            assert result.returncode == 0, result.stderr
            assert '--db-id' in result.stdout
        ''')

    def test_batch_entry_and_log_paths_after_rename(self):
        self.run_code('''
            from pathlib import Path
            import importlib, os, runpy, sys, types
            root = Path(sys.argv[1]); sys.path.insert(0, str(root))
            pandas = types.ModuleType('pandas'); pandas.DataFrame = object
            sys.modules['pandas'] = pandas
            trees = types.ModuleType('treelib'); trees.Tree = object; trees.Node = object
            sys.modules['treelib'] = trees
            client = types.ModuleType('openai'); client.OpenAI = object
            sys.modules['openai'] = client
            os.environ['OPENAI_API_KEY'] = 'unused-test-value'
            ns = runpy.run_path(str(root / 'Run.py'))
            assert Path(ns['printlog_path']) == root.resolve() / 'printlog.txt'
            main = ns['main']; main.__globals__['get_test_queries_data'] = lambda: []
            main()
            for name in ['Tree_Running.Task_Tree_Running',
                         'Tree_Running.Tree_Building.Task_Tree_Building',
                         'Tree_Running.Agents.Code_generation',
                         'Tree_Running.Agents.Code_checking',
                         'Tree_Running.Agents.Bug_fixing']:
                module = importlib.import_module(name)
                assert Path(module.printlog_path) == root.resolve() / 'printlog.txt'
        ''')


if __name__ == "__main__":
    unittest.main()
