import glob
import os


def remove_trailing_whitespace(code: str) -> str:
    lines = code.splitlines()
    new_lines = []
    for line in lines:
        for i in range(len(line) - 1, -1, -1):
            if line[i] != " ":
                break
        else:
            new_lines.append("")
            continue
        new_lines.append(line[:i + 1])
    return "\n".join(new_lines)


output_folder = "newsrc"
try:
    os.mkdir(output_folder)
except FileExistsError:
    pass
for path in glob.glob("src/*.py"):
    file = path.split("\\")[-1]
    with open(path, encoding="utf8") as f:
        with open(f"{output_folder}/{file}", "w", encoding="utf8") as g:
            g.write(remove_trailing_whitespace(f.read()))