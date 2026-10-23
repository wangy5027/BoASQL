# BoA-SQL：Agent 推理与 Spider 实验

本目录提供 **BoA-SQL: Executable Blueprint-of-Action for Text-to-SQL with reinforcement learning** 的 Agent 推理与 Spider 实验代码。系统根据自然语言问题检索数据库结构、制定执行计划，并通过 SQL 执行反馈修正生成结果。

| 论文信息 | 内容 |
| --- | --- |
| 论文题目 | BoA-SQL: Executable Blueprint-of-Action for Text-to-SQL with reinforcement learning |
| 作者 | Yang Wang; Zhilong Xie; Lin Zhang; Lingyun Gu; Qing Li |
| 发表年份 | 2026 |
| 期刊 | Engineering Applications of Artificial Intelligence |
| 卷与文章编号 | 166, 113454 |
| 论文代码仓库 | [wangy5027/BoASQL](https://github.com/wangy5027/BoASQL) |
| 论文与 DOI | [10.1016/j.engappai.2025.113454](https://doi.org/10.1016/j.engappai.2025.113454) |
| BibTeX 引用 | [论文引用](../citation.bib) |
| 团队代码汇总仓库 | [wangy5027/FICCodes](https://github.com/wangy5027/FICCodes) |

## 方法流程

1. **数据库结构准备**：从建表语句提取表、列、数据类型及主外键关系，生成供 Agent 使用的结构描述。
2. **相关信息筛选**：根据问题选择相关表和列，缩小生成 SQL 时使用的上下文。
3. **任务规划**：判断任务复杂度，为需要分解的问题生成任务树。
4. **逐步生成 SQL**：按任务顺序生成 SQL，并将前序步骤与当前步骤合并。
5. **执行与修复**：在 SQLite 数据库上执行 SQL，利用报错修复语句；必要时根据失败原因重新规划任务。
6. **最终检查与评测**：检查 SQL 与问题要求的一致性，保存预测，并使用 test-suite 和本项目的修正版评测进行分析。

当前任务树构建对分解深度和步骤数有约束。源码还保留了一条 `Tree_optimization` 路径，但其在主流程中的调用目前被注释；不能将该路径视为默认启用的功能。

## 主要文件

| 路径 | 用途 |
| --- | --- |
| [`Run.py`](Run.py) | 当前 Spider 批量运行入口 |
| [`DATA_SETUP.md`](DATA_SETUP.md) | 数据下载、放置位置和详细评测说明 |
| `DB-KG-Initialization/` | 从建表语句生成数据库结构描述 |
| `Tree_Running/Task_Tree_Running.py` | 任务执行、SQL 衔接和失败后重新规划 |
| `Tree_Running/Tree_Building/` | 表列筛选、任务分解和规划相关工具 |
| `Tree_Running/Agents/` | 模型接口、SQL 生成、报错修复和最终检查 |
| `Tree_Running/Tools/` | 数据读取、数据库切换和输出记录 |
| `Evaluation/test-suite-sql-eval-master/test-suite-sql-eval-master/` | 第三方 test-suite 工具和保留的预测文件 |
| `correctified_official_evaluation/` | 本实验使用的修正版评测 |

批量运行使用根目录的 `Run.py`；单题运行使用 `Tree_Running/Run.py`，并显式提供问题和 `--db-id`。两种入口均可通过脚本路径从其他工作目录启动。

## 环境准备

项目资源路径根据源码位置定位，不依赖安装盘符、外层目录名称或当前工作目录。路径拼接使用跨平台接口，已在 Windows 下验证改名、含空格路径和异地启动；尚未在 Linux/macOS 上完整运行。建议先在 Python 3.11 环境中准备运行；这不是已经锁定并验证的完整复现环境。本目录尚未提供经端到端验证的依赖版本锁定文件。

在本目录打开 PowerShell，创建环境并安装当前主流程与评测所需的依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install openai pandas treelib sqlparse nltk tqdm chardet func_timeout tabulate
```

这些依赖来自当前源码的导入关系，未固定版本。若所安装的 NLTK 在评测时提示缺少资源，按错误提示安装对应资源。

`change_kg()` 使用 `sys.executable` 和参数列表启动数据库结构初始化脚本，自动复用当前 Python 解释器，并支持含空格的路径。也可以先激活环境再运行：

```powershell
.\.venv\Scripts\Activate.ps1
python --version
```

备用模型接口文件涉及 `anthropic`、`google.generativeai`、`huggingface_hub`、`groq` 和 `mistralai`，默认主流程不导入它们，无需为了运行默认流程全部安装。

## 配置模型

当前主流程分别从以下文件导入模型接口：

- `Tree_Running/Agents/agents_init.py`
- `Tree_Running/Tree_Building/Agents/agents_init.py`

两处默认 `LlmAgent` 的模型名称均为 `gpt-3.5-turbo-16k`，温度为 `0`。该名称是历史实验配置，不代表所使用的服务当前一定提供该模型。

发布版本的两处默认接口均从环境变量读取配置。在运行程序的同一个 PowerShell 窗口中设置：

```powershell
$env:OPENAI_API_KEY = 'YOUR_API_KEY'
$env:OPENAI_BASE_URL = 'https://api.openai.com/v1'
$env:OPENAI_MODEL = 'YOUR_AVAILABLE_MODEL_NAME'
```

请替换示例值。使用其他 OpenAI 兼容服务时，设置其实际接口地址，并确认模型支持当前请求参数。未设置 `OPENAI_MODEL` 时保留历史默认模型名称；没有 `OPENAI_API_KEY` 时程序会在初始化阶段报错。不要把真实凭据写入源码或提交到仓库。

Claude、Gemini、Llama、Mistral 等接口文件是备用实现，目前没有统一的命令行模型切换参数。仅修改备用文件不会自动切换主流程。

## 数据准备

本项目使用 **Spider 1.0**。数据文件与数据库不随本目录提供。

- [Spider 官方主页与下载入口](https://yale-lily.github.io/spider)
- [Spider 数据下载链接](https://drive.google.com/file/d/1403EGqzIDoHMdQF4c9Bkyl7dZLZ5Wt6J/view?usp=sharing)
- [test-suite 官方工具与数据说明](https://github.com/taoyds/test-suite-sql-eval)
- [test-suite 测试数据库下载链接](https://drive.google.com/file/d/1mkCx2GOFIqNesD4y8TDAO1yX1QZORP5w/view?usp=sharing)

下载链接如有变化，以官方页面为准。完整的目录放置要求见 [`DATA_SETUP.md`](DATA_SETUP.md)。当前 Agent 读取：

```text
spider/dev.json
spider/test_database/<db_id>/<db_id>.sqlite
spider/test_database/<db_id>/schema.sql
```

虽然路径名为 `test_database`，当前入口读取的仍是 `dev.json` 开发集。下载包若使用 `database` 目录名，需要按现有代码要求整理路径。

test-suite 测试数据库另放在 `test_suite_database/`，不要与 Agent 使用的原始 SQLite 数据库混淆。缺少 `schema.sql` 的数据库需要按数据准备说明补齐。

## 运行 Agent

完成依赖、模型配置和数据准备后，在项目根目录执行：

```powershell
python Run.py
```

单题运行示例（需准备相应的 `concert_singer` 数据库）：

```powershell
python Tree_Running/Run.py "How many singers are there?" --db-id concert_singer
```

项目文件夹可以重命名或移动；保留内部相对层级即可。数据和运行输出始终定位到项目根目录。从其他目录启动时，使用实际的脚本路径，例如 `python "../my project/Run.py"`。

程序按照 `spider/dev.json` 的实际长度，从第 `0` 题顺序运行，不需要题号选择文件。对于 1,034 道题的开发集，范围为 `0` 至 `1033`。

- 程序保留失败时停止的行为；修复问题后重新启动仍从第 `0` 题开始，不自动断点续跑。
- 每道题可能触发多次模型请求，完整运行需要相应的服务额度。
- 不要同时启动多个实例处理不同数据库：当前数据库结构文件和输出文件为共享路径。

运行会在根目录生成或追加：

| 输出 | 内容 |
| --- | --- |
| `DEV_predict.txt` | 生成的 SQL |
| `DEV_gold.txt` | 对应参考 SQL 与数据库 ID |
| `DEV_question.txt` | 题号与问题 |
| `printlog.txt` | 运行日志 |
| `trees.json` | 任务树记录 |

这些文件仍采用追加写入。重新完整运行前，应移走或清空根目录旧输出，避免重复记录；不要误删 `Evaluation/` 下保留的评测输入。当前 `trees.json` 会连续追加 JSON 对象，不是一个可直接整体解析的标准 JSON 数组。

## 评测

### test-suite

评测目录保留以下历史预测，每份均为 1,034 行：

- `SDB_GPT3.5_predict.txt`
- `SDB_GPT4.0_predict.txt`
- `SDB_GPT4.0_predict_re.txt`

配套 gold 为同目录下的 `DEV_gold.txt`。三份预测内容不同，具体与论文报告结果的对应关系仍需负责人确认，不能仅根据 `_re` 后缀判定最终版本。

数据准备完成后，在项目根目录运行：

```powershell
$evalDir = 'Evaluation/test-suite-sql-eval-master/test-suite-sql-eval-master'
python "$evalDir/evaluation.py" --gold "$evalDir/DEV_gold.txt" --pred "$evalDir/SDB_GPT3.5_predict.txt" --db 'test_suite_database' --table 'spider/tables.json' --etype exec --progress_bar_for_each_datapoint
```

评测其他保留版本时替换 `--pred`。评测本次重新生成的输出时，将 `--gold` 和 `--pred` 分别改为根目录的 `DEV_gold.txt`、`DEV_predict.txt`，并先核对二者的题目顺序、行数和单行 SQL 格式。

示例不使用 `--plug_value`，因为它会用 gold 中的值填充预测，改变评测条件。其他选项应与实际论文实验设置一致。

### 修正版评测

`correctified_official_evaluation/` 是本实验的一部分。其 `Correctified_Spider_dev_target_ouput/` 下的 70 个修正参考文件是必要输入，不能当作中间结果删除。

在原始 Spider 数据库准备完成后执行：

```powershell
$evalDir = 'Evaluation/test-suite-sql-eval-master/test-suite-sql-eval-master'
python 'correctified_official_evaluation/correctified_evaluation.py' "$evalDir/SDB_GPT3.5_predict.txt" "$evalDir/DEV_gold.txt" 'SDB_GPT3.5'
```

脚本会在缺少对应目录时生成逐题执行结果。重复评测同名项目但替换了预测文件时，应先清理该项目旧的 `*_predict_ouput/` 目录，避免复用过期结果。

修正版脚本有自身的结果比较规则，输出其定义的修正统计。请结合实际实验方法解释，不能将它的输出直接当作 test-suite 总分。

## 当前版本的复现边界

- **资源定位约定**：项目自有资源以源码所在位置为基准；`Spider_Experiment` 只是当前文件夹名称，不再参与路径计算。评测命令中显式提供的相对输入路径（如 `--pred`、`--gold`、`--db`）仍按命令执行时的工作目录解释；从其他位置调用评测时请相应调整参数。
- **历史评测辅助入口**：`correctified_official_evaluation/evaluation.py` 需要显式传入项目名，汇总已生成的目标和预测目录；导入该文件不会再自动读取写死的旧实验目录。该脚本不代替上文的修正版评测入口。
- **异常处理**：部分递归重试分支没有返回递归结果，失败路径可能导致返回值异常；尚未进行完整修复。
- **验证范围**：当前做过源码语法检查、模拟数据从第 0 题顺序遍历检查，以及改名/含空格路径/不同工作目录下的结构初始化、数据库读取、评测输出和单题入口检查。尚未重新下载数据、调用模型完成全量实验或复核论文指标。
- **发布状态**：默认模型接口已移除硬编码凭据，仍需确认依赖版本及最终预测版本；本目录不声明已经具备开箱即用的完整论文复现能力。

## 路径回归检查

在项目根目录运行，不需要真实数据或模型 API：

```powershell
python -B -m unittest discover -s tests -v
```

测试在临时副本中创建小型 SQLite 数据库，模拟可选依赖，并验证重命名、含空格路径和不同工作目录下的资源定位。它不运行真实模型，也不代表完整实验已复现。

## 第三方代码与引用

test-suite 工具来自 [taoyds/test-suite-sql-eval](https://github.com/taoyds/test-suite-sql-eval)，保留其 [原始 README](Evaluation/test-suite-sql-eval-master/test-suite-sql-eval-master/README.md) 与 [LICENSE](Evaluation/test-suite-sql-eval-master/test-suite-sql-eval-master/LICENSE)。当前目录已移除其数据包、示例数据及与本次 Spider 实验无关的实验产物；上游 README 中的其他任务示例不一定具有对应的本地数据。

使用 Spider 与 test-suite 时，请遵循官方数据和代码的许可、引用要求。本项目自有代码的开源许可尚未在此目录声明，第三方工具的许可证不自动适用于全部代码。
