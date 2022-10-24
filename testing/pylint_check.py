from pylint.lint import Run
import glob


if __name__ == "__main__":
    for file in glob.glob("src/*.py"):
        result = Run([file], do_exit=False)