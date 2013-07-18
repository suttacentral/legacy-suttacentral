from menu import menu_data
from classes import Parallel, Sutta
from jinja2 import Environment, FileSystemLoader
from webassets.ext.jinja2 import AssetsExtension

import assets, config, logging, os.path, regex, scdb

logger = logging.getLogger(__name__)

# The base class for all SuttaCentral views.
class ViewBase:
    def __init__(self):
        # Subclasses use this object to obtain templates.
        self.env = Environment(
            loader=FileSystemLoader(config.templates_root),
            extensions=[AssetsExtension],
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.env.assets_environment = assets.env
        # Subclasses assign a template
        self.template = None

    # This makes the basic context that all pages need.
    def makeContext(self):
        self.context = {"page_lang": "en",
                        "collections": menu_data}

    # Combine template and context to produce an HTML page.
    def render(self):
        self.makeContext()
        return self.template.render(self.context)

# A simple view that injects some static text 
# between the header and footer.
class InfoView(ViewBase):
    def __init__(self, page_name):
        ViewBase.__init__(self)
    
        self.template = self.env.get_template(page_name + ".html")

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
        self.context["sutta"] = self.sutta
        self.context["parallels"] = parallels
        self.context["has_alt_volpage"] = has_alt_volpage
        self.context["has_alt_acronym"] = has_alt_acronym

class TextView(ViewBase):
    def __init__(self, uid, lang):
        ViewBase.__init__(self)
        self.uid = uid
        self.lang = lang
        self.template = self.env.get_template('text.html')

    @property
    def filename(self):
        return os.path.join(self.lang, self.uid) + '.html'

    @property
    def path(self):
        return os.path.join(config.text_root, self.filename)

    def get_file_content(self):
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                return f.read()
        except OSError:
            return False

    def try_alt_sutta_url(self):
        # TODO: Not sure if this code is valid or not...
        sutta = scdb.getDBR().suttas.get(self.uid)
        if sutta and sutta.url:
            logger.info('Found sutta {} without text view file {}'.format(
                sutta.uid, self.filename))
            m = regex.search(r'/([^/]*)/([^/]*)/([^/]*)', url)
            if m:
                alt_filename = os.path.join(config.text_root, lang, m[1]) + '.html'
                if os.path.exists(alt_filename):
                    logger.info(('Redirecting to alt sutta url {} for missing ' +
                        ' file {}').format(url, self.filename))
                    cherrypy.lib.cptools.redirect(url=url, internal=False)
            return False

    def makeContext(self):
        ViewBase.makeContext(self)
        content = self.get_file_content()
        if not content:
            self.try_alt_sutta_url()
            raise cherrypy.HTTPError(404,
                'No text with filename {}'.format(self.filename))

        text = regex.search(r'(?mx)<body[^>]*>(.*)</body>', content,
                            regex.MULTILINE + regex.DOTALL)[1]
        self.context["text"] = text

class DivisionView(ViewBase):
    def __init__(self, division):
        ViewBase.__init__(self)

        self.template = self.env.get_template('division.html')
        self.division = division

    def makeContext(self):
        ViewBase.makeContext(self)

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
        self.context["division"] = self.division

class SearchResultView(ViewBase):
    def __init__(self, search_result):
        ViewBase.__init__(self)
        self.template = self.env.get_template('search_result.html')
        self.search_result = search_result

    def makeContext(self):
        ViewBase.makeContext(self)

        self.context["result"] = self.search_result
        self.context["dbr"] = scdb.getDBR()

class AjaxSearchResultView(SearchResultView):
    def __init__(self, search_result):
        SearchResultView.__init__(self, search_result)

        self.template = self.env.get_template('ajax_search_result.html')

