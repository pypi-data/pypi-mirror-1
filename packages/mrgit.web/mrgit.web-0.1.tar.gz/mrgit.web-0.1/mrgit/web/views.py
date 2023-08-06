
import git
from webob.exc import HTTPFound

from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.chameleon_zpt import get_template
from repoze.bfg.location import lineage
from repoze.bfg.settings import get_settings
from repoze.bfg.view import static

from pygments import highlight
from pygments.lexers import get_lexer_for_mimetype
from pygments.formatters import HtmlFormatter


static = static('static')


class BaseView(object):
    """
    """

    layout = 'templates/layout.pt'
    template = None

    def __init__(self, context, request):
        self.request = request
        self.context = context
        self.context_url = request.application_url + request.path

    def __call__(self):
        if not self.template:
            raise NotImplemented, 'template not defined'
        return render_template_to_response(self.template,
                request = self.request, context = self.context,
                view = self, layout = get_template(self.layout))

    # TODO: memoize per request
    @property
    def travesable_objects(self):
        return [item for item in lineage(self.context)]

    def menu_items(self):
        items = []
        items_url = self.request.application_url
        for item in reversed(self.travesable_objects):
            if items:
                items_url += '/'+item.__name__
            items.append(dict(
                name = item.__name__,
                url = items_url,
                current = False))
        if items:
            items[-1]['current'] = True
        return items

class ReposView(BaseView):
    template = 'templates/repos.pt'
    

class RepoView(BaseView):
    template = 'templates/repo.pt'

    def __call__(self):
        # 1. resolve head
        # TODO: read head from cookie
        head = 'master'

        # 2. check if head exists and redirect to it
        if head in [i.name for i in self.context.heads]:
            return HTTPFound(location=self.context_url+'tree/'+head)
    
        # 3. if not say that repository is empty
        super(RepoView, self).__call__()

class RepoBrowserView(BaseView):
    pass

class TreeView(BaseView):
    template = 'templates/tree.pt'

    @property
    def last_tree_commit(self):
        commit = self.context.repo.git.log(
            '-1', '--format=%ar (%ai)|||%an|||%s').split('|||')
        return dict(
            date    = commit[0],
            author  = commit[1],
            comment = commit[2])

    def last_commit(self, blob, format='%s'):
        return self.context.repo.git.log(
                    '-1', '--format='+format, '--', blob)

class BlobView(TreeView):
    lexer = None
    template = 'templates/blob.pt' 
    formatter = HtmlFormatter(linenos=True, cssclass="sourcecode")

    def __call__(self):
        try:
            self.lexer = get_lexer_for_mimetype(self.context.mime_type)
        except:
            return HTTPFound(location=self.context_url+'/@@download')
        return super(BlobView, self).__call__()

    def highlight(self, code):
        return highlight(code, self.lexer, self.formatter)

class BlobDownloadView(BaseView):
    
    def __call__(self):
        import pdb; pdb.set_trace()
