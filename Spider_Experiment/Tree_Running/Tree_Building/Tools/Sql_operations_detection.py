import re

def extract_used_sql_operations_from_thinking(text):
    operations = []

    sentences = re.split(r"\.\s+|\n", text)  # Split text into sentences

    operation_patterns = {
        "filtering": [r"\bfiltering\b", r"\bfilter\b", r"\bfilter\b"],
        "grouping": [r"\bgrouping\b", r"\bgroup\b"],
        "multiple tables joining": [r"\bjoining\b", r"\bmultiple tables\b"],
        # Add more operation patterns as needed
        "aggregating": [r"\baggregating\b", r"\baggregate\b", r"\baggregation\b"],
        "indexing": [r"\bindexing\b", r"\bindex\b"],
        "merging": [r"\bmerging\b", r"\bmerge\b"],
        "partitioning": [r"\bpartitioning\b", r"\bpartition\b"],
        "sorting": [r"\bsorting\b", r"\bsort\b"],
    }

    for sentence in sentences:
        for operation, patterns in operation_patterns.items():
            matches = [re.search(pattern, sentence, re.IGNORECASE) for pattern in patterns]
            if any(matches):
                # print(sentence)
                # print("+",operation)
                if operation not in operations:
                    operations.append(operation)

        # Negation detection within the sentence
    negation_patterns = [r"\bnot require\b|\bnot requires\b", r"\bwithout\b", r"\babsence\b", r"\bnot involve\b|\bnot involves\b",r"\bthere is no\b"]
    for sentence in sentences:
        negation_matches = [re.search(pattern, sentence, re.IGNORECASE) for pattern in negation_patterns]
        if any(negation_matches):
            for operation, patterns in operation_patterns.items():
                matches = [re.search(pattern, sentence, re.IGNORECASE) for pattern in patterns]
                if any(matches):
                    # print(sentence)
                    # print("-",operation)
                    operations.remove(operation)

    return operations

# node_0_0 = "Based on the given information, the task requires joining three tables ('23_golden', '24_silver', '25_platinum') on the 'time' column. Since the tables have the same structure and only need to be joined on a single column, the complexity of this task is relatively low. There is no data filtering, grouping, or complex operations involved. Therefore, this task can be considered easy."
# node_0_1 = "Based on the given information, this task involves selecting specific columns from a joined table and filtering the data based on a specific date. The number of tables that need to be joined is not mentioned, so we cannot determine the complexity of the join operation. However, the task does not involve any complex operations like grouping or nested querying. It only requires selecting columns and applying a simple filter. Therefore, we can consider this task as easy."

# x = extract_used_sql_operations_from_thinking(node_0_0)
# print(x)