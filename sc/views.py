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
import sc.search.query

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
    env.filters['max'] = max
    env.filters['min'] = min
    env.filters['datetime'] = util.format_datetime
    env.filters['timedelta'] = util.format_timedelta
    env.filters['uid_to_name'] = lambda uid: scimm.imm().uid_to_name(uid)
    env.filters['uid_to_acro'] = lambda uid: scimm.imm().uid_to_acro(uid)

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
            'embed': 'embed' in cherrypy.request.params,
            'search_query': '',
            'no_index': False,
            'imm': sc.scimm.imm(),
            'ajax': 'ajax' in cherrypy.request.params,
            'cookies': {m.key: m.value for m in cherrypy.request.cookie.values()}
        })

    def massage_whitespace(self, text):
        return regex.sub(r'\n[ \n\t]+', r'\n', text)

    def render(self):
        """Return the HTML for this view."""
        try:
            template = self.get_template()
        except jinja2.exceptions.TemplateSyntaxError as e:
            cherrypy.response.status = 500
            message = type(e).__name__ + ' : line {e.lineno} in {e.name}'.format(e=e)
            sourcelines = ["{:4} {}".format(i + 1, l) for i, l in
                            enumerate(sc.tools.html.escape(e.source).split('\n'))]
            sourcelines[e.lineno - 1] = '<strong>{}</strong>'.format(sourcelines[e.lineno - 1])
            traceback = ("<pre>{trace}</pre>" +
                "<p>{message}</p>").format(message=e.message, trace='<br>'.join(sourcelines[max(0, e.lineno-3):e.lineno+2]))
            cherrypy.response.headers['Traceback'] = traceback
            raise cherrypy.HTTPError(500, message)
        context = self.get_global_context()
        self.setup_context(context)
        return self.massage_whitespace(template.render(dict(context)))
"""
['__cause__', '__class__', '__context__', '__delattr__', '__dict__',
'__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__',
'__gt__', '__hash__', '__init__', '__le__', '__lt__', '__module__', '__ne__',
'__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__',
'__setstate__', '__sizeof__', '__str__', '__subclasshook__',
'__suppress_context__', '__traceback__', '__weakref__',
'args', 'filename', 'lineno', 'message', 'name', 'source',
'translated', 'with_traceback']

"""
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

    file_prefixes = ['sc-offline']

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
            if latest_path.exists():
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
    
    def __init__(self, uid, lang_code, canonical=True):
        self.uid = uid
        self.lang_code = lang_code
        self.canonical = canonical

    def setup_context(self, context):
        from sc.tools import html
        m = self.content_regex.search(self.get_html())
        m.detach_string() # Free up memory now.
        imm = scimm.imm()

        context.uid = self.uid
        context.sutta = imm.suttas.get(self.uid)
        context.division = imm.divisions.get(self.uid)
        context.canonical = self.canonical
        
        context.textdata = textdata = imm.get_text_data(self.uid, self.lang_code)
        context.title = textdata.name if textdata else '?'
        context.text = m['content']
        if context.embed:
            context.text = self.shorter_text(context.text)
        context.has_quotes = '‘' in context.text or '“' in context.text
        try:
            context.snippet = self.get_snippet(context.text)
        except Exception as e:
            logger.error('Failed to generated snippet for {} ({})'.format(self.uid, str(e)))
            context.snippet = ''
        # Eliminate newlines from Full-width-glyph languages like Chinese
        # because they convert into spaces when rendered.
        # TODO: This check should use 'language' table
        if self.lang_code in {'zh'}:
            context.text = self.massage_cjk(context.text)
        context.lang_code = self.lang_code

        context.text_refs = []
        if context.sutta:
            if context.sutta.text_ref:
                context.text_refs.append(context.sutta.text_ref)
            context.text_refs.extend(context.sutta.translations)
            
        elif context.division:
            if context.division.text_ref:
                context.text_refs.append(context.division.text_ref)
            #context.text_refs.extend(context.division.translations)
    
    def shorter_text(self, html, target_len=2500):
        # Don't bother cutting off excessively short amount of text
        if len(html) < target_len * 1.5:
            return html
        root = sc.tools.html.fromstring(html[:target_len])
        pees = root.select('article > *')
        if len(pees) > 1:
            to_drop = pees[-1]
            if to_drop.getparent().tag == 'blockquote':
                to_drop = to_drop.getparent()
            bookmark = to_drop.get('id')
            if not bookmark and len(to_drop) > 0:
                bookmark = to_drop[0].get('id')
            else:
                for e in root.iter():
                    if e.get('id'):
                        bookmark = e.get('id')
                    if e == to_drop or e.getnext() == to_drop:
                        break
            to_drop.drop_tree()
        root.select('article')[-1].append(sc.tools.html.fromstring(
            '<p><a href="{href}">…continue reading…</a>'.format(
                href='http://suttacentral.net/{}/{}#{}'.format(
                    self.lang_code, self.uid, bookmark))))
        return sc.tools.html.tostring(root, encoding='unicode')
    
    def get_snippet(self, html, target_len=500):
        root = sc.tools.html.fromstring(html[:target_len + 2000])
        for e in root.cssselect('.hgroup'):
            e.drop_tree()
        article = root.cssselect('article')[0]
        parts = []
        total_len = 0
        for e in article:
            if e.tag not in {'p', 'blockquote'}:
                continue
            text = e.text_content()
            parts.append(text)
            total_len += len(text)
            if total_len > target_len:
                break

        text = '   '.join(parts)
        if len(text) > target_len:
            text = text[:target_len] + ' …'
        return text
        
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
    
    @staticmethod
    def massage_cjk(text):
        def deline(string):
            return string.replace('\n', '').replace('<p', '\n<p')
        
        m = regex.match(r'(?s)(.*?)(<aside[^>]+id="metaarea".*?</aside>)(.*)', text)
        if m or not m:
            pre, meta, post = m[1:]
            return ''.join([deline(pre), meta, deline(post)])
        return deline(text)

class TextSelectionView(TextView):
    template_name = 'paragraph'
    
    def __init__(self, uid, lang_code, targets):
        self.uid = uid
        self.lang_code = lang_code
        self.targets = targets

    def setup_context(self, context):
        context.selection = self.extract_selection()
    
    def extract_selection(self):
        from sc.tools import html
        targets = self.targets
        root = html.fromstring(self.get_html())
        id_map = root.id_map()
        elements = root.cssselect('article > *:not(div), article > div.hgroup, article > div:not(.hgroup) > *');
        results = []
        for target in targets.split('+'):
            
            m = regex.match(r'(\d+)(?:\.(\d+)-(\d+))?', target)
            
            target_id = int(m[1])
            char_start = None if m[2] is None else int(m[2])
            char_end = None if m[3] is None else int(m[3])
            
            target_element = elements[target_id]
            if char_start is not None:
                pos = 0
                char_rex = regex.compile(r'\S')
                def inner_callback(m):
                    nonlocal pos, char_start, char_end
                    result = m[0]
                    pos += 1
                    if pos == char_end:
                        result = result + '__HLEND__'
                    if pos == char_start:
                        result = '__HLSTART__' + result
                    return result
                    
                def callback(text):
                    nonlocal pos
                    if pos > char_end:
                        return text
                    return char_rex.sub(inner_callback, text)

                target_element.each_text(callback)

            results.append(target_element)
        result_strings = []
        last = None
        for i, element in enumerate(results):
            if i > 0:
                if results[i - 1] != last:
                    result_strings.append('<p>…</p>')
            result_strings.append(str(element))
            last = element

        return '\n'.join(result_strings).replace('__HLSTART__', '<span class="marked">').replace('__HLEND__', '</span>')
        
    
class SuttaView(TextView):
    """The view for showing the sutta text in original sutta langauge."""

    def __init__(self, sutta, lang, canonical):
        super().__init__(sutta.uid, lang.uid, canonical)
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

class DefinitionView(ViewBase):
    """ The view used for dictionary definition pages """

    template_name = 'define'

    def __init__(self, term):
        self.term = term

    def setup_context(self, context):
        from sc.search import dicts
        context.no_index = True
        context.term = term = self.term
        context.title = "define: {}".format(self.term)
        entry = context.entry = dicts.get_entry(self.term)
        if entry:
            context.near_terms = dicts.get_nearby_terms(entry['number'])
        else:
            context.near_terms = []
        context.fuzzy_terms = dicts.get_fuzzy_terms(term)

class ElasticSearchResultsView(ViewBase):
    template_name = 'elasticsearch_results'

    def __init__(self, query, results, **kwargs):
        self.query = query
        self.results = results
        self.kwargs = kwargs

    def setup_context(self, context):
        context.query = self.query
        context.results = self.results
        context.limit = int(self.kwargs['limit'])
        context.total = self.results['hits']['total']
        context.offset = int(self.kwargs['offset'])
        
        context.search_languages = [lang for lang in
                                        sorted(context.imm.languages.values(),
                                            key=lambda l: int(l.search_priority))
                                        if context.imm.tim.exists(lang_uid=lang.uid)]
        context.query_lang = self.kwargs.get('lang')
        context.no_index = True
        
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

class SuttaInfoView(ViewBase):
    template_name = 'sutta_info'
    def __init__(self, uid, lang):
        self.uid = uid
        self.lang = lang

    def setup_context(self, context):
        imm = sc.scimm.imm()
        context.sutta = imm.suttas[self.uid]
        context.translation = None
        for tr in context.sutta.translations:
            if tr.url.startswith('http'):
                continue
            if tr.lang.uid == self.lang:
                context.translation = tr
                break
        
        context.lang = imm.languages[self.lang]
        parallels = [ll
                    for ll in context.sutta.parallels
                    if ll.sutta.get_translation(lang=context.lang)]
        context.full_parallels = [ll for ll in parallels if not ll.partial]
        context.partial_parallels = [ll for ll in parallels if ll.partial]
        context.base_url = sc.config.app['base_url']

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

class ErrorView(ViewBase):
    template_name = 'errors/error'
    
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.code = kwargs['status'][0:3]
        if self.code == '404':
            self.template_name = 'errors/404'
        if kwargs['message'] == 'Elasticsearch Not Available':
            self.template_name = 'errors/search_error'

    def setup_context(self, context):
        context.update(self.kwargs)
        context.request = cherrypy.request
        context.response = cherrypy.response
        context.production_environment = (
            config.newrelic_environment == 'production'
            and 'traceback' not in cherrypy.request.params)
