from menu import menu_data
from classes import Parallel, Sutta
from jinja2 import Environment, FileSystemLoader
from webassets.ext.jinja2 import AssetsExtension

import assets, config, logging, os.path, regex, scdb
from cherrypy.lib.cptools import redirect as http_redirect
import cherrypy
import newrelic.agent
import regex

logger = logging.getLogger(__name__)

class NewRelicBrowserTimingProxy:
    """
        New Relic real user monitoring proxy. See:
        https://newrelic.com/docs/python/real-user-monitoring-in-python
    """

    @property
    def header(self):
        if config.newrelic_real_user_monitoring:
            return newrelic.agent.get_browser_timing_header()
        else:
            return ''

    @property
    def footer(self):
        if config.newrelic_real_user_monitoring:
            return newrelic.agent.get_browser_timing_footer()
        else:
            return ''

# The base class for all SuttaCentral views.
class ViewBase:
    # Subclasses use this object to obtain templates.
    env = Environment(
            loader=FileSystemLoader(config.templates_root),
            extensions=[AssetsExtension],
            trim_blocks=True,
            lstrip_blocks=True,
        )
    def __init__(self):
        self.env.assets_environment = assets.env
        # Subclasses assign a template
        self.template = None

    # This makes the basic context that all pages need.
    def makeContext(self):
        self.context = {
            "collections": menu_data,
            "newrelic_browser_timing": NewRelicBrowserTimingProxy(),
            "page_lang": "en",
            "search_query": ""
        }

    # Combine template and context to produce an HTML page.
    def render(self):
        self.makeContext()
        return self.template.render(self.context)

def sub(string, pattern, repl):
    return regex.sub(pattern, repl, string)
ViewBase.env.filters['sub'] = sub

# A simple view that injects some static text 
# between the header and footer.
class InfoView(ViewBase):
    def __init__(self, page_name):
        ViewBase.__init__(self)

        self.page_name = page_name
        self.template = self.env.get_template(page_name + ".html")

    def makeContext(self):
        ViewBase.makeContext(self)
        if self.page_name != 'home':
            title = self.page_name.replace('_', ' ').capitalize()
            if title == 'Contacts':
                title = 'People'
            self.context["title"] = title

# Given a Sutta object produces a Parallel page.
class ParallelView(ViewBase):
    def __init__(self, sutta):
        ViewBase.__init__(self)

        self.template = self.env.get_template('parallel.html')
        self.sutta = sutta
    
    def makeContext(self):
        ViewBase.makeContext(self)

        # Add the origin to the beginning of the list of 
        # parallels. The template will display this at the
        # top of the list with a different style.
        origin = Parallel(sutta=self.sutta, partial=False, footnote="", indirect=False)
        parallels = [origin] + self.sutta.parallels

        # Get the information for the table footer.
        has_alt_volpage = False
        has_alt_acronym = False

        for parallel in parallels:
            if parallel.sutta.alt_volpage_info:
                has_alt_volpage = True
            if parallel.sutta.alt_acronym:
                has_alt_acronym = True
        
        # Add data specific to the parallel page to the context.
        self.context["title"] = "{}: {}".format(
            self.sutta.acronym, self.sutta.name)
        self.context["sutta"] = self.sutta
        self.context["parallels"] = parallels
        self.context["has_alt_volpage"] = has_alt_volpage
        self.context["has_alt_acronym"] = has_alt_acronym

class TextView(ViewBase):
    def __init__(self, uid, lang_code):
        ViewBase.__init__(self)
        self.uid = uid
        self.lang_code = lang_code
        self.template = self.env.get_template('text.html')

    @property
    def filename(self):
        return os.path.join(self.lang_code, self.uid) + '.html'

    @property
    def path(self):
        return os.path.join(config.text_root, self.filename)

    def get_file_content(self):
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                return f.read()
        except OSError:
            return False

    def get_tag(self, content, tag):
        re = r'(?mx)<{}[^>]*>(.*)</{}>'.format(tag, tag)
        return regex.search(re, content, regex.MULTILINE | regex.DOTALL)[1]

    def makeContext(self):
        ViewBase.makeContext(self)
        content = self.get_file_content()
        if not content:
            raise cherrypy.NotFound()

        text = self.get_tag(content, 'body')
        self.context["text"] = text

class SuttaView(TextView):

    def __init__(self, sutta, lang, uid, lang_code):
        self.sutta = sutta
        self.lang = lang
        super().__init__(uid, lang_code)

    @property
    def subdivision(self):
        subdivision = self.sutta.subdivision
        if subdivision.uid.endswith('-nosub'):
            return subdivision.division
        else:
            return subdivision

    def makeContext(self):
        super().makeContext()
        self.context["title"] = "{}: {} ({}) - {}".format(
            self.sutta.acronym, self.sutta.name, self.lang.name,
            self.subdivision.name)

class DivisionView(ViewBase):
    def __init__(self, division):
        ViewBase.__init__(self)

        self.template = self.env.get_template('division.html')
        self.division = division

    def makeContext(self):
        ViewBase.makeContext(self)

        self.context["title"] = "{}: {}".format(self.division.acronym,
            self.division.name)
        self.context["has_alt_volpage"] = False
        self.context["has_alt_acronym"] = False

        for subdivision in self.division.subdivisions:
            for sutta in subdivision.suttas:
                if sutta.alt_volpage_info:
                    self.context["has_alt_volpage"] = True
                if sutta.alt_acronym:
                    self.context["has_alt_acronym"] = True

        self.context["division"] = self.division

class SubdivisionView(ViewBase):
    def __init__(self, subdivision):
        ViewBase.__init__(self)

        self.template = self.env.get_template('subdivision.html')
        self.subdivision = subdivision

    def makeContext(self):
        ViewBase.makeContext(self)

        self.context["title"] = "{} {}: {} - {}".format(
            self.subdivision.division.acronym, self.subdivision.acronym,
            self.subdivision.name, self.subdivision.division.name)
        self.context["has_alt_volpage"] = False
        self.context["has_alt_acronym"] = False

        for sutta in self.subdivision.suttas:
            if sutta.alt_volpage_info:
                self.context["has_alt_volpage"] = True
            if sutta.alt_acronym:
                self.context["has_alt_acronym"] = True

        self.context["subdivision"] = self.subdivision

class SubdivisionHeadingsView(ViewBase):
    def __init__(self, division):
        ViewBase.__init__(self)

        self.template = self.env.get_template('subdivision_headings.html')
        self.division = division

    def makeContext(self):
        ViewBase.makeContext(self)
        self.context["title"] = "{}: {}".format(self.division.acronym,
            self.division.name)
        self.context["division"] = self.division

class SearchResultView(ViewBase):
    def __init__(self, search_query, search_result):
        ViewBase.__init__(self)
        self.template = self.env.get_template('search_result.html')
        self.search_query = search_query
        self.search_result = search_result

    def makeContext(self):
        ViewBase.makeContext(self)

        self.context["search_query"] = self.search_query
        self.context["title"] = 'Search: "{}"'.format(
            self.search_query)
        self.context["result"] = self.search_result
        self.context["dbr"] = scdb.getDBR()

class AjaxSearchResultView(SearchResultView):
    def __init__(self, search_query, search_result):
        SearchResultView.__init__(self, search_query, search_result)

        self.template = self.env.get_template('ajax_search_result.html')

