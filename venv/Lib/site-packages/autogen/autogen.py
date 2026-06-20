#!/usr/bin/env python
try:
    import win32api
except:
    # not available on linux
    pass
from docopt import docopt
import shutil
import os
from os.path import join
import sys
from pkg_resources import get_distribution, DistributionNotFound
import yaml
from .project import Project, subprocess_run
from .utils import get_root
from .defaultlog import log

TEMPLATES = os.path.abspath(join(__file__, os.pardir, os.pardir, "templates"))

def main():
    """
    Tool to configure python projects

    Usage:
        autogen -d|-s|-M|-m|-p

    options:
        -h, --help     Display this help message
        -v, --version  Show version and exit

        -d, --docs     Generate sphinx docs
        -s, --setup    Generate setup.py
        -M,--major     Publish major release
        -m,--minor     Publish minor release
        -p,--patch     Publish patch release

    """
    # process args
    try:
        version = get_distribution("autogen").version
    except DistributionNotFound:
        version = "not installed"
    args = docopt(main.__doc__, version=version)
    log.info(args)

    root = get_root()
    if not root:
        log.error("must be run inside a git repo")
        sys.exit()

    # docs
    if args["--docs"]:
        os.chdir(root)
        make_docs()
        return

    # setup.py
    p = Project()
    if args["--setup"]:
        p.create_setup()
        return

    # release = update version; recreate setup.py; release to git; release to pypi
    if args["--major"] or args["--minor"] or args["--patch"]:
        if subprocess_run("git status --porcelain"):
            log.error("git commit all changes before release")
            return
        if args["--major"]:
            p.update_version(0)
        elif args["--minor"]:
            p.update_version(1)
        elif args["--patch"]:
            p.update_version(2)
        p.release()

def make_docs():
    """ initialise everything needed for generating docs and publishing on gitlab pages automatically """
    docs = "docs"
    os.makedirs(docs, exist_ok=True)

    # create files if they don't exist
    files = ["index.rst", "conf.py", "confplus.py", "makefile", "example_page.rst", "example_image.jpg"]
    exists = [f for f in files if os.path.exists(f"{docs}/{f}")]
    created = set(files) - set(exists)
    if exists:
        exists = ", ".join(exists)
        log.warning(f"already exists: {exists}")
    if created:
        for f in created:
            shutil.copy(f"{TEMPLATES}/{f}", docs)
        created = ", ".join(created)
        log.info(f"created: {created}")

    # update or copy gitlab CI
    with open(f"{TEMPLATES}/.gitlab-ci.yml") as f:
        pages_ci = yaml.safe_load(f)
    if os.path.exists(".gitlab-ci.yml"):
        with open(".gitlab-ci.yml") as f:
            ci = yaml.safe_load(f)
        if "pages" not in ci:
            ci["pages"] = pages_ci["pages"]
            log.info(f"gitlab-ci updated")
        log.warning(f"gitlab-ci already includes pages")
    else:
        shutil.copy(f"{TEMPLATES}/.gitlab-ci.yml", ".gitlab-ci.yml")
        log.info(f"gitlab-ci created")

if __name__ == "__main__":
    main()
