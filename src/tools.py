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
# a bazillion zeroes to try and wipe out the servers memory when unzipped,
# because we use writestr atm, this requires unzipping into memory)
# At present a maximum of 2-3x MAX_FILE_SIZE memory might be used when 
# processing an archive.
# However timeouts also have to be considered. If someone has downloaded
# the internet and wants us to process it, it needs to be refused or time out.

MAX_RETRIVE_AGE = 600   # time in seconds.
# How long the users result zip will be kept alive for before being valid
# targets for garbage collection. May live for longer.

import random, pathlib, datetime, logging, io, regex, os
import config, lhtmlx
from cherrypy import expose, HTTPError
from cherrypy.lib.static import serve_fileobj
from views import InfoView
from zipfile import ZipFile, ZIP_DEFLATED, is_zipfile
from time import time as current_time
from html import escape
from tempfile import TemporaryFile
from bs4 import UnicodeDammit
from util import humansortkey

logger = logging.Logger(__name__)

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

# babel.dates.format_timedelta almost cut the mustard but no ms
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

class Report(list):
    class Entry:
        def __init__(self):
            self.filename = ''
            self.info = []
            self.warnings = []
            self.errors = [] # If there are errors, it failed.
            self.modified = False
        def __repr__(self):
            out = '<Report.Entry ' + self.filename + ' : '
            if self.info:
                out += ' {} info'.format(self.info)
            if self.warnings:
                out += ' {} warnings'.format(self.warnings)
            if self.errors:
                out += ' {} errors'.format(self.errors)
            if self.modified:
                out += ' (modified)'
            out += '>'
            return out
    
    error = None # If error is set, something went badly wrong.
    title = ''
    header = ''
    footer = ''
    download = None # Should be a simple filename
    downloadsize = 'Unknown'
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
        if self.download:
            out += ' download: {} ({})\n'.format(self.download, self.downloadsize)
        if len(self) > 0:
            out += ' contents: \n' + '\n'.join(repr(e) for e in self)
        out += '>\n'
        return out

class ProcessingError(Exception):
    pass

class ProcessorBase:
    """ The ProcessorBase attempts to implement all the zip and filehandling
    stuff so that derived classes only need to implement process_str,
    and perhaps process_bytes
    
    """
    
    output_encoding = None # None = keep existing
    allowed_types = None # None = all allowed.
    
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
        self.report.download = resultfile.name
        self.report.downloadsize = humansize(os.stat(resultfile.fileobj.fileno()).st_size)
        
    def process_one(self, infile):
        """ process a non-zipped file. Is this needed? """
        self.init_report()
        
        self.finalize_report(resultfile)
        return report        
    
    def process_zip(self, inzipfile, filename):
        """ Process every file in a zip archive
        
        Returns a `Report` object containing information about what happened
        and a name which can be used to construct a url to the result zip.
        """
        
        report = self.init_report()
        
        if not is_zipfile(inzipfile):
            report.error = "{} is not a valid zip archive.".format(filename)
            return report
        
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
                report.error = "Archive too large. Maximum uncompressed size is {}.".format(humansize(MAX_ARCHIVE_SIZE))
                return report
            
            for zinfo in inzip.filelist:
                data = self.process_file(inzip.open(zinfo, 'r'), zinfo)
                if data is None:
                    # This happens when an error occured.
                    continue
                # Manually specify compress_type in case some loony uploads
                # a -0 archive (archive compression is overridden by ZipInfo)
                outzip.writestr(zinfo, data, compress_type=ZIP_DEFLATED)
        
        self.finalize_report(resultfile)
        return report
        
    def process_file(self, fileobj, zinfo, continue_on_error=False):
        entry = Report.Entry()
        self.entry = entry
        self.report.append(entry)
        
        entry.filename = zinfo.filename
        entry.info.append("{}: {}".format(zinfo.filename, humansize(zinfo.file_size)))
        if zinfo.file_size > MAX_FILE_SIZE:
            # This is probably malicious so we wont bend over backwards.
            entry.errors.append("File too large. File must be no larger than {}.".format(humansize(MAX_FILE_SIZE)))
            return None
        
        suffix = pathlib.Path(zinfo.filename).suffix.lower()
        filedata = fileobj.read()
        fileobj = io.BytesIO(filedata)
        
        try:
            if (self.allowed_types and suffix not in self.allowed_types 
                            and suffix[1:] not in self.allowed_types):
                entry.info("No instructions for {}".format(suffix))
                out = self.process_unknown(fileobj)
            elif suffix in {'.txt'}:
                entry.info.append("Treating as text")
                out = self.process_txt(fileobj)
            elif suffix in {'.html', '.htm'}:
                entry.info.append("Treating as html")
                out = self.process_html(fileobj)
            elif suffix in {'.xml', '.xhtml'}:
                entry.info.append("Treating as xml")
                out = self.process_xml(fileobj)
            elif suffix in {'.odt', '.sxw'}:
                entry.info.append("Treating as Open Document")
                out = self.process_odt(fileobj)
            else:
                entry.info.append("Unknown file, not processing")
                out = self.process_unknown(fileobj)
        except ProcessingError:
            return None
        
        # We could do better (and worse), this confirms the file definitely
        # hasn't changed. But there might be quite meaningless changes.
        entry.modified = out != filedata
            
        return out
    
    def process_unknown(self, fileobj):
        return fileobj.read()
    
    def process_txt(self, fileobj):
        raise NotImplementedError
    
    def process_html(self, fileobj):
        raise NotImplementedError
    
    def process_xml(self, fileobj):
        raise NotImplementedError
    
    def process_odt(self, odt):
        """ Calls process_xml on content.xml inside the odt 
        
        .odt is pretty easy to work with using ZipFile, so it has been
        included as an option, but there are few guarantees about more
        complex operations producing a valid odt document in return.
        
        Still as long as the xml structure isn't changed (much) the document
        will come out just fine.
        
        """
        
        outodtdata = io.BytesIO()
        with ZipFile(odt, 'r') as inodt,\
                ZipFile(io.BytesIO(outodtdata), 'w', ZIP_DEFLATED) as outodt:
            for zinfo in inodtzip.filelist:
                if zinfo.file_size > MAX_FILE_SIZE:
                    self.entry.errors.append("File too large. File must be no larger than {}.".format(humansize(MAX_FILE_SIZE)))
                    # probably malicious so an Error
                    raise ProcessingError
                zi_in_obj = inodtzip.open(zinfo, 'r')
                if zinfo.filename == 'content.xml':
                    # Process content.xml
                    zdata = self.process_xml(zi_in_obj)
                else:
                    # Everything else, just copy straight through.
                    zdata = zi_in_obj.read()
                outodtzip.writestr(zinfo, zdata)
        
        return outodtdata.getvalue()
    
    def process_bytes(self, data):
        # Default encoding is utf8. If another encoding is needed, 
        # the process_filetype method needs to handle that and call
        # process_str
        return self.process_str(data.decode()).encode(self.output_encoding)
    
    def process_str(self, string):
        raise NotImplementedError

class TextProcessor(ProcessorBase):
    """ Only process the text contents of the file, leaving markup alone 
    
    The derived class should implement process_str.
    """
    def process_txt(self, fileobj):
        return self.process_bytes(fileobj.read())
    
    def process_html(self, fileobj):
        doc = lhtmlx.parse(fileobj)
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

class ElementTreeProcessor(ProcessorBase):
    """ Apply transformations to an ElementTree representation of the document
    
    Isn't truly meaningful for .txt, altough a .txt is processed as html
    just fine, the content is wrapped in a p element.
    
    The derived class should implement process_root
    
    """
    
    def process_txt(self, fileobj):
        dom = lhtmlx.parse(fileobj, encoding='utf8')
        self.process_root(dom.getroot())
        return dom.text_content().encode()
    
    def process_html(self, fileobj):
        dom = lhtmlx.parse(fileobj)
        self.process_root(doc.getroot())
        return lxml.html.tostring(doc, doctype=doc.docinfo.doctype, 
                                    encoding=doc.encoding)
        
    def process_xml(self, fileobj):
        dom = lxml.etree.parse(fileobj)
        self.process_root(doc.getroot())
        return lxml.etree.tostring(doc, xml_declaration=True, 
                                    doctype=doc.docinfo.doctype,
                                    encoding=doc.docinfo.encoding)
    def process_root(self, root):
        raise NotImplementedError
    
class CSXProcessor(TextProcessor):
    """ Attemps to convert CSX+ to UTF-8
    
    Works for both true CSX+, and UTF-8 resulting from treating
    CSX+ as Latin1.
    
    If the content isn't CSX+ it will mess things up, no effort
    is made to detect this condition.
    
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

class DetwingleProcessor(ProcessorBase):
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

class CleanupProcessor(ElementTreeProcessor):
    pass
    

class Tools(object):
    """ Provide HTML/XML processing web services.
    
    Note that potential for denial of service is very high, since
    this module can do things like dynamically create files and consume
    gobs of cpu. The main consideration has been limiting memory use.
    
    """
    
    class ResultFile:
        " Used for delivery of results to user "
        def __init__(self, fileobj, name):
            self.fileobj = fileobj
            self.name = name
            self.createtime = current_time()
        
    @expose()
    def index(self, **kwargs):
        return InfoView('tools/tools').render()
    
    @expose()
    def reencode(self, userzip, action=None, **kwargs):
        print('Re-encode {} / {}'.format(userzip, action))
        if action == 'csxplus':
            processor = CSXProcessor()
        elif action == 'detwingle':
            processor = DetwingleProcessor()
        else:
            raise HTTPError(404, "Invalid form parameters")
        
        report = processor.process_zip(userzip.file, userzip.filename)
        return '<!DOCTYPE html><html><body><p>' + "<br>".join(
                                escape(s) for s in str(report).split('\n'))
    
    stored_files = {}
    
    @expose()
    def result(self, filename):
        try:
            result = self.stored_files[filename]
        except KeyError:
            raise KeyError("{}, {}".format(filename, self.stored_files))
        result.fileobj.seek(0)
        return serve_fileobj(result.fileobj, 'application/x-download', 
                               'attachment', name=result.name)
    
    @classmethod
    def make_return_file(cls, infilename):
        """ Return a file which the user can download
        
        This file is automatically deleted when it falls out of scope, but it
        is kept alive by being put in a dict.
        
        Presently the file is served from cherrypy. It could also be 
        put in the static folder and the folder regularly cleared of
        stale files. Doing it this way keeps the Tools tree self-contained and
        means we aren't storing copies of what the user has uploaded.
        
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
        
        m = regex.match(r'(.*)_\d{2}-\d{2}-\d{2}_\d{2}:\d{2}:\d{2}', stem, regex.I)
        if m:
            stem = m[1]
        
        stem += datetime.datetime.now().strftime("_%d-%m-%y_%H:%M:%S")
        
        filename = stem + path.suffix
        
        result = cls.ResultFile(TemporaryFile('w+b'), filename)
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
        for filename, result in list(Tools.stored_files.values()):
            if now - result.createtime > MAX_RETRIVE_AGE:
                try:
                    # Let the garbage collector get the temp file
                    # (If it is being served, it should be kept alive)
                    del cls.stored_files[filename]
                    
                except KeyError: # Could happen due to multithreading.
                    pass