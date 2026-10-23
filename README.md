# BoA-SQL

**BoA-SQL: Executable Blueprint-of-Action for Text-to-SQL with reinforcement learning**

Yang Wang, Zhilong Xie, Lin Zhang, Lingyun Gu, Qing Li

*Engineering Applications of Artificial Intelligence*, Volume 166, Part A, Article 113454 (2026).

[Paper / DOI](https://doi.org/10.1016/j.engappai.2025.113454) · [Publisher](https://www.sciencedirect.com/science/article/pii/S0952197625034852) · [BibTeX](citation.bib)

This repository provides the agent inference implementation and Spider experiments for BoA-SQL. The system converts natural language questions into SQL through schema filtering, task-tree planning, stepwise SQL generation, and repair guided by execution feedback.

## Release Scope

**This release includes agent inference and Spider experiment code. Reinforcement learning training code is not included.**

- Database schema initialization, table and column selection, task planning, SQL generation, execution, and repair.
- The test-suite evaluation tool, three historical prediction files, and their corresponding gold references.
- The corrected evaluation implementation used in our experiments, with 70 required reference files.
- Instructions for data preparation, model configuration, execution, and evaluation.

Full datasets, model weights, runtime caches, and intermediate experiment outputs are not included. See the [data preparation guide](Spider_Experiment/DATA_SETUP.md) for public dataset download links and expected file locations.

## Getting Started

Clone the repository and enter the experiment directory. The following commands use PowerShell:

```powershell
git clone https://github.com/wangy5027/BoASQL.git
Set-Location BoASQL/Spider_Experiment
```

Before running the agent, install the dependencies, prepare the data, and configure the model:

1. Follow the [environment and model setup instructions](Spider_Experiment/README.md). Configure the model interface through the `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `OPENAI_MODEL` environment variables.
2. Download Spider 1.0 and the required evaluation data, then arrange the databases and schema files as described in the [data preparation guide](Spider_Experiment/DATA_SETUP.md).
3. Run `python Run.py` for batch inference, or use the single-question entry point below. Single-question inference also requires the relevant database, dependencies, and model service.

```powershell
python Tree_Running/Run.py "How many singers are there?" --db-id concert_singer
```

Batch inference starts at question index 0 of the development set. Outputs are appended to existing files, so move or clear previous outputs before starting a new run. See the [detailed project guide](Spider_Experiment/README.md) for restart behavior, model API requirements, and evaluation commands. The detailed project and data preparation guides are currently in Chinese.

Project resources are located relative to the source files. You can move the project directory while preserving its internal structure. Relative paths explicitly passed to evaluation commands are resolved from the current working directory.

## Repository Contents and Reproducibility

| Path | Contents |
| --- | --- |
| [Spider_Experiment/](Spider_Experiment/) | Agent code, experiment documentation, evaluation tools, and path regression tests |
| [Spider_Experiment/README.md](Spider_Experiment/README.md) | Environment setup, model configuration, execution and evaluation commands, and known limitations |
| [Spider_Experiment/DATA_SETUP.md](Spider_Experiment/DATA_SETUP.md) | Dataset downloads, file layout, and evaluation inputs |
| [citation.bib](citation.bib) | BibTeX entry for the paper |

The release has passed static checks, mocked entry-point checks, and path regression checks covering renamed directories, paths containing spaces, and execution from different working directories. Full model experiments have not been rerun, and the reported paper metrics have not been revalidated for this release. Dependency versions are not pinned, and the mapping between the historical prediction files and the reported results still requires confirmation. See the project guide for detailed limitations.

Run the path checks from `Spider_Experiment` without real datasets or model API calls:

```powershell
python -B -m unittest discover -s tests -v
```

## Citation

If you find this project useful for your research, please cite our paper:

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

## Third-Party Resources and Feedback

This project uses the Spider dataset and the test-suite evaluation tool. Please follow their respective license and citation requirements. The test-suite tool's [original README](Spider_Experiment/Evaluation/test-suite-sql-eval-master/test-suite-sql-eval-master/README.md) and [LICENSE](Spider_Experiment/Evaluation/test-suite-sql-eval-master/test-suite-sql-eval-master/LICENSE) are retained. Third-party licenses do not automatically apply to all code in this repository; a license for the project's own code has not yet been declared.

Maintainer: [wangy5027](https://github.com/wangy5027). Please report usage questions through [GitHub Issues](https://github.com/wangy5027/BoASQL/issues), including your environment, command, and error output with sensitive information removed.
