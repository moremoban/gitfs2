import fs
from gitfs2.repo import GitRequire

from mock import patch
from nose.tools import ok_


@patch("gitfs2.repo.git_clone")
def test_opener(fake_clone):
    fake_clone.return_value = "."
    url = "git://github.com/moremoban/pypi-mobans.git?submodule=true!/tests"
    file_system = fs.open_fs(url)
    ok_(file_system.exists(u"test_gitfs_opener.py"))
    fake_clone.assert_called_with(
        GitRequire(
            git_url="git://github.com/moremoban/pypi-mobans.git",
            submodule="true",
        ),
        action_required=True,
    )
