import subprocess
import shlex
import os
from os.path import join

import logging
log = logging.getLogger()

def normpath(path):
    """ return normalised path """
    return path.replace("\\", "/")

def subprocess_run(cmd):
    """ subprocess_run command string and return output """
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    result = subprocess.run(cmd, text=True, check=True, capture_output=True)
    return result.stdout

def get_root(path=None):
    """ return folder where .git is located; or False if not in a git repo """
    if not path:
        path = os.getcwd()
    while True:
        if ".git" in os.listdir(path):
            return path
        if path == os.path.dirname(path):
            return False
        path = os.path.dirname(path)

def git2docker():
    """ add .gitignore to .dockerignore """
    # get gitignore including global
    git = subprocess.getoutput(['git', 'status', "--porcelain", "--ignored"])
    git = [r.split()[1] for r in git.splitlines()]

    # add abs path
    root = subprocess.getoutput(["git", "rev-parse", "--show-toplevel"])
    git = ["!"+join(root, r[1:]) if r.startswith("!")
           else join(root, r) for r in git]

    # get dockerignore up to ####
    docker = []
    if os.path.exists(".dockerignore"):
        with open(".dockerignore") as f:
            for row in f.readlines():
                if row.startswith("####"):
                    break
                docker.append(row.strip("\r\n"))
    docker.append("#### Below added from files ignored by git")
    docker.append(".dockerignore")
    docker.extend(git)
    with open(".dockerignore", "w") as f:
        f.write("\n".join(docker))