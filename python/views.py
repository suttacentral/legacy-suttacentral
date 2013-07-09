from menu import menu_data
from classes import Parallel, Sutta
from jinja2 import Environment, FileSystemLoader

import config, regex

# The base class for all SuttaCentral views.
class ViewBase:
    def __init__(self):
        # Subclasses use this object to obtain templates.
        self.env = Environment(loader=FileSystemLoader(config.templates_root))

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

    def makeContext(self):
        ViewBase.makeContext(self)
        import os.path

        filename = os.path.join(config.text_root, self.lang, self.uid) + '.html'
        try:
            f = open(filename, 'r', encoding='utf-8')
        except OSError:
            try:
                url = scdb.getDBR().suttas[uid].url
                m = regex.search(r'/([^/]*)/([^/]*)/([^/]*)', url)
                filename = os.path.join(config.text_root, lang, m[1]) + '.html'
                if os.path.exists(filename):
                    cherrypy.lib.cptools.redirect(url=url, internal=False)
                else:
                    raise OSError('File not found')
            except OSError:
                raise cherrypy.HTTPError(501, "That url is theoretically valid, \
                                            but we don't have an original or translation \
                                            available in that language.")
            
        text = regex.search(r'(?mx)<body[^>]*>(.*)</body>', f.read(),
                            regex.MULTILINE + regex.DOTALL)[1]
        f.close()
        
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
