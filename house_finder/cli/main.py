from argparse import ArgumentParser

import yaml

from .. import finder
from .. import place

def parse_arguments():

    parser = ArgumentParser()
    parser.add_argument('--input', '-i', help='input yaml file with search specifications')
    parser.add_argument('--secrets', '-s', help='yaml file containing passcodes and keys')
    parser.add_argument('--output', '-o', help='output file path')
    args = parser.parse_args()

    return load_yaml(args.input), load_yaml(args.secrets), args.output

def load_yaml(file_path):
    with open(file_path) as file:
        return yaml.load(file)

def main():
    input, secrets, output = parse_arguments()
    finder.optimise(input, secrets, output)


if __name__ == "__main__":
    main()
    place.cache.close()
