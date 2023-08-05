import turbogears
from turbogears import controllers, expose, widgets
from wiki20.model import Page
from docutils.core import publish_parts
import re
from sqlobject import SQLObjectNotFound, IN
import turbolucene
from turbolucene import *

wikiwords = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")

def make_document(page):
    """Turn page into a TurboLucene document."""
    document = Document()
    document.add(Field('id', str(page.id), STORE, UN_TOKENIZED))
    document.add(Field('pagename', page.pagename, STORE, UN_TOKENIZED))
    document.add(Field('data', page.data, COMPRESS, TOKENIZED))
    return document

def results_formatter(results):
    """Return the pages that match the ids provided by TurboLucene"""
    if results:
        return list(Page.select(IN(Page.q.id, [int(id) for id in results])))

turbolucene.start(make_document, results_formatter)

search_form = widgets.TableForm(submit_text=u'Search', fields=[
  widgets.TextField('query', label='')])

class Root(controllers.RootController):
    @expose(template="wiki20.templates.page")
    def index(self, pagename="FrontPage"):
        try:
            page = Page.byPagename(pagename)
        except SQLObjectNotFound:
            raise turbogears.redirect("notfound", pagename = pagename)
        content = publish_parts(page.data,
                                writer_name="html")['html_body']
        root = str(turbogears.url('/'))
        content = wikiwords.sub(r'<a href="%s\1">\1</a>' % root, content)
        return dict(data=content, page=page, search_form=search_form)

    @expose("wiki20.templates.edit")
    def notfound(self, pagename):
        page = Page(pagename=pagename, data="")
        turbolucene.add(page)
        return dict(page=page)

    @expose(template="wiki20.templates.edit")
    def edit(self, pagename):
        page = Page.byPagename(pagename)
        return dict(page=page)

    @expose("wiki20.templates.pagelist")
    @expose("json")
    def pagelist(self):
        pages = [page.pagename for page in Page.select(orderBy=Page.q.pagename)]
        return dict(pages=pages)

    @expose()
    def save(self, pagename, data, submit):
        page = Page.byPagename(pagename)
        page.data = data
        turbolucene.update(page)
        turbogears.flash("Changes saved!")
        raise turbogears.redirect("/%s" % pagename)

    @expose()
    def default(self, pagename):
        return self.index(pagename)

    @expose(template='wiki20.templates.search')
    def search(self, query=None):
        results = turbolucene.search(query)
        return dict(search_form=search_form, query=query, results=results)
