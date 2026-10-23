# BoA-SQL

**BoA-SQL: Executable Blueprint-of-Action for Text-to-SQL with reinforcement learning**

Yang Wang, Zhilong Xie, Lin Zhang, Lingyun Gu, Qing Li

*Engineering Applications of Artificial Intelligence*, Volume 166, Part A, Article 113454 (2026).

[论文与 DOI](https://doi.org/10.1016/j.engappai.2025.113454) · [出版社页面](https://www.sciencedirect.com/science/article/pii/S0952197625034852) · [BibTeX 文件](citation.bib)

本仓库提供 BoA-SQL 的 Agent 推理与 Spider 实验实现。系统通过数据库结构筛选、任务树规划、逐步 SQL 生成与执行反馈修复，将自然语言问题转换为 SQL。

## 当前发布内容

**本次发布包含 Agent 推理与 Spider 实验代码，尚不包含强化学习训练代码。**

- 数据库结构初始化、表列筛选、任务规划、SQL 生成、执行与修复代码。
- test-suite 评测工具、三份历史预测及配套 gold。
- 本实验使用的修正版评测代码及 70 个必要参考文件。
- 数据准备、模型配置、运行与评测说明。

完整数据集、模型权重、运行缓存和中间实验输出不随仓库上传。公开数据集的下载入口及本地放置方式见[数据准备说明](Spider_Experiment/DATA_SETUP.md)。

## 开始使用

```powershell
git clone https://github.com/wangy5027/BoASQL.git
Set-Location BoASQL/Spider_Experiment
```

随后依次完成环境安装、数据下载和模型配置，再运行 Agent：

1. 阅读[环境安装与模型配置](Spider_Experiment/README.md)。模型接口通过 `OPENAI_API_KEY`、`OPENAI_BASE_URL` 和 `OPENAI_MODEL` 环境变量配置。
2. 按[数据准备说明](Spider_Experiment/DATA_SETUP.md)下载 Spider 1.0 和评测所需数据，整理数据库及建表语句。
3. 运行批量入口 `python Run.py`，或使用下方的单题入口；单题运行同样需要对应数据库、依赖及模型服务。

```powershell
python Tree_Running/Run.py "How many singers are there?" --db-id concert_singer
```

批量入口从开发集第 0 题开始。运行输出采用追加写入，重新运行前须处理旧输出；失败后的恢复方式、模型调用要求及评测命令请参阅[完整项目说明](Spider_Experiment/README.md)。

资源路径根据源码位置定位；可以移动项目文件夹，但请保留内部相对层级。评测命令显式传入的相对路径按执行命令时的工作目录解释。

## 目录与复现状态

| 路径 | 内容 |
| --- | --- |
| [Spider_Experiment/](Spider_Experiment/) | Agent 源码、实验说明、评测工具和路径回归测试 |
| [Spider_Experiment/README.md](Spider_Experiment/README.md) | 环境、模型、运行与评测命令，以及已知限制 |
| [Spider_Experiment/DATA_SETUP.md](Spider_Experiment/DATA_SETUP.md) | 数据下载、放置路径和评测输入说明 |
| [citation.bib](citation.bib) | 本论文的 BibTeX 引用 |

当前版本已完成静态与模拟入口检查，以及改名、含空格路径和不同工作目录下的路径回归检查。尚未重新执行完整模型实验或复核论文指标；依赖版本未锁定，历史预测文件与论文结果的对应关系仍需确认。详细限制见项目说明。

不需要真实数据或模型 API 的路径检查可在 `Spider_Experiment` 目录执行：

```powershell
python -B -m unittest discover -s tests -v
```

## 引用

如果本项目对你的研究有所帮助，请引用我们的论文：

```bibtex
@article{wang2026boasql,
  title   = {{BoA-SQL}: Executable {Blueprint-of-Action} for {Text-to-SQL} with reinforcement learning},
  author  = {Wang, Yang and Xie, Zhilong and Zhang, Lin and Gu, Lingyun and Li, Qing},
  journal = {Engineering Applications of Artificial Intelligence},
  volume  = {166},
  pages   = {113454},
  year    = {2026},
  doi     = {10.1016/j.engappai.2025.113454},
  url     = {https://doi.org/10.1016/j.engappai.2025.113454}
}
```

## 第三方资源与反馈

本项目使用 Spider 数据集和 test-suite 评测工具，请遵循各自的许可与引用要求。test-suite 的[原始说明](Spider_Experiment/Evaluation/test-suite-sql-eval-master/test-suite-sql-eval-master/README.md)和[许可证](Spider_Experiment/Evaluation/test-suite-sql-eval-master/test-suite-sql-eval-master/LICENSE)已保留；第三方许可证不自动适用于本项目的全部代码。本项目自有代码的开源许可尚未声明。

代码维护：[wangy5027](https://github.com/wangy5027)。使用问题可在[本仓库 Issues](https://github.com/wangy5027/BoASQL/issues)中反馈，附上运行环境、命令和已移除敏感信息的报错。
