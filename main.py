import argparse

from ply_parser import parse_cmd
from ply_parser import parse_file


parser = argparse.ArgumentParser()
parser.add_argument("--file", help="path to file")
parser.add_argument("--hide_tree", help="hide ast tree")

if __name__ == "__main__":
    args = parser.parse_args()

    if args.file is not None:
        parse_file(args.file)
    else:
        parse_cmd(True if args.hide_tree == "1" else False)
