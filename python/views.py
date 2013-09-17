import babel.dates, cherrypy, jinja2, newrelic.agent, os.path, regex, time
from webassets.ext.jinja2 import AssetsExtension

import assets, config, scdb
from menu import menu_data
from classes import Parallel, Sutta

import logging
logger = logging.getLogger(__name__)

__jinja2_environment = None
def jinja2_environment():
    """Return the Jinja2 environment singleton used by all views.
    
    For information on Jinja2 custom filters, see
    http://jinja.pocoo.org/docs/api/#custom-filters
    """

    global __jinja2_environment
    if __jinja2_environment:
        return __jinja2_environment

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(config.templates_root),
        extensions=[AssetsExtension],
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.assets_environment = assets.env

    def datetime_filter(value, format='short', locale='en_AU'):
        return babel.dates.format_datetime(value,
            format=format, locale=locale)
    env.filters['datetime'] = datetime_filter

    def sub_filter(string, pattern, repl):
        return regex.sub(pattern, repl, string)
    env.filters['sub'] = sub_filter

    __jinja2_environment = env
    return env

class NewRelicBrowserTimingProxy:
    """New Relic real user monitoring proxy.
    
    See: https://newrelic.com/docs/python/real-user-monitoring-in-python
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

class ViewBase:
    """The base class for all SuttaCentral views.

    Views must define a get_template() method that should return a Jinja2
    template.

    Views can optionally define a setup_context() method that will be executed
    during the render() method.

    The context property is a dictionary of template accessible variables.

    Views should assign the 'title' context variable so that the page will have
    a (reasonably) relavent title.
    """

    env = jinja2_environment()

    def get_template(self):
        """Returns the Jinja2 template for this view."""
        raise NotImplementedError()

    def setup_context(self, context):
        """Optional method for subclasses to assign additional context
        variables. This is executed during the render() method."""
        pass

    def get_global_context(self):
        """Return a dictionary of variables accessible by all templates."""
        return {
            'collections': menu_data,
            'newrelic_browser_timing': NewRelicBrowserTimingProxy(),
            'offline': cherrypy.request.offline,
            'page_lang': 'en',
            'search_query': '',
        }

    def render(self):
        """Return the HTML for this view."""
        template = self.get_template()
        context = self.get_global_context()
        self.setup_context(context)
        return template.render(context)

class InfoView(ViewBase):
    """A simple view that renders the template page_name; mostly used for
    static pages."""

    def __init__(self, page_name):
        self.page_name = page_name

    def get_template(self):
        return self.env.get_template(self.page_name + ".html")

    def setup_context(self, context):
        if self.page_name != 'home':
            title = self.page_name.replace('_', ' ').capitalize()
            if title == 'Contacts':
                title = 'People'
            context['title'] = title

class DownloadsView(InfoView):
    """The view for the downloads page."""

    formats = ['zip', '7z']

    def __init__(self):
        super().__init__('downloads')

    def setup_context(self, context):
        super().setup_context(context)
        context['offline_data'] = self.__offline_data()
        context['db_data'] = self.__db_data()

    def __file_data(self, basename, exports_path):
        data = []
        for format in self.formats:
            latest_filename = '{}-latest.{}'.format(basename, format)
            latest_path = os.path.join(exports_path, latest_filename)
            local_path = os.path.realpath(latest_path)
            logger.debug(latest_path)
            if os.path.exists(local_path):
                data.append({
                    'filename': os.path.basename(local_path),
                    'url': local_path[len(config.static_root):],
                    'time': os.path.getctime(local_path),
                    'size': os.path.getsize(local_path),
                    'format': format,
                })
        return data

    def __offline_data(self):
        return self.__file_data('sc-offline', config.exports_root)

    def __db_data(self):
        return self.__file_data('sc-db', config.exports_root)

class ParallelView(ViewBase):
    """The view for the sutta parallels page."""

    def __init__(self, sutta):
        self.sutta = sutta

    def get_template(self):
        return self.env.get_template('parallel.html')

    def setup_context(self, context):
        context['title'] = "{}: {}".format(
            self.sutta.acronym, self.sutta.name)
        context['sutta'] = self.sutta

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
        context['parallels'] = parallels
        context['has_alt_volpage'] = has_alt_volpage
        context['has_alt_acronym'] = has_alt_acronym

class TextView(ViewBase):
    """The view for showing the text of a sutta or tranlsation."""

    def __init__(self, uid, lang_code):
        self.uid = uid
        self.lang_code = lang_code

    def get_template(self):
        return self.env.get_template('text.html')

    def setup_context(self, context):
        # TODO: Figure out title
        content = self.get_file_content()
        if not content:
            raise cherrypy.NotFound()
        context['text'] = self.get_tag(content, 'body')

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

class SuttaView(TextView):
    """The view for showing the sutta text in original sutta langauge."""

    def __init__(self, sutta, lang, uid, lang_code):
        super().__init__(uid, lang_code)
        self.sutta = sutta
        self.lang = lang

    def setup_context(self, context):
        super().setup_context(context)
        context['title'] = '{}: {} ({}) - {}'.format(
            self.sutta.acronym, self.sutta.name, self.lang.name,
            self.subdivision.name)
        context['sutta_lang_code'] = self.lang_code

    @property
    def subdivision(self):
        subdivision = self.sutta.subdivision
        if subdivision.uid.endswith('-nosub'):
            return subdivision.division
        else:
            return subdivision

class DivisionView(ViewBase):
    """Thew view for a division."""

    def __init__(self, division):
        self.division = division

    def get_template(self):
        return self.env.get_template('division.html')

    def setup_context(self, context):
        context['title'] = "{}: {}".format(self.division.acronym,
            self.division.name)
        context['division'] = self.division
        context['has_alt_volpage'] = False
        context['has_alt_acronym'] = False

        for subdivision in self.division.subdivisions:
            for sutta in subdivision.suttas:
                if sutta.alt_volpage_info:
                    context['has_alt_volpage'] = True
                if sutta.alt_acronym:
                    context['has_alt_acronym'] = True


class SubdivisionView(ViewBase):
    """The view for a subdivision."""

    def __init__(self, subdivision):
        self.subdivision = subdivision

    def get_template(self):
        return self.env.get_template('subdivision.html')

    def setup_context(self, context):
        context['title'] = "{} {}: {} - {}".format(
            self.subdivision.division.acronym, self.subdivision.acronym,
            self.subdivision.name, self.subdivision.division.name)
        context['subdivision'] = self.subdivision
        context['has_alt_volpage'] = False
        context['has_alt_acronym'] = False

        for sutta in self.subdivision.suttas:
            if sutta.alt_volpage_info:
                context['has_alt_volpage'] = True
            if sutta.alt_acronym:
                context['has_alt_acronym'] = True

class SubdivisionHeadingsView(ViewBase):
    """The view for the list of subdivisions for a division."""

    def __init__(self, division):
        self.division = division

    def get_template(self):
        return self.env.get_template('subdivision_headings.html')

    def setup_context(self, context):
        context['title'] = "{}: {}".format(self.division.acronym,
            self.division.name)
        context['division'] = self.division

class SearchResultView(ViewBase):
    """The view for the search page."""

    def __init__(self, search_query, search_result):
        super().__init__()
        self.search_query = search_query
        self.search_result = search_result

    def get_template(self):
        return self.env.get_template('search_result.html')

    def setup_context(self, context):
        context['search_query'] = self.search_query
        context['title'] = 'Search: "{}"'.format(
            self.search_query)
        context['result'] = self.search_result
        context['dbr'] = scdb.getDBR()

class AjaxSearchResultView(SearchResultView):
    """The view for /search?ajax=1."""

    def get_template(self):
        return self.env.get_template('ajax_search_result.html')
