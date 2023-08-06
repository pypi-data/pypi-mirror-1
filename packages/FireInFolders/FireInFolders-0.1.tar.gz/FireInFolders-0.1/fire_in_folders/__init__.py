#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from subprocess import Popen
from optparse import OptionParser


def fire_in_folder(folder, args):
    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        if os.path.isdir(path) and not file.startswith('.'): # TODO: linux specific
            p = Popen(
                args=args,
                cwd=path,
            )
            p.wait()

def main():
    parser = OptionParser(usage="fire_in_folders [options] command\n")
    parser.add_option(
        "-s",
        "--src",
        action="store",
        dest="src",
        type="string",
        default="src",
        help="destination folder where to execute command in all subfolders")

    (options, args) = parser.parse_args()

    if not len(args):
        parser.parse_args(['-h'])

    target_path = os.path.join(os.getcwd(), options.src)

    if not os.path.exists(target_path):
        parser.error('Folder does not exist: %s' % target_path)

    fire_in_folder(target_path, args)


if __name__ == '__main__':
    main()
