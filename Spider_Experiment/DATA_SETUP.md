# Spider 数据下载与评测数据准备

本目录仅包含 BoA-SQL 的 Agent 部分，不包含强化学习训练代码。Spider 数据集、数据库副本和逐题实验中间输出已从工作目录移除；运行前请按下文自行下载数据。

## 1. 下载 Spider 1.0

- [Spider 1.0 官方主页](https://yale-lily.github.io/spider)：进入 Getting Started，点击 Spider Dataset。
- [官方主页当前提供的 spider_data.zip 下载链接](https://drive.google.com/file/d/1403EGqzIDoHMdQF4c9Bkyl7dZLZ5Wt6J/view?usp=sharing)。若链接发生变化，以官方主页为准。
- [官方代码与数据格式说明](https://github.com/taoyds/spider)。

本项目使用 Spider 1.0，不是 Spider 2.0。下载后保留数据发布版本及来源说明，遵守官方的数据使用与引用要求。这里核对了官方链接，未重新下载压缩包，也未验证重新下载的数据与历史实验副本逐字节一致。

清理前，`spider/dev.json` 有 1,034 道开发集题目；另一个 `spider/test_data/dev.json` 有 2,147 道题目。当前根目录 `Run.py` 读取前者，不要将两个文件互相覆盖或混用。

## 2. Agent 与修正版评测使用的路径

以包含 `Run.py` 的目录为项目根目录（下图以当前名称 `Spider_Experiment` 为例，可重命名），整理为：

```text
Spider_Experiment/
├── Run.py
└── spider/
    ├── dev.json
    ├── tables.json
    └── test_database/
        └── <db_id>/
            ├── <db_id>.sqlite
            └── schema.sql
```

当前代码把原始 SQLite 数据库的位置固定写成 `spider/test_database/`，即使运行的是开发集也使用该路径。若官方压缩包解压后的目录名为 `database/`，请将其中需要的 `<db_id>` 子目录复制到项目的 `spider/test_database/` 下；不要因为目录名含 test 就改用另一组题目或另一套标注。

- `Tree_Running/Tools/test_file_related.py` 读取 `spider/dev.json` 和每个数据库的 `schema.sql`。
- `Tree_Running/Agents/Tools/KG_DB_foundamental_functions.py` 执行对应的 `<db_id>.sqlite`。
- `correctified_official_evaluation/correctified_evaluation.py` 同样读取 `spider/test_database/<db_id>/<db_id>.sqlite`。

确认每个问题的 `db_id` 都有对应数据库。官方包中的部分数据库可能没有 `schema.sql`；此时需从对应 SQLite 数据库的 `sqlite_master` 中导出建表语句，写入该文件，并检查表名、列名、主外键以及引号格式是否能被本项目的正则解析器识别。不要创建空的 schema 文件代替。

根目录 `Run.py` 自动按 `spider/dev.json` 的实际长度，从第 0 题开始依次运行全部题目，不再读取额外的题号选择文件。对于 1,034 道题的开发集，运行范围为 `0` 至 `1033`。原有失败时停止的处理保持不变；修复失败原因后重新启动，仍从第 0 题开始。输出文件仍采用追加写入，重新完整运行前请移走或清空根目录的旧运行输出，避免重复追加；不要删除 `Evaluation/` 中保留的最终评测输入。

`DB-KG-Initialization/` 和两套 Agent 的 Tools 目录中保留了小型 `CREATE_TABLE_MESSAGE.txt`、`Database_kg.txt`。它们是现有代码使用的结构文件，运行时会按数据库更新；初始化脚本通过当前 Python 解释器调用，路径相对于源码位置确定，支持含空格的目录名。

## 3. 下载 test-suite 专用数据库

- [test-suite 官方仓库及使用说明](https://github.com/taoyds/test-suite-sql-eval)。
- [官方 README 提供的测试数据库下载链接](https://drive.google.com/file/d/1mkCx2GOFIqNesD4y8TDAO1yX1QZORP5w/view?usp=sharing)。

test-suite 的测试数据库与 Agent 使用的原始 Spider 数据库用途不同。将下载内容解压并整理到项目根目录的 `test_suite_database/`，确保其下直接按 `<db_id>` 分目录，并保留下载包中同一数据库的各个测试实例。

```text
Spider_Experiment/
└── test_suite_database/
    └── <db_id>/
        └── ...下载包提供的 SQLite 测试实例...
```

不要把压缩包的外层目录误当作 `--db` 路径；也不要用原始数据库的单库执行比较冒充完整 test-suite 评测。

## 4. 保留的最终评测输入

位置：`Evaluation/test-suite-sql-eval-master/test-suite-sql-eval-master/`。

| 文件 | 用途 |
| --- | --- |
| `DEV_gold.txt` | 与预测配套的 1,034 行参考 SQL 和数据库 ID |
| `SDB_GPT3.5_predict.txt` | 1,034 行 GPT-3.5 预测 |
| `SDB_GPT4.0_predict.txt` | 1,034 行 GPT-4 预测 |
| `SDB_GPT4.0_predict_re.txt` | 1,034 行另一版 GPT-4 预测 |

三份预测内容不同，暂全部保留，具体哪一份作为最终发布结果待负责人确认。保留原始文件名，未擅自将 `_re` 标为最终版本。`DEV_gold.txt` 作为最终评测配套输入保留，不属于此次删除的原始数据包。

行数一致仅是初步检查，不等于已验证题目顺序、数据版本及论文指标完全一致。对新的预测，必须保证每行与 gold 对应，且每条 SQL 占一行。

## 5. test-suite 运行示例

以下在项目根目录的 PowerShell 中执行。先安装适用的 Python 环境及评测依赖；第三方工具声明需要 `sqlparse`、`nltk`，本地评测代码还使用 `tqdm`。数据下载和环境准备未在本次清理中执行。

```powershell
python -m pip install sqlparse nltk tqdm

$evalDir = 'Evaluation/test-suite-sql-eval-master/test-suite-sql-eval-master'
python "$evalDir/evaluation.py" --gold "$evalDir/DEV_gold.txt" --pred "$evalDir/SDB_GPT3.5_predict.txt" --db 'test_suite_database' --table 'spider/tables.json' --etype exec --progress_bar_for_each_datapoint
```

评测另外两份预测时，仅替换 `--pred` 对应文件名。`--etype exec` 计算执行评测；需要同时计算结构匹配时，按第三方 README 使用 `--etype all` 并提供对应的 `tables.json`。

本方法生成包含值的 SQL，示例不加 `--plug_value`。该选项会使用 gold 中的值填充预测，改变评测条件，不应在未说明的情况下使用。其他选项也应与论文实验设置保持一致。

## 6. 修正版评测

保留 `correctified_official_evaluation/` 中的源码及 `Correctified_Spider_dev_target_ouput/` 下的 70 个修正参考文件。这些文件是评测输入，不是可丢弃的模型中间输出。保留其原有目录和拼写，因为代码按这些路径读取。

模型的 `*_predict_ouput/` 逐题结果已删除。修正版评测在缺少对应结果目录时会通过 `obtain_predict_csv` 重新执行预测并生成它们。

准备好第 2 节的原始数据库后，在项目根目录执行：

```powershell
$evalDir = 'Evaluation/test-suite-sql-eval-master/test-suite-sql-eval-master'
python 'correctified_official_evaluation/correctified_evaluation.py' "$evalDir/SDB_GPT3.5_predict.txt" "$evalDir/DEV_gold.txt" 'SDB_GPT3.5'
```

运行此脚本还需要 `pandas`、`chardet`、`func_timeout`、`tabulate`、`nltk` 等适用依赖。该脚本输出的是其定义的修正统计，请按实际实验方法使用，不要将其单独输出直接当作 test-suite 总分。

路径定位与初始化调用已完成可移植性修复，Agent 和评测算法未因此更改；尚未重新运行或验证实验分数。显式传给评测命令的相对输入路径按当前工作目录解释，上述命令按项目根目录编写。
