import argparse

from ply_parser import parse_cmd
from ply_parser import parse_file


parser = argparse.ArgumentParser()
parser.add_argument("--file", help="path to file")
parser.add_argument("--hide_tree", help="hide ast tree")
parser.add_argument("--verbose", help="display lexer tokens")

if __name__ == "__main__":
    args = parser.parse_args()

    verbosity_flag = True if args.verbose == "1" else False

    if args.file is not None:
        parse_file(args.file, verbosity_flag)
    else:
        parse_cmd(True if args.hide_tree == "1" else False, verbosity_flag)
