def parse_patch(patch):
    lines = []

    for line in patch.split("\n"):
        if line.startswith("+") and not line.startswith("+++"):
            lines.append(line[1:].strip())

    return lines