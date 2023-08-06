
import os
from repoze.bfg.router import make_app
from mrgit.web.models import Repo

def repo(global_config, **kw):

    repo_dir = kw['repo_dir']
    
    # 1. path should be absolute
    repo_dir = os.path.abspath(repo_dir)

    # 2. check if folder exists
    if not os.path.isdir(repo_dir):
        # 2.1. create if it doesnt exists
        os.mkdir(repo_dir)
        # 2.2. initialize bare git repository
        root = Repo.create(repo_dir)

    # 3. instantiate repo
    else:
        root = Repo(repo_dir)

    def get_root(environ):
        return root

    import mrgit.web
    return make_app(get_root, mrgit.web, options=kw)

def repos(global_config, **kw):

    repos_dir = kw['repos_dir']
    
    # 1. path should be absolute
    if os.path.isabs(repos_dir):
        raise 'Configuration "repos_dir" option should provide absolute path.'

    raise NotImplemented, 'Yet!'

    import mrgit.web
    return make_app(mrgit.web.models.repos_root, mrgit.web, options=kw)
