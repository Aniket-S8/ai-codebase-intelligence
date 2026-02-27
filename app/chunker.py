import re


def extract_java_chunks(file_content):
    """
    Extract class-level and method-level chunks from Java file.
    Returns list of chunk dictionaries.
    """

    chunks = []

    lines = file_content.split("\n")

    class_pattern = re.compile(r"\bclass\s+(\w+)")
    method_pattern = re.compile(
        r"\b(public|private|protected)\s+[\w<>\[\]]+\s+(\w+)\s*\("
    )

    current_class = None

    for i, line in enumerate(lines):
        class_match = class_pattern.search(line)
        if class_match:
            current_class = class_match.group(1)

        method_match = method_pattern.search(line)
        if method_match:
            method_name = method_match.group(2)

            # Capture method block (naive brace matching)
            start_line = i
            brace_count = 0
            method_lines = []

            for j in range(i, len(lines)):
                method_lines.append(lines[j])
                brace_count += lines[j].count("{")
                brace_count -= lines[j].count("}")

                if brace_count == 0 and "}" in lines[j]:
                    end_line = j
                    break

            chunks.append(
                {
                    "class_name": current_class,
                    "method_name": method_name,
                    "content": "\n".join(method_lines),
                    "start_line": start_line + 1,
                    "end_line": end_line + 1,
                }
            )

    return chunks