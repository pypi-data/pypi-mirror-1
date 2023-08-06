
import os
import git
from repoze.bfg.settings import get_settings


class Dummy(object):

    def __init__(self, environ):
        pass

class Repos(object):

    def __getitem__(self, key):
        repo_dir = os.path.join(get_settings()['repos_dir'], key)
        if os.path.isdir(repo_dir):
            return Repo(repo_dir)
        raise KeyError

    @property
    def repositories(self):
        return os.listdir(get_settings()['repos_dir'])

class Repo(git.Repo):

    @property
    def __name__(self):
        return self.path.split('/')[-1]
   
    def __getitem__(self, key):
        if key == 'tree':
            return RepoBrowser(self)
        # TODO: make it pluggable so we can plug issues, wiki, etc...
        raise KeyError

class RepoBrowser(object):
   
    __name__ = 'tree'
    
    tree_path = []

    def __init__(self, repo):
        self.repo = repo

    @property
    def __parent__(self):
        return Repo(self.repo.path)
        
    def __getitem__(self, key):
        if key in [i.name for i in self.repo.heads]:
            return Tree(self, self.repo, key)
        raise KeyError

class Tree(git.Tree):

    def __init__(self, parent, *arg, **kw):
        super(Tree, self).__init__(*arg, **kw)
        self.tree_path = parent.tree_path + [parent]
        
    @property
    def __name__(self):
        if self.name:
            return self.name
        return self.id

    @property
    def __parent__(self):
        return self.tree_path[-1]

    def __getitem__(self, key):
        if key in self.keys():

            item = self.get(key)
            
            if item.__class__ == git.Blob:
                return Blob(self, item.repo, item.id,
                    mode=item.mode, name=item.name)
            elif item.__class__ == git.Tree:
                return Tree(self, item.repo, item.id,
                    mode=item.mode, name=item.name)

        raise KeyError

class Blob(git.Blob):
    
    def __init__(self, parent, *arg, **kw):
        super(Blob, self).__init__(*arg, **kw)
        self.tree_path = parent.tree_path + [parent]

    @property
    def __name__(self):
        return self.name
    
    @property
    def __parent__(self):
        return self.tree_path[-1]

