from pylint.lint import Run
import glob


for file in glob.glob("src/*.py"):
    print(file)
    result = Run([file], do_exit=False)