import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main():
    parser = argparse.ArgumentParser(description="Generate SQL for one Spider question.")
    parser.add_argument("question", help="Natural-language question")
    parser.add_argument("--db-id", required=True, help="Spider database identifier")
    args = parser.parse_args()

    from Tree_Running.Tools.test_file_related import change_kg

    if not change_kg(args.db_id):
        raise RuntimeError("Database structure initialization failed.")

    from Tree_Running.Task_Tree_Running import Task_Tree_Running

    signal, task_tree, final_code = Task_Tree_Running(
        root_task=args.question, root_task_iden="0", db_id=args.db_id
    )
    print("Status:", signal)
    print(final_code)


if __name__ == "__main__":
    main()
