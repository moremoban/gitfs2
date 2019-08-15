import fs
from gitfs2.repo import git_clone, GitRequire


def test_clone_a_real_github():
    git_url = "https://github.com/moremoban/hello"
    require = GitRequire(git_url=git_url)
    folder = git_clone(require)
    fs.open_fs(folder)
