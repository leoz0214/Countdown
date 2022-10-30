from pylint.lint import Run
import glob
import sys


if __name__ == "__main__":
    sys.path.extend((".", "./src"))
    for file in glob.glob("src/*.py"):
        result = Run([file], do_exit=False)