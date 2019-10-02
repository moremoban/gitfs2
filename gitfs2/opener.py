from gitfs2 import repo
from fs.osfs import OSFS
from fs.opener import Opener


class GitFSOpener(Opener):
    protocols = ["git"]
    update_registry = {}

    def open_fs(self, fs_url, parse_result, writeable, create, cwd):
        repo_name, _, dir_path = parse_result.resource.partition("/")
        git_url = "{protocol}://{resource}".format(
            protocol=parse_result.protocol, resource=parse_result.resource
        )
        require = repo.GitRequire(
            git_url=git_url,
            branch=parse_result.params.get("branch"),
            submodule=parse_result.params.get("submodule"),
            reference=parse_result.params.get("reference"),
        )
        local_folder = repo.git_clone(
            require, action_required=GitFSOpener.update_registry.get(git_url, True)
        )
        if GitFSOpener.update_registry.get(git_url, True):
            GitFSOpener.update_registry[git_url] = False
        if parse_result.path:
            local_folder = local_folder + parse_result.path
        osfs = OSFS(root_path=local_folder)
        return osfs
