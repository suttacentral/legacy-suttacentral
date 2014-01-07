""" Sutta Central HTML Text Processing Tools 

These tools are segregated because in a certain sense they have
nothing to do with the suttas. In fact they could make a legitimate 
standalone web application.



"""

MAX_ARCHIVE_SIZE = 50 * 1000 * 1000 # Size in bytes when uncompressed.
MAX_FILE_SIZE = 20 * 1000 * 1000    # Size in bytes when uncompressed.
# These are generous maximums considering our collection was 60mb at time of
# writing this comment. The largest individual file I could find was 11mb,
# inside an odt file of the Thai tipitika.
# These maximums are mainly to protect against zip-bombs (i.e. compressing
# a bazillion zeroes to try and wipe out the servers memory when unzipped)
# At present a maximum of 2-3x MAX_FILE_SIZE memory might be used when 
# processing an archive.
# However timeouts also have to be considered. If someone has downloaded
# the internet and wants us to process it, it needs to be refused or time out.

MAX_RETRIVE_AGE = 900   # time in seconds.
# How long the users result zip will be kept alive for before being valid
# targets for garbage collection. May live for longer.

import random, pathlib, datetime, logging, io, regex, os

from cherrypy import expose, HTTPError
from cherrypy.lib.static import serve_file
from collections import OrderedDict
from zipfile import ZipFile, ZIP_DEFLATED, is_zipfile, ZipInfo
from time import time as current_time
from tempfile import TemporaryFile, NamedTemporaryFile
from bs4 import UnicodeDammit
from subprocess import Popen, PIPE, call

import sc
from sc.views import InfoView
from sc.util import humansortkey
from . import html, crumple, finalizer
from .emdashar import Emdashar, SortedLogger

logger = logging.Logger(__name__)


tidy_level = OrderedDict((
    ("minimal", "--doctype html5 --output-html 1 --replace-color 1\
    --tidy-mark 0 --quiet 1 --drop-proprietary-attributes 1 \
    --output-encoding utf8"),
    
    ("moderate", "--clean 1 --join-classes 1 --join-styles 1 \
    --merge-divs 1 --merge-spans 1"),
    
    ("merciless", "-gdoc")
    ))

tidy_options = {
    'tidy-nolinewrap': '-w 0',
    'tidy-logicalemphasis': '--logical-emphasis 1',
    'tidy-force': '--force-output 1'}
    
# There are probably stock version of these formatting functions
# but as usual I don't have internet right now.
def humansize(size_in_bytes):
    size = size_in_bytes
    for sizesfx in ('b', 'kb', 'mb', 'gb', 'tb', 'pb'): # <- yes, pb is there.
        # Use decimal rather than binary because it formats better.
        if size >= 1000:
            size /= 1000
        else:
            break
    return "{:.3g}{}".format(size, sizesfx)

# format_timedelta almost cut the mustard but no ms precision
def humantime(seconds):
    if seconds < 0.1:
        out = '{}ms'.format(int(seconds * 1000))
    elif seconds > 60:
        m = int(seconds / 60)
        s = round(seconds - 60 * m)
        if (m > 59):
            out = '{}m'.format(m)
        else:
            out = '{}m {}s'.format(m, s)
    else:
        out = '{:.3g}s'.format(seconds)
    return out


def TempFile(infile=None):
    "Create a suitable temporary file"
    outfile = TemporaryFile()
    if infile and hasattr(infile, 'read'):
        outfile.writelines(infile)
        outfile.seek(0)
    return outfile
        

class Report(list):
    """ A report is generated per upload """
    class Entry:
        """ At least one Entry is generated per file.
        
        More than one entry may be generated per file, each operation
        may generate it's own entry.
        
        """
        summary = ''
        filename = ''
        messages = []
        errors = False
        warnings = False
        modified = False
        language = None
        
        def __init__(self):
            self.messages = []

        def __repr__(self):
            out = '<Report.Entry ' + self.summary + ' : '
            out += str(self.messages)
            if self.modified:
                out += ' (modified)'
            out += '>'
            return out
        
        def error(self, msg, lineno=None):
            self.errors = True
            self.messages.append(('error', msg, lineno))
        
        def warning(self, msg, lineno=None):
            self.warnings = True
            self.messages.append(('warning', msg, lineno))
        
        def info(self, msg, lineno=None):
            self.messages.append(('info', msg, lineno))
            
        def heading(self, msg, lineno=None):
            self.messages.append(('heading', msg, lineno))
    
    error = None # If error is set, something went badly wrong.
    title = ''
    header = ''
    footer = ''
    filename = ''
    result = None # Should be a simple filename
    processed_bytes = 0

    def __repr__(self):
        out = '<Report'
        if self.error:
            out += ' error: {} \n'.format(self.error)
        if self.title:
            out += ' title: {}\n'.format(self.title)
        if self.header:
            out += ' header: {}\n'.format(self.header)
        if self.footer:
            out += ' footer: {}\n'.format(self.footer)
        if len(self) > 0:
            out += ' contents: \n' + '\n'.join(repr(e) for e in self)
        out += '>\n'
        return out
    
    def __bool__(self):
        # A Report is always truthy even if it contains not entries.
        return True

class ReportView(InfoView):
    def __init__(self, report):
        self.report = report
        super().__init__('tools/report')
        
    def setup_context(self, context):
        context.report = self.report
        pass

class ToolsView(InfoView):
    
    def __init__(self, template):
        super().__init__(template)
        
    def setup_context(self, context):
        context.tidy_level = tidy_level
        context.tidy_options = tidy_options

def monkeypatch_ZipExtFile():
    """ Fix 100% CPU infinite loop bug in zipfile.ZipExtFile.read
    
    A monkey patch seemed the best solution since as well as fixing
    the hang, it also raises an exception on corrupt input (read1 doesn't
    hang but silently returns corrupt binary data). The stdlib test_zipfile.py
    passes just the same with this patch applied.
    
    This is required to harden the server against zip bombs.
    
    """
    
    from zipfile import ZipExtFile, BadZipFile
    
    _read1_org = ZipExtFile._read1
    def _read1(self, n):
        data = _read1_org(self, n)
        if not data:
            self._eof = True
            self._update_crc(data)
        return data
    ZipExtFile._read1 = _read1

monkeypatch_ZipExtFile()

class ProcessingError(Exception):
    pass

class ProcessorError(Exception):
    pass

class BaseProcessor:
    """ The BaseProcessor attempts to implement all the zip and filehandling
    stuff so that derived classes only need to implement process_str,
    and perhaps process_bytes.
    
    As a rule the data is passed around, while the flow control for report 
    information and other little bits of information is far less well defined.
    
    """
    
    output_encoding = None # None = keep existing
    allowed_types = None # None = all allowed.
    
    
    def __init__(self, **kwargs):
        self.options = kwargs
        
    def output_filename(self, filename):
        """ This permits renamining the output file """
        return filename
    
    @property
    def name(self):
        raise NotImplementedError
        
    def init_report(self):
        report = Report()
        self.report = report
        self.starttime = current_time()
        report.title = "Applying {}".format(self.name)
        return report
    
    def finalize_report(self, resultfile):
        self.report.footer = "Complete in {}".format(humantime(
                                            current_time() - self.starttime))
        if self.report.processed_bytes > 0:
            self.report.result = resultfile
        
    def process_one(self, infile, filename):
        """ process a non-zipped file. Is this needed? """
        self.init_report()
        resultfile = Tools.make_return_file(filename)
        
        stat = os.stat(infile.fileno)
        #Create a fake zipinfo
        zi = ZipInfo(filename=filename)
        zi.file_size = stat.st_size
        data = self.process_file(infile)
        resultfile.write(data)
        self.finalize_report(resultfile)
        return report        
    
    type_map = {'.txt': 'process_txt',
                '.xml': 'process_xml',
                '.xhtml': 'process_html',
                '.html': 'process_html',
                '.htm': 'process_html',
                '.epub': 'process_epub',
                '.odt': 'process_odt',
                '.sxw': 'process_odt'}
    
    def process_zip(self, inzipfile, filename):
        """ Process every file in a zip archive
        
        Returns a `Report` object containing information about what happened
        and a name which can be used to construct a url to the result zip.
        
        """
        
        report = self.init_report()
        
        if not is_zipfile(inzipfile):
            raise InputError("{} is not a valid zip archive.".format(filename))
        
        resultfile = Tools.make_return_file(filename)
        outzipfile = resultfile.fileobj
        
        with ZipFile(inzipfile, 'r') as inzip, \
            ZipFile(outzipfile, 'w', compression=ZIP_DEFLATED) as outzip:
            # By default filelist is sorted alphabetically, do numeric instead.
            inzip.filelist.sort(key=lambda zi: humansortkey(zi.filename))
            total_size = sum(zinfo.file_size for zinfo in inzip.filelist)
            report.header = "{} contains {} files, total {}.".format(filename, 
                                                        len(inzip.filelist),
                                                        humansize(total_size))
            
            if total_size > MAX_ARCHIVE_SIZE:
                raise ProcessorError("Archive too large. Maximum uncompressed size is {}.".format(humansize(MAX_ARCHIVE_SIZE)))
            
            self.preprocess_zip(inzip)
            
            for zinfo in inzip.filelist:
                data = self.process_file(inzip.open(zinfo, 'r'), zinfo)
                if data is None:
                    # This happens when an error occured.
                    continue
                if not hasattr(data, 'decode'):
                    # Under exceptional cirumstances, an iterable of new
                    # filedata is returned. This requires special handling.
                    for filename, filedata in data:
                        self.report.processed_bytes += len(filedata)
                        outzip.writestr(str(filename), filedata)
                else:
                    self.report.processed_bytes += len(data)
                    outzip.writestr(zinfo, data, compress_type=ZIP_DEFLATED)
        
        self.finalize_report(resultfile)
        return report
        
    def process_file(self, fileobj, zinfo, continue_on_error=False):
        if zinfo.file_size == 0:
            return b''
        entry = Report.Entry()
        self.entry = entry
        self.report.append(entry)
        
        entry.filename = pathlib.Path(zinfo.filename)
        entry.summary = "{}: {}".format(zinfo.filename, humansize(zinfo.file_size))
        if zinfo.file_size > MAX_FILE_SIZE:
            # This is probably malicious so we wont bend over backwards.
            entry.error("File too large. File must be no larger than {}.".format(humansize(MAX_FILE_SIZE)))
            return None
        
        suffix = pathlib.Path(zinfo.filename).suffix.lower()
        self.suffix = suffix
        
        try:
            fn = None
            
            if (self.allowed_types and suffix not in self.allowed_types 
                            and suffix[1:] not in self.allowed_types):
                entry.info("No instructions for {}".format(suffix))
            elif suffix in self.type_map:
                # Raises attribute error. Programmer should see.
                fn = getattr(self, self.type_map[suffix])
            else:
                entry.info("Unknown file, not processing")
            
            if fn == None:
                outdata = fileobj.read()
            else:
                fileobj = self.preprocess_file(fileobj)
                outdata = fn(fileobj)
            
        except ProcessingError as e:
            entry.error(str(e))
            return None
        
        zinfo.filename = self.output_filename(zinfo.filename)
        # Out is bytes at the moment. Due to how ZipFile works the alternative
        # would be to create a TemporaryFile, this is because ZipFile's write
        # method needs to know information like the data length, it thus 
        # requires the complete data, either as bytes, or a file.
        # Keeping it zipping around in memory seems expedient.
        return outdata
    
    def preprocess_zip(self, zipfile):
        "May examine the zip and alter zipfile.listlist"
        pass
    
    def preprocess_file(self, fileobj):
        return fileobj
    
    def process_txt(self, fileobj):
        raise NotImplementedError
    
    def process_html(self, fileobj):
        raise NotImplementedError
    
    def process_xml(self, fileobj):
        raise NotImplementedError
    
    def process_zipfmt(self, inzipfile, fn_map=None):
        """ Processes a format which is actually just a zip file
        
        This includes formats such as odt, epub, docx and many more, however
        fn_map must declare what contents are actually to be processed, since
        all these formats will have numerous non-content files in the archive.
        
        fn_map should be a dict or dict-like-object, for each
        file in inzip, process_zipfmt will first try fn_map.get(filename)
        then fn_map.get(suffix), if get(filename) returns a non-None falsey
        value (i.e. False) then the file is explicitly skipped even if the
        suffix check would have permitted it to be processed.
        
        Fancier criteria such as regex match or Path match can be implemented
        by passing in a custom class which defines 'get' and returns either a
        function or None.
        
        """
        
        if not fn_map:
            raise ValueError("Function map must be defined")
        
        entry = self.entry
        
        outzipfile = TempFile()
        try:
            inzipfile.seek(0)
        except io.UnsupportedOperation:
            # ZipFile requires a seekable stream
            inzipfile = TempFile(inzipfile)
        with ZipFile(inzipfile, 'r') as inzip,\
                ZipFile(outzipfile, 'w', ZIP_DEFLATED) as outzip:
            total_size = sum(zinfo.file_size for zinfo in inzip.filelist)
            entry.summary = '{}: {}'.format(entry.filename, humansize(total_size))
            for zinfo in inzip.filelist:
                if zinfo.file_size > MAX_FILE_SIZE:
                    self.entry.error("File too large. File must be no larger than {}.".format(humansize(MAX_FILE_SIZE)))
                    # probably malicious so an Error
                    raise ProcessingError
                zi_in_obj = inzip.open(zinfo, 'r')
                filename = zinfo.filename
                
                fn = fn_map.get(filename)
                if fn is None:
                    fn = fn_map.get(pathlib.Path(filename).suffix.lower())
                if fn:
                    zdata = fn(zi_in_obj)
                else:
                    # Everything else, just copy straight through.
                    zdata = zi_in_obj.read()
                outzip.writestr(zinfo, zdata)
        
        outzipfile.seek(0)
        return outzipfile.read()
    
    def process_odt(self, odt):
        """ Calls process_xml on content.xml inside the odt 
        
        .odt is pretty easy to work with using ZipFile, so it has been
        included as an option, as long as the xml structure isn't changed 
        (much) the document will come out just fine.
        
        """
        
        return self.process_zipfmt(odt, {'content.xml': self.process_xml})
    
    def process_epub(self, epub):
        """ Convert epub 
        
        I don't have the epub specification on hand but it seems that
        the content will be either html or xhtml files. However regardless
        of whether it calls them .html or .xhtml, they seem either way
        to be approximately polygot or xhtml markup.
        
        """
        
        return self.process_zipfmt(epub, {'.html': self.process_html, 
                                   '.xhtml': self.process_html})
    
    def process_bytes(self, data):
        # Default encoding is utf8. If another encoding is needed, 
        # the process_filetype method needs to handle that and call
        # process_str
        return self.process_str(data.decode()).encode(self.output_encoding)
    
    def process_str(self, string):
        raise NotImplementedError

class TextProcessor(BaseProcessor):
    """ Only process the text contents of the file, leaving markup alone 
    
    The derived class should implement process_str.
    """
    def process_txt(self, fileobj):
        return self.process_bytes(fileobj.read())
    
    def process_html(self, fileobj):
        doc = html.parse(fileobj)
        for e in doc.iter():
            if e.text:
                e.text = self.process_str(e.text)
        return lxml.html.tostring(doc, doctype=doc.docinfo.doctype, 
                                    encoding=self.output_encoding or doc.docinfo.encoding)
    
    def process_xml(self, fileobj):
        doc = lxml.etree.parse(fileobj)
        for e in doc.iter():
            if e.text:
                e.text = self.process_str(e.text)
        return lxml.etree.tostring(doc, xml_declaration=True, 
                                    doctype=doc.docinfo.doctype,
                                    encoding=self.output_encoding or doc.docinfo.encoding)

class CSXProcessor(TextProcessor):
    """ Attempts to convert CSX+ to UTF-8
    
    Works for both true CSX+, and UTF-8 resulting from treating
    CSX+ as Latin1.
    
    If the content isn't CSX+ it will mess things up, no effort
    is made to detect this condition.
    
    Does work okay with mixed proper UTF-8 and "CSX+ UTF-8"
    
    """
    output_encoding = "UTF-8"
    
    name = "CSX to UTF-8"
    def process_html(self, fileobj):
        return self.process_txt(fileobj)
    
    def process_xml(self, fileobj):
        return self.process_txt(fileobj)
    
    def process_bytes(self, data):
        try:
            string = data.decode('utf8')
        except UnicodeError:
            string = data.decode('latin1')
        return self.process_str(string).encode(self.output_encoding)
    
    def process_str(self, string):
        return string.translate(self._csx_to_utf8_tr)
    
    _csx_to_utf8_tr = str.maketrans(
                    'àâãäåæ\x83\x88\x8c\x93\x96çèéêëìíîïð¤¥ñòóôõö÷øùú§üýþÿ',
                    'āĀīĪūŪâêîôûṛṚṝṜḷḶḹḸṅṄñÑṭṬḍḌṇṆśŚṣṢṁṃṂḥḤ')

class DetwingleProcessor(BaseProcessor):
    """ Calls bs4.UnicodeDammit.detwingle
    
    Shouldn't cause any harm if the document is already UTF-8.
    
    """
    output_encoding = "UTF-8"
    
    name = "Detwingle"
    
    def process_txt(self, fileobj):
        return UnicodeDammit.detwingle(fileobj.read())
    
    def process_html(self, fileobj):
        return self.process_txt(fileobj)
    
    # There is not much point in trying to do XML since anything
    # which creates XML would already have re-encoded and detwingle
    # only works on "mixed encoded bytes".

class HTMLProcessor(BaseProcessor):
    "Inputs HTML/XHTML, outputs HTML5 with UTF-8 encoding"
    
    allowed_types = {'.htm', '.html', '.xhtml'}
    
    def output_filename(self, filename):
        return str(pathlib.Path(filename).with_suffix('.html'))
    
    def process_xml(self, fileobj):
        return self.process_html(fileobj)
    
    def process_html(self, fileobj):
        doc = html.parse(fileobj)
        root = doc.getroot()
        html.xhtml_to_html(doc) # This is very fast.
        self.process_root(root)
        
        return self.root_to_bytes(root)
    
    def root_to_bytes(self, root):
        root.headsure.insert(0, root.makeelement('meta', charset="UTF-8"))
        if not root.head.select('title'):
            root.head.append(root.makeelement('title'))
        root.attrib.clear()
        return root.pretty(doctype='<!DOCTYPE html>', 
                encoding='UTF-8', 
                include_meta_content_type=False).encode()
        
    def process_root(self, root):
        raise NotImplementedError
    
class CleanupProcessor(HTMLProcessor):
    
    name = "Cleanup"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode = self.options.get('cleanup')
    
    def preprocess_file(self, fileobj):
        """ Apply tidy as a preprocessor """
        
        if self.mode == 'descriptiveclasses':
            # Set special tidy flags.
            self.options['tidy-flags'] = crumple.tidy_flags
            
            return self.tidy(fileobj)
        
        elif self.mode == 'html5tidy':
            return self.tidy(fileobj)
        
        return fileobj
    
    def tidy(self, fileobj):
        """ Call tidy on a fileobj """
        
        tidy_cmd = self.options.get('tidy-flags', '').split()
        if not tidy_cmd:
            # Build command string manually here. This might
            # be needed if user has javascript disabled.
            target = self.options.get('tidy-level')
            if target is not None and target in tidy_level:
                for level, flags in tidy_level.items():
                    tidy_cmd += flags.split()
                    if level == target:
                        break
                
                for key in tidy_options:
                    if key in self.options:
                        tidy_cmd += tidy_options[key].split()
            else:
                raise ProcessingError('No Tidy level or unknown Tidy level')
        
        tidy_cmd = [sc.config.tidyprogram] + tidy_cmd
        
        entry = self.entry
        entry.heading("Running HTML5 Tidy")
        
        # tidy: 0 = no probs, 1 = warnings, 2 = errors, we don't care.
        try:
            with Popen(tidy_cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE) as tidy:
                out, errors = tidy.communicate(fileobj.read())
        except FileNotFoundError:
            raise ProcessorError("Tidy program not found!")
        
        for line in errors.decode(encoding='utf8').split('\n'):
            if 'Warning:' in line:
                entry.warning(line.replace('Warning: ', ''))
            elif 'Error:' in line:
                entry.error(line.replace('Error: ', ''))
        if entry.errors:
            entry.info('Fix errors and try again.')
            raise ProcessingError
        elif not entry.messages:
            entry.info("Tidy reported no problems")
        return io.BytesIO(out)
    
    def process_root(self, root):
        self.entry.info('Processing root')
        if 'cherrypick' in self.options:
            selector = self.options.get('cherrypick-css', '')
            target = root.select(selector)
            if not selector or len(target) == 0:
                raise ProcessingError("Content CSS Selector '{}' matched nothing. Body would be empty.".format(selector))
            root.body.clear()
            root.body.extend(target)
        
        if self.mode == 'descriptiveclasses':
            self.entry.heading('Generating Normalized Class Names')
            try:
                crumple.crumple(root, self.options)
            except Exception as e:
                self.entry.error('{} ({})'.format(type(e), e))
        
        if 'strip-header' in self.options:
            selector = self.options.get("strip-header-css", '')
            keep = root.select(selector)
            keep.extend(root.select('head .whitelist'))
            root.head.clear()
            root.head.extend(keep)
        
class FinalizeProcessor(HTMLProcessor):
    name = "Finalize"
    metadata = {}
    
    def output_filename(self, filename):
        filename = pathlib.Path(filename)
        if self.options.get('canonical-paths') and self.entry.language:
            p = finalizer.generate_canonical_path(self.entry.filename.stem, self.entry.language)
            if p:
                filename = p / filename.name
        
        return super().output_filename(filename)
    
    def preprocess_zip(self, zipfile):
        "Discover metadata and store in instance variable metadata"
        
        # We process any files named '*-meta.*', filtering them out.
        newlist = []
        for zi in zipfile.filelist:
            filepath = pathlib.Path(zi.filename)
            stem = filepath.stem.lower()
            dirpath = filepath.parent
            if stem.endswith('meta'):
                string = zipfile.open(zi).read().decode(encoding='UTF-8')
                root = html.fromstring(string)
                
                self.metadata[dirpath] = finalizer.process_metadata(root)
                entry = Report.Entry()
                self.report.append(entry)
                entry.summary = 'Metadata file: {}'.format(humansize(zi.file_size))
                entry.info('Will be applied to all files in {} folder'.format(str(dirpath)))
            else:
                newlist.append(zi)
        
        zipfile.filelist = newlist
    
    def process_html(self, fileobj):
        doc = html.parse(fileobj)
        html.xhtml_to_html(doc) # This is very fast.
        
        root = doc.getroot()
        
        sections = root.select('section')
        if len(sections) > 1:
            self.entry.info("Looks like file contains {} suttas".format(
                                                            len(sections)))
            # Multiple sutta mode.
            return self.process_many(root)
        
        # Single sutta mode.
        self.process_root(root)
        return self.root_to_bytes(root)
    
    def process_root(self, root):
        finalizer.finalize(root, entry=self.entry, options=self.options, 
            metadata=self.metadata.get(self.entry.filename.parent))
    
    def process_many(self, root):
        orgentry = self.entry
        orgroot = root
        try:
            metadata = root.select('div#metaarea')[0]
        except IndexError:
            metadata = self.metadata.get(self.entry.filename.parent)
        author_blurb = finalizer.discover_author(root, self.entry)
        es = root.select('section section')
        language = finalizer.discover_language(root, self.entry)
        
        if es:
            entry.error("File contains nested sections. Sections must not be nested.", lineno=es[0].sourceline)
            raise ProcessingError("Unable to proceed due to nested sections")
        for num, section in enumerate(root.select('section')):
            root = html.document_fromstring('<html><head><body>')
            root.body.append(section)
            entry = Report.Entry()
            try:
                entry.filename = pathlib.Path(section.attrib['id'])
            except KeyError:
                entry.error("Section has no 'id' attribute", lineno=section.sourceline)
                raise ProcessingError("With multiple suttas in one file, <section id=\"uid\"> notation must be used")
            self.report.append(entry)
            self.entry = entry
            entry.language = language
            
            finalizer.finalize(root, entry=entry, options=self.options, 
                metadata=metadata, language=language, author_blurb=author_blurb,
                num_in_file=num)
            entry.filename = pathlib.Path(root.select('section')[0].attrib['id']+ '.html') 
            
            filename = self.output_filename(orgentry.filename.parent / entry.filename)
            
            yield (filename, self.root_to_bytes(root))

class EmdasharProcessor(BaseProcessor):
    name = "Fix Puncutation"
    allowed_types = None
    def process_txt(self, fileobj):
        text = fileobj.read().decode()
        text = text.replace('\n\n', '<p>').replace('\n', '<br>')
        root = html.fromstring(text)
        self.process_root(root)
        text = str(html).replace('<p>', '\n\n').replace('<br>', '\n')
        return text.encode()
    
    def process_html(self, fileobj):
        doc = html.parse(fileobj)
        self.process_root(doc.getroot())
        return html.tostring(doc, doctype=doc.docinfo.doctype, 
                        encoding=self.output_encoding or doc.docinfo.encoding)
    
    def process_xml(self, fileobj):
        doc = html.parseXML(fileobj)
        self.process_root(doc.getroot())
        return html._etree.tostring(doc, xml_declaration=True, 
                        doctype=doc.docinfo.doctype or '<!DOCTYPE html>',
                        encoding=self.output_encoding or doc.docinfo.encoding)
    
    def process_root(self, root):
        self.entry.info('Applying Emdashar')
        
        if self.options.get('details'):
            logger = SortedLogger()
            logger.file = TemporaryFile('w+')
        else:
            logger = None
        dashar = Emdashar(logger=logger)
        
        for p in root.iter('p'):
            if p.text:
                p.text = p.text.lstrip()
            dashar.emdash(p)
            
        if self.options.get('details'):
            logger.flush()
            logger.file.seek(0)
            self.entry.info('Details of {} changes:'.format(logger.count))
            for line in logger.file:
                self.entry.info(line)

class Tools:
    """ Provide HTML/XML processing web services.
    
    Note that potential for denial of service is very high, since
    this module can do things like dynamically create files and consume
    gobs of cpu. The main consideration has been limiting memory use.
    
    Several countermeasures against zip bombs have been employed.
    
    """
    
    class ResultFile:
        " Used for delivery of results to user "
        def __init__(self, fileobj, name):
            self.fileobj = fileobj
            self.filename = name
            self.createtime = current_time()
        @property
        def url(self):
            return Tools.result_url(self.filename)
        
        @property
        def size(self):
            return humansize(os.stat(self.fileobj.fileno()).st_size)
        
    @expose()
    def index(self, **kwargs):
        return ToolsView('tools/about').render()
    
    @expose()
    def csx_reencode(self, **kwargs):
        return ToolsView('tools/reencode').render()
    
    @expose()
    def cleanup_bad_html(self, **kwargs):
        return ToolsView('tools/cleanup').render()
    
    @expose()
    def fix_punctuation(self, **kwargs):
        return ToolsView('tools/emdashar').render()
        
    @expose()
    def finalize_for_submission(self, **kwargs):
        return ToolsView('tools/finalize').render()

    @expose()
    def reencode(self, userfile, action=None, **kwargs):
        if action == 'csxplus':
            processor = CSXProcessor()
        elif action == 'detwingle':
            processor = DetwingleProcessor()
        else:
            raise HTTPError(404, "Invalid form parameters")
        
        report = processor.process_zip(userfile.file, userfile.filename)
        return ReportView(report).render()
    
    @expose()
    def finalize(self, userfile, **kwargs):
        processor = FinalizeProcessor(**kwargs)
        report = processor.process_zip(userfile.file, userfile.filename)
        return ReportView(report).render()
    
    @expose()
    def clean(self, userfile, **kwargs):
        processor = CleanupProcessor(**kwargs)
        report = processor.process_zip(userfile.file, userfile.filename)
        return ReportView(report).render()
    
    @expose()
    def emdashar(self, userfile, **kwargs):
        processor = EmdasharProcessor(**kwargs)
        report = processor.process_zip(userfile.file, userfile.filename)
        return ReportView(report).render()
    
    @expose()
    def result(self, filename):
        try:
            result = self.stored_files[filename]
        except KeyError:
            raise HTTPError(404, "File does not exist.")
        result.fileobj.flush()
        
        return serve_file(result.fileobj.name, 'application/x-download', 'attachment', name=result.filename)
    
    @classmethod
    def result_url(cls, filename):
        return '/tools/result/' + filename
    
    stored_files = {}
    
    @classmethod
    def make_return_file(cls, infilename):
        """ Return a file which the user can download
        
        This file is automatically deleted when it falls out of scope, but it
        is kept alive by being put in a dict.
        
        Presently the file is served from cherrypy. It could also be 
        put in the static folder and the folder regularly cleared of
        stale files. Doing it this way keeps the Tools tree self-contained.
        
        If the process is restarted the return files are discarded.
        There would also be obvious problems if running more than one
        process.
        
        """
        
        path = pathlib.Path(infilename)
        stem = path.stem
        
        # We timestamp the result, but remove a previous timestamp made by us.
        # I like timestamped filenames because many people are bad at version
        # control and might need to revert to an earlier version of their work
        # TODO this should be the users time. Check how to do this on-line.
        
        m = regex.match(r'(.*?)(?:_\d{2}-\d{2}-\d{2})+(?:_\d{2}:\d{2}:\d{2})+$', stem, regex.I)
        if m:
            stem = m[1]
        
        stem += datetime.datetime.now().strftime("_%d-%m-%y_%H:%M:%S")
        
        filename = stem + path.suffix
        
        result = cls.ResultFile(NamedTemporaryFile('w+b'), filename)
        # Chance of name collision is remote at best due to datetimestamp,
        # would almost have to be some kind of double-submit.
        # It is deliberately permitted. The latter clobbers the earlier.
        
        cls.clear_stale_downloads()
        cls.stored_files[filename] = result
        return result
    
    @classmethod
    def clear_stale_downloads(cls):
        """ Eliminate stale downloads 
        
        This method takes very little time so can be executed willy-nilly.
        """
        now = current_time()
        for result in list(Tools.stored_files.values()):
            if now - result.createtime > MAX_RETRIVE_AGE:
                try:
                    # Let the garbage collector get the temp file
                    del cls.stored_files[result.filename]
                except KeyError: # Could happen due to multithreading.
                    pass