import os
import sys
import errno
import subprocess
import logging

import fs
import fs.path
import fs.errors
from gitfs2 import reporter, constants

LOG = logging.getLogger(__name__)


class GitRequire(object):
    def __init__(
        self, git_url=None, branch=None, submodule="False", reference=None
    ):
        self.git_url = git_url
        self.submodule = convert_submodule(submodule)
        self.branch = branch
        self.reference = reference

    def clone_params(self):
        clone_params = {
            "single_branch": True,
            "depth": constants.DEFAULT_CLONE_DEPTH,
        }
        if self.branch is not None:
            clone_params["branch"] = self.branch
        elif self.reference is not None:
            clone_params["reference"] = self.reference
        return clone_params

    def __eq__(self, other):
        return (
            self.git_url == other.git_url
            and self.submodule == other.submodule
            and self.branch == other.branch
            and self.reference == other.reference
        )

    def __repr__(self):
        return "%s,%s,%s" % (self.git_url, self.branch, self.submodule)


def convert_submodule(submodule_string):
    if submodule_string in ["1", "True", "true"]:
        return True
    return False


def git_clone(require, action_required=True):
    from git import Repo
    from git.exc import GitCommandError

    if sys.platform != "win32":
        # Unfortunately for windows user, the following function
        # needs shell=True, which expose security risk. I would
        # rather not to trade it with its marginal benefit
        make_sure_git_is_available()

    app_home = get_app_home()
    mkdir_p(app_home)

    repo_name = get_repo_name(require.git_url)
    local_repo_folder = fs.path.join(app_home, repo_name)

    if action_required:
        try:
            fs.open_fs(local_repo_folder)
            reporter.info("Found repo in %s" % local_repo_folder)
            repo = Repo(local_repo_folder)
            repo.git.pull()
            if require.reference:
                repo.git.checkout(require.reference)
            elif require.branch:
                repo.git.checkout(require.branch)
            if require.submodule:
                reporter.info("updating submodule")
                repo.git.submodule("update")
        except fs.errors.CreateFailed:
            reporter.info("git clone %s" % require.git_url)
            repo = Repo.clone_from(
                require.git_url, local_repo_folder, **require.clone_params()
            )
            if require.submodule:
                reporter.info("checking out submodule")
                repo.git.submodule("update", "--init")
        except GitCommandError as e:
            reporter.warn("Unable to run git commands")
            LOG.warn(e)
            return local_repo_folder

    return local_repo_folder


def get_repo_name(repo_url):
    import giturlparse
    from giturlparse.parser import ParserError

    try:
        repo = giturlparse.parse(repo_url.rstrip("/"))
        return repo.name
    except ParserError:
        reporter.error(constants.MESSAGE_INVALID_GIT_URL % repo_url)
        raise


def get_app_home():
    from appdirs import user_cache_dir

    home_dir = user_cache_dir(appname=constants.PROGRAM_NAME)
    return fs.path.join(home_dir, constants.REPOS_DIR_NAME)


def make_sure_git_is_available():
    try:
        subprocess.check_output(["git", "--help"])
    except Exception:
        raise Exception("Please install git command")


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
