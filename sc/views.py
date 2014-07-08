import cherrypy
import datetime
import http.client
import jinja2
import newrelic.agent
import regex
import socket
import time
import json
import urllib.parse
from webassets.ext.jinja2 import AssetsExtension

import sc
from sc import assets, config, data_repo, scimm, util
from sc.menu import get_menu
from sc.scm import scm, data_scm
from sc.classes import Parallel, Sutta

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
        loader=jinja2.FileSystemLoader(str(sc.templates_dir)),
        extensions=[AssetsExtension],
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.assets_environment = assets.get_env()

    env.filters['date'] = util.format_date
    env.filters['time'] = util.format_time
    env.filters['datetime'] = util.format_datetime
    env.filters['timedelta'] = util.format_timedelta
    env.filters['uid_to_name'] = lambda uid: scimm.imm().uid_to_name(uid)

    def sub_filter(string, pattern, repl):
        return regex.sub(pattern, repl, string)
    env.filters['sub'] = sub_filter

    def sht_expansion(string):
        """Add links from SHT vol/page references to the sht-lookup page."""
        if 'SHT' in string:
            # Replace &nbsp; with spaces
            string = string.replace('&nbsp;', ' ')
            baseurl = '/sht-lookup/'
            def replacement(m):
                # Ignore 'also cf. ix p. 393ff' and ' A'
                first, second = m[1], m[2]
                if regex.match(r'.+p\.\s*', first) or \
                   regex.match(r'.+A', first):
                    return '{}{}'.format(first, second)
                else:
                    # replace n-dash with dash
                    path = second.replace('−', '-')
                    return '{}<a href="{}{}" target="_blank">{}</a>'.format(
                        first, baseurl, path, second)
            string = regex.sub(r'([^0-9]+)([0-9]{1,4}(?:\.?[\−\+0-9a-zA-Z]+)?)',
                replacement, string)
        return string
    env.filters['sht_expansion'] = sht_expansion

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

class ViewContext(dict):
    """A dictionary with easy object-style setters/getters.

    >>> context = ViewContext()
    >>> context['a'] = 1
    >>> context.b = 2
    >>> context
    {'a': 1, 'b': 2}
    """

    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value

class ViewBase:
    """The base class for all SuttaCentral views.

    Views must set or override the template_name property.

    Views can optionally define a setup_context() method that will be executed
    during the render() method.

    Views should assign the 'title' context variable so that the page will have
    a (reasonably) relavent title.
    """

    env = jinja2_environment()

    @property
    def template_name(self):
        """Return the template name for this view."""
        raise NotImplementedError('Views must define template_name')

    def get_template(self):
        """Return the Jinja2 template for this view."""
        return self.env.get_template(self.template_name + ".html")

    def setup_context(self, context):
        """Optional method for subclasses to assign additional context
        variables. This is executed during the render() method. The context
        variable is a dictionary with magic setters (see ViewContext)."""
        pass

    def get_global_context(self):
        """Return a dictionary of variables accessible by all templates."""
        nonfree_fonts = config.nonfree_fonts
        if cherrypy.request.offline:
            if not config.always_nonfree_fonts:
                nonfree_fonts = False
                
        return ViewContext({
            'menu': get_menu(),
            'config': config,
            'current_datetime': datetime.datetime.now(),
            'development_bar': config.development_bar,
            'newrelic_browser_timing': NewRelicBrowserTimingProxy(),
            'nonfree_fonts': nonfree_fonts,
            'offline': cherrypy.request.offline,
            'page_lang': 'en',
            'scm': scm,
            'search_query': '',
            'imm': sc.scimm.imm(),
        })

    def massage_whitespace(self, text):
        return regex.sub(r'\n[ \n\t]+', r'\n', text)

    def render(self):
        """Return the HTML for this view."""
        template = self.get_template()
        context = self.get_global_context()
        self.setup_context(context)
        return self.massage_whitespace(template.render(dict(context)))

class InfoView(ViewBase):
    """A simple view that renders the template page_name; mostly used for
    static pages."""

    def __init__(self, page_name):
        self.page_name = page_name
    
    @property
    def template_name(self):
        return self.page_name

    def setup_context(self, context):
        if self.page_name != 'home':
            title = self.page_name.replace('_', ' ').capitalize()
            if title == 'Contacts':
                title = 'People'
            context.title = title

class DownloadsView(InfoView):
    """The view for the downloads page."""

    formats = ['zip', '7z']

    def __init__(self):
        super().__init__('downloads')

    def setup_context(self, context):
        super().setup_context(context)
        context.offline_data = self.__offline_data()

    def __file_data(self, basename, exports_path):
        data = []
        
        for latest_path in sorted(exports_path.glob('*-latest.*')):
            if latest_path.suffix.lstrip('.') not in self.formats:
                continue
            #latest_filename = '{}-latest.{}'.format(basename, format)
            #latest_path = exports_path / latest_filename
            #if latest_path.exists():
            local_path = latest_path.resolve()
            relative_url = local_path.relative_to(sc.static_dir)
            data.append({
                'filename': local_path.name,
                'url': '/{}'.format(relative_url),
                'time': local_path.stat().st_ctime,
                'size': local_path.stat().st_size,
                'format': format,
            })
        return data

    def __offline_data(self):
        return self.__file_data('sc-offline', sc.exports_dir)

class ParallelView(ViewBase):
    """The view for the sutta parallels page."""

    template_name = 'parallel'

    def __init__(self, sutta):
        self.sutta = sutta

    def setup_context(self, context):
        context.title = "{}: {}".format(
            self.sutta.acronym, self.sutta.name)
        context.sutta = self.sutta

        # Add the origin to the beginning of the list of 
        # parallels. The template will display this at the
        # top of the list with a different style.
        origin = Parallel(sutta=self.sutta, partial=False, footnote="", indirect=False)
        
        # Get the information for the table footer.
        has_alt_volpage = False
        has_alt_acronym = False

        for parallel in self.sutta.parallels:
            if parallel.negated:
                continue
            if parallel.sutta.alt_volpage_info:
                has_alt_volpage = True
            if parallel.sutta.alt_acronym:
                has_alt_acronym = True
        
        # Add data specific to the parallel page to the context.
        context.origin = origin
        context.has_alt_volpage = has_alt_volpage
        context.has_alt_acronym = has_alt_acronym
        context.citation = SuttaCitationView(self.sutta).render()

class VinayaParallelView(ParallelView):
    template_name = 'vinaya_parallel'

class TextView(ViewBase):
    """The view for showing the text of a sutta or tranlsation."""

    template_name = 'text'

    # Extract the (non-nestable) hgroup element using regex, DOTALL
    # and non-greedy matching makes this straightforward.
    content_regex = regex.compile(r'''
        <body[^>]*>
        (?<content>.*)
        </body>
        ''', flags=regex.DOTALL | regex.VERBOSE)
    
    # Note: Links come after section
    links_regex = regex.compile(r'class="(?:next|previous)"')
    
    def __init__(self, uid, lang_code):
        self.uid = uid
        self.lang_code = lang_code

    def setup_context(self, context):
        from sc.tools import html
        m = self.content_regex.search(self.get_html())
        m.detach_string() # Free up memory now.
        imm = scimm.imm()
        
        context.sutta = imm.suttas.get(self.uid)
        context.division = imm.divisions.get(self.uid)
        
        context.textdata = textdata = imm.get_text_data(self.uid, self.lang_code)
        context.title = textdata.name if textdata else '?'
        context.text = m['content']
        # Eliminate newlines from Full-width-glyph languages like Chinese
        # because they convert into spaces when rendered.
        # TODO: This check should use 'language' table
        if self.lang_code in {'zh'}:
            context.text = self.massage_cjk(context.text)
        context.lang_code = self.lang_code
        
    @property
    def path(self):
        relative_path = scimm.imm().text_path(self.uid, self.lang_code)
        if not relative_path:
            return None
        return sc.text_dir / relative_path
    
    def get_html(self):
        """Return the text HTML or raise a cherrypy.NotFound exception"""
        if self.path:
            with self.path.open('r', encoding='utf-8') as f:
                return f.read()
        else:
            raise cherrypy.NotFound()

    def text_json(self):
        # Put some useful information for javascript into a script field
        # The absolute path relative to the domain
        imm = scimm.imm()
        sutta = imm.suttas.get(self.uid)
        if sutta:
            subdivision = sutta.subdivision
            division = subdivision.division
            root_lang = sutta.lang.uid
        else:
            division = imm.divisions.get(self.uid)
            subdivision = None
            sutta = None
            

        if not subdivision:
            subdiv_uid = self.uid
            while subdiv_uid and not subdivision:
                if subdiv_uid in imm.subdivisions:
                    subdivision = imm.subdivisions[subdiv_uid]
                    division = subdivision.division
                    break
                subdiv_uid = subdiv_uid[:-1]
            else:
                subdivision = None

        root_lang = division.collection.lang.uid
        
        out = {'lang_code':self.lang_code,
        'uid': self.uid,
        'sutta_uid': sutta.uid if sutta else None,
        'subdivision_uid': subdivision.uid if subdivision else None,
        'division_uid': division.uid if division else None,
        'all_lang_codes': list(imm.tim.get(uid=self.uid)),
        'root_lang_code': root_lang,
        }

        return json.dumps(out, ensure_ascii=False, sort_keys=True)
    
    @staticmethod
    def massage_cjk(text):
        def deline(string):
            return string.replace('\n', '').replace('<p', '\n<p')
        
        m = regex.match(r'(?s)(.*?)(<div[^>]+id="metaarea".*?</div>)(.*)', text)
        if m or not m:
            pre, meta, post = m[1:]
            return ''.join([deline(pre), meta, deline(post)])
        return deline(text)
    
class SuttaView(TextView):
    """The view for showing the sutta text in original sutta langauge."""

    def __init__(self, sutta, lang):
        super().__init__(sutta.uid, lang.uid)
        self.sutta = sutta
        self.lang = lang

    def setup_context(self, context):
        super().setup_context(context)
        context.title = '{}: {} ({}) - {}'.format(
            self.sutta.acronym, context.title, self.lang.name,
            self.subdivision.name)
        context.sutta_lang_code = self.sutta.lang.iso_code

    @property
    def subdivision(self):
        subdivision = self.sutta.subdivision
        if subdivision.name is None:
            return subdivision.division
        else:
            return subdivision

class PitakaView(ViewBase):
    template_name = 'pitaka'

    def __init__(self, pitaka):
        self.pitaka = pitaka

    def setup_context(self, context):
        context.pitaka = self.pitaka
        

class DivisionView(ViewBase):
    """Thew view for a division."""

    template_name = 'division'

    def __init__(self, division):
        self.division = division

    def setup_context(self, context):
        context.title = "{}: {}".format(self.division.acronym,
            self.division.name)
        context.division = self.division
        context.division_text_url = None
        if self.division.text_ref:
            context.division_text_url = self.division.text_ref.url
        context.has_alt_volpage = False
        context.has_alt_acronym = False

        for subdivision in self.division.subdivisions:
            for sutta in subdivision.suttas:
                if sutta.alt_volpage_info:
                    context.has_alt_volpage = True
                if sutta.alt_acronym:
                    context.has_alt_acronym = True

class SubdivisionView(ViewBase):
    """The view for a subdivision."""

    def __init__(self, subdivision):
        self.subdivision = subdivision

    template_name = 'subdivision'

    def setup_context(self, context):
        context.title = "{} {}: {} - {}".format(
            self.subdivision.division.acronym, self.subdivision.acronym,
            self.subdivision.name, self.subdivision.division.name)
        context.subdivision = self.subdivision
        context.has_alt_volpage = False
        context.has_alt_acronym = False

        for sutta in self.subdivision.suttas:
            if sutta.alt_volpage_info:
                context.has_alt_volpage = True
            if sutta.alt_acronym:
                context.has_alt_acronym = True

class SubdivisionHeadingsView(ViewBase):
    """The view for the list of subdivisions for a division."""

    template_name = 'subdivision_headings'

    def __init__(self, division):
        self.division = division

    def setup_context(self, context):
        context.title = "{}: {}".format(self.division.acronym,
            self.division.name)
        context.division = self.division

class SearchResultView(ViewBase):
    """The view for the search page."""

    template_name = 'search_result'

    def __init__(self, search_query, search_result):
        super().__init__()
        self.search_query = search_query
        self.search_result = search_result

    def setup_context(self, context):
        context.search_query = self.search_query
        context.title = 'Search: "{}"'.format(
            self.search_query)
        context.result = self.search_result
        context.imm = scimm.imm()

class AjaxSearchResultView(SearchResultView):
    """The view for /search?ajax=1."""

    template_name = 'ajax_search_result'

class ShtLookupView(ViewBase):
    """The view for the SHT lookup page."""

    template_name = 'sht_lookup'

    def __init__(self, query):
        self.sht_id = self.parse_first_id(query)
        if self.sht_id:
            self.redir_url = self.get_idp_url(self.sht_id)

    def parse_first_id(self, query):
        m = regex.match(r'^([0-9]{1,4}(?:\.?[0-9a-zA-Z]+)?)', query)
        if m:
            # replace . with /
            return m[1].replace('.', '/')
        else:
            return None

    def get_idp_url(self, sht_id):
        host = 'idp.bl.uk'
        path = '/database/oo_loader.a4d?pm=SHT%20{}'.format(
            urllib.parse.quote_plus(sht_id)
        )
        url = 'http://{}{}'.format(host, path)
        timeout = 1.0
        conn = http.client.HTTPConnection(host, timeout=timeout)
        try:
            conn.request('GET', path)
            response = conn.getresponse()
        except socket.timeout:
            logger.error('SHT Lookup {} timed out after {}s'.format(
                url, timeout))
            return False
        if response.status in [301, 302, 303]:
            location = response.headers['Location']
            if 'itemNotFound' not in location:
                return 'http://idp.bl.uk/database/' + location
            else:
                logger.info('SHT Lookup ID {} not found'.format(sht_id))
                return False
        else:
            logger.error('SHT Lookup {} returned unexpected response {}'.format(
                url, response.status))
            return False

    def setup_context(self, context):
        context.title = 'SHT Lookup {}'.format(self.sht_id)
        context.sht_id = self.sht_id
        context.redir_url = self.redir_url
        if self.redir_url:
            raise cherrypy.HTTPRedirect(self.redir_url, 302)

class SuttaCitationView(ViewBase):

    def __init__(self, sutta):
        self.sutta = sutta

    def get_template(self):
        return self.env.get_template('sutta_citation.txt')

    def setup_context(self, context):
        context.sutta = self.sutta

class AdminIndexView(InfoView):
    """The view for the admin index page."""

    def __init__(self):
        super().__init__('admin')

    def setup_context(self, context):
        super().setup_context(context)
        context.data_last_update_request = data_repo.last_update()
        context.data_scm = data_scm
        context.imm_build_time = scimm.imm().build_time

class UidsView(InfoView):
    
    def __init__(self):
        super().__init__('uids')
    
    def setup_context(self, context):
        imm = scimm.imm()
        context.imm = imm
        atoz = ''.join(chr(97 + i) for i in range(0, 26))
        alltwo = set(a + b for a in atoz for b in atoz)
        used = set()
        for uid in imm.divisions:
            used.update(uid.split('-'))
        
        for uid in imm.languages:
            used.update(uid.split('-'))
        
        for uid in imm.subdivisions:
            used.update(uid.split('-'))
        
        unused = alltwo - used
        
        context.unused = sorted(unused)
        context.used = sorted(u for u in used if u.isalpha())
        context.atoz = atoz
