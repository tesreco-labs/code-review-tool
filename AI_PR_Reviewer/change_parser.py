import re


def extract_changes(patch):
    """
    Extract changes with line number information.

    Returns:
    [
        {
            "change_type": "...",
            "old_code": "...",
            "new_code": "...",
            "old_start": ...,
            "old_end": ...,
            "new_start": ...,
            "new_end": ...
        }
    ]
    """

    if not patch:
        return []

    changes = []

    lines = patch.splitlines()

    old_line = 0
    new_line = 0

    i = 0

    while i < len(lines):

        line = lines[i]

        # -------------------------
        # Parse Hunk Header
        # -------------------------

        if line.startswith("@@"):

            match = re.search(
                r'@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@',
                line
            )

            if match:

                old_line = int(match.group(1))
                new_line = int(match.group(2))

            i += 1
            continue

        # -------------------------
        # Modification
        # -------------------------

        if line.startswith("-"):

            old_start = old_line
            new_start = new_line

            old_block = []

            while i < len(lines) and lines[i].startswith("-"):

                old_block.append(lines[i][1:])
                old_line += 1
                i += 1

            new_block = []

            while i < len(lines) and lines[i].startswith("+"):

                new_block.append(lines[i][1:])
                new_line += 1
                i += 1

            changes.append({

                "change_type": "modified",

                "old_code": "\n".join(old_block),

                "new_code": "\n".join(new_block),

                "old_start": old_start,
                "old_end": old_line - 1,

                "new_start": new_start,
                "new_end": new_line - 1

            })

            continue

        # -------------------------
        # Addition
        # -------------------------

        elif line.startswith("+"):

            start = new_line

            block = []

            while i < len(lines) and lines[i].startswith("+"):

                block.append(lines[i][1:])
                new_line += 1
                i += 1

            changes.append({

                "change_type": "added",

                "old_code": "",

                "new_code": "\n".join(block),

                "old_start": None,
                "old_end": None,

                "new_start": start,
                "new_end": new_line - 1

            })

            continue

        else:

            old_line += 1
            new_line += 1

        i += 1

    return changes