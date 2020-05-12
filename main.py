import argparse

from ply_parser import run


parser = argparse.ArgumentParser()
parser.add_argument("--hide_tree", help="hide ast tree")

if __name__ == "__main__":
    args = parser.parse_args()

    run(True if args.hide_tree == "1" else False)
