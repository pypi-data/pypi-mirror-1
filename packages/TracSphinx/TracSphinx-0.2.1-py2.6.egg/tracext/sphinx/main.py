"""
"""
# python import
import os

# genshi import
from genshi import XML

# trac import
from trac.core import *
from trac.web.chrome import INavigationContributor, ITemplateProvider, \
                            add_stylesheet
from trac.web.main import IRequestHandler
from trac.util import escape, Markup

# tools import
from sphinx.webtools import update_docs, reformat_content_links,\
                        PicklerContentManager, get_genentries, get_modentries

from sphinx.webtools import highlight, search

class SphinxPlugin(Component):
    implements(INavigationContributor, IRequestHandler, ITemplateProvider)

    # INavigationContributor methods

    def get_active_navigation_item(self, req):
        """
        """
        return 'sphinx'

    def get_navigation_items(self, req):
        """
        """
        # try to load user config
        try:
            navbar_title = self.config['sphinx'].get('navbar_title')
            if not navbar_title or navbar_title == '':
                navbar_title = 'Doc Sphinx'
        except:
            pass

        yield 'mainnav', 'sphinx', Markup('<a href="%s">%s</a>' % (
                self.env.href.sphinx(), navbar_title))

    # IRequestHandler methods

    def match_request(self, req):
        """
        """
        return req.path_info == '/sphinx'

    def process_request(self, req):
        """
        """
        # set the plugin stylesheet
        add_stylesheet(req, 'static/css/sphinx.css')

        # action search
        try:
            search_words = req.args.get('search')
            if not search_words == '':
                return self.__search(search_words)
        except:
            pass

        # action factory
        action = req.args.get('action')
        item = req.args.get('item')
        if action == 'refresh':
            return self.__refresh()

        if action == 'index' or item == 'genindex':
            return self.__index()

        if action == 'modules' or item == 'modindex':
            return self.__modules()

        if action == 'search' or item == 'search':
            return self.__search()

        # default
        pickler_url = req.args.get('item')
        search_words = req.args.get('search_words')
        return self.__view(pickler_url, search_words)

    # sphinx plugin part

    def __get_source_dir(self):
        """
        """
        # try to load user config
        try:
            source_dir = self.config['sphinx'].get('source_dir')
            if source_dir or not source_dir == '':
                return source_dir
        except:
            pass

        # source dir for the sphinx docs
        project_dir = self.config['trac'].get('repository_dir')
        source_dir = os.path.join(project_dir, 'docs', 'source')
        return source_dir

    def __get_doc_dir(self):
        """
        """
        # try to load user config
        try:
            doc_dir = self.config['sphinx'].get('doc_dir')
            if doc_dir or not doc_dir == '':
                return doc_dir
        except:
            pass

        # doc dir for the sphinx docs
        trac_dir = self.env.path
        doc_dir = os.path.join(trac_dir, 'sphinx-docs')
        return doc_dir

    def __refresh(self):
        """Controller for sphinx pickle doc refresh.
        """
        # get the source doc dir
        source_dir = self.__get_source_dir()

        # get the doc dir
        doc_dir = self.__get_doc_dir()

        # update the doc files
        error = update_docs(
                            source_dir=source_dir,
                            doc_dir=doc_dir)

        # success message
        if not error:
            msg = '<h1>'
            msg += '<a href="/pygloo/sphinx">Update done successfully!</a>'
            msg += '</h1>'
        else:
            msg = '<h1>An error occurred during the built!</h1>'

        # set result dict
        result = dict(
                    toc=None,
                    rellinks=None,
                    search='',
                    content=XML(msg),
                    error=error)

        # return for render
        return 'sphinx-view.html', result, None

    def __view(self, pickler_url=None, search_words=None):
        """
        """
        # set the base url
        base_url = 'sphinx'

        # get the doc dir
        doc_dir = self.__get_doc_dir()

        # default index path
        if not pickler_url:
            pickler_url = 'index'

        # get pickler content manager
        pickler_ct_manager = PicklerContentManager(
                                        base_url, doc_dir, pickler_url)

        # get the table of content
        toc_str = pickler_ct_manager.get_toc()

        # try to creat XML TOC
        if toc_str:
            toc = XML(toc_str)
        # None otherwise
        else:
            toc = None

        # get the rellinks
        rellinks = pickler_ct_manager.get_rellinks()

        # get the content
        content_str = pickler_ct_manager.get_body()

        # set class find in the content
        if search_words and content_str:
            search_words = search_words.replace('+', ' ')
            content_str = highlight(content_str, search_words)

        # little reformat
        if content_str:
            content_xml = XML(content_str)
            content = reformat_content_links(base_url, doc_dir, content_xml)
        else:
            content = None

        # set result dict
        result = dict(
                    toc=toc,
                    rellinks=rellinks,
                    search='',
                    content=content,
                    error=None)

        return 'sphinx-view.html', result, None

    def __index(self):
        """Controller for genindex sphinx function.
        """
        # set the base url
        base_url = 'sphinx'

        # get the doc dir
        doc_dir = self.__get_doc_dir()

        # get page entries
        entries = get_genentries(base_url, doc_dir)

        # set result dict
        result = dict(
                    search='',
                    entries=entries)

        return 'sphinx-index.html', result, None

    def __modules(self):
        """Controller for modindex sphinx function.
        """
        # set the base url
        base_url = 'sphinx'

        # get the doc dir
        doc_dir = self.__get_doc_dir()

        # get page entries
        entries = get_modentries(base_url, doc_dir)

        # set result dict
        result = dict(
                    search='',
                    entries=entries)

        return 'sphinx-modules.html', result, None

    def __search(self, search_words=''):
        """Controller for the search sphinx function
        """
        # set the base url
        base_url = 'sphinx'

        # get the doc dir
        doc_dir = self.__get_doc_dir()

        # search
        if not search_words == '':
            result = search(base_url, doc_dir, search_words)

        else:
            result = None

        # set result dict
        result = dict(
                    search=search_words,
                    result=result)

        # return for render
        return 'sphinx-search.html', result, None

    # ITemplateProvider methods

    def get_templates_dirs(self):
        """Used to add the plugin's templates.
        """
        from pkg_resources import resource_filename
        return [resource_filename(__name__, 'templates')]

    def get_htdocs_dirs(self):
        """Used to add the plugin's htdocs.
        """
        from pkg_resources import resource_filename
        return [('static', resource_filename(__name__, 'htdocs'))]
