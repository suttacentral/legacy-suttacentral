""" Sutta Central HTML Text Processing Tools 

These tools are segregated because in a certain sense they have
nothing to do with the suttas. In fact they could make a legitimate 
standalone web application.



"""

import config
from cherrypy import expose
from views import InfoView

from zipfile import ZipFile, ZIP_DEFLATED, is_zipfile
from pathlib import Path
from Threading import RLock
import random

import lhtmlx
import logging, io, regex
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
        filename = ''
        info = ''
        warnings = ''
        errors = ''
        modified = False
        def __repr__(self):
            out = '<' +self.filename
            if self.info:
                out += ' {} info'.format(self.info)
            if self.warnings:
                out += ' {} warnings'.format(self.warnings)
            if self.errors:
                out += ' {} errors'.format(self.errors)
            if self.modified:
                out += ' (modified)'
            out += '>'
    
    error = None # If error is set, something went badly wrong.
    header = ''
    footer = ''
    download = None # Should be a simple filename

class ProcessorBase:
    output_encoding = None # None = keep existing
    allowed_types = None # None = all allowed.
    
    def process_zip(self, inzipfile, outzipfile):
        """ Process every file in a zip archive
        
        
        """
        
        start=time()
        report = Report()
        if not is_zipfile(inzipfile):
            report.error = "{} is not a valid zip archive.".format(inzipfile.name)
            return report
        
        with ZipFile(inzipfile, 'r') as inzip, \
            ZipFile(outzipfile, 'w', compression=ZIP_DEFLATED) as outzip:
            report.header = "{} contains {} files.".format(inzipfile.name, 
                                                        len(inzip.filelist))
            for zi in inzipfile.filelist:
                data, report_entry = self.process_file(inzip.open(zi, 'r'))
                # Manually specify compress_type in case some loony uploads
                # a -0 archive (ZipFile compression is overridden by ZipInfo)
                outzip.open(zi, 'w', compress_type=ZIP_DEFLATED).write(data)
                report.append(report_entry)
        
        report.footer = "Complete in {}".format(humantime(time()-start))
        report.download = outzipfile.filename
        return report
        
    def process_file(self, fileobj, zi, continue_on_error=False):
        entry = Report.Entry()
        self.entry = entry
        entry.fileinfo = "{}: {}".format(zi.filename, humansize(zi.file_size))
        
        suffix = Path(zi.filename).suffix.lower()
        filedata = fileobj.read()
        fileobj = io.BytesIO(filedata)
        
        if (allowed_types and suffix not in allowed_types 
                        and suffix[1:] not in allowed_types):
            entry.info("No instructions for {}".format(suffix))
            out = self.process_unknown(fileobj)
        elif suffix in {'.txt'}:
            entry.info = "Treating as text"
            out = self.process_txt(fileobj)
        elif suffix in {'.html', '.htm'}:
            entry.info = "Treating as html"
            out = self.process_html(fileobj)
        elif suffix in {'.xml', '.xhtml'}:
            entry.info = "Treating as xml"
            out = self.process_xml(fileobj)
        elif suffix in {'.odt', '.sxw'}:
            entry.info = "Treating as Open Document"
            out = self.process_odt(fileobj)
        else:
            entry.info = "Unknown file, not processing"
            out = self.process_unknown(fileobj)
        
        # We could do better (and worse), this confirms the file definitely
        # hasn't changed. But there might be quite meaningless changes.
        entry.modified = out != filedata
            
        return out, entry
    
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
            for zi in inodtzip.filelist:
                zi_in_obj = inodtzip.open(zi, 'r')
                if zi.filename == 'content.xml':
                    # Process content.xml
                    zdata = self.process_xml(zi_in_obj)
                else:
                    # Everything else, just copy straight through.
                    zdata = zi_in_obj.read()
                outodtzip.writestr(zi, zdata)
        
        return outodtdata.getvalue()
    
    def process_bytes(self, data):
        # Default encoding is utf8. If another encoding is needed, 
        # the process_filetype method needs to handle that and call
        # process_str
        return self.process_str(data.decode()).encode(self.output_encoding)
    
    def process_str(self, string):
        raise NotImplementedError

class TextProcessor(ProcessorBase):
    """ Only process the text contents of the file, leaving markup alone """
    def process_txt(self, fileobj):
        return process_bytes(fileobj.read())
    
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
    
    """
    
    def process_txt(self, fileobj):
        dom = lhtmlx.parse(fileobj, encoding='utf8')
        self.process(dom.getroot()
        return dom.text_content().encode()
    
    def process_html(self, fileobj):
        dom = lhtmlx.parse(fileobj)
        self.process(doc.getroot())
        return lxml.html.tostring(doc, doctype=doc.docinfo.doctype, 
                                    encoding=doc.encoding)
        
    def process_xml(self, fileobj):
        dom = lxml.etree.parse(fileobj)
        self.process(doc.getroot())
        return lxml.etree.tostring(doc, xml_declaration=True, 
                                    doctype=doc.docinfo.doctype,
                                    encoding=doc.docinfo.encoding)
    def process(self, root):
        raise NotImplementedError
    
class CSXProcessor(TextProcessor):
    output_encoding = "UTF-8"
    def process_html(self, fileobj):
        return process_bytes(fileobj.read())
    
    def process_xml(self, fileobj):
        return process_bytes(fileobj.read())
    
    def process_bytes(self, data):
        try:
            string = data.decode(encoding='utf8')
        except UnicodeError:
            string = data.decode(encoding='latin1')
        return process_str(string).decode(self.output_encoding)     
    
    def process_str(self, string):
        return self.csx_to_utf8()
    
    _csx_to_utf8_tr = str.maketrans(
                    'àâãäåæ\x83\x88\x8c\x93\x96çèéêëìíîïð¤¥ñòóôõö÷øùú§üýþÿ',
                    'āĀīĪūŪâêîôûṛṚṝṜḷḶḹḸṅṄñÑṭṬḍḌṇṆśŚṣṢṁṃṂḥḤ') 
    csx_to_utf8(string):
        return string.translate(self._csx_to_utf8_tr)

@expose()
class Tools(object):
    def __call__(self, *args, **kwargs):
        return InfoView('tools').render()
    
    @expose()
    def reencode(self, userfile, **kwargs):
        processor = CSXProcessor()
        
        outzip = self.make_return_file(userfile.file.filename)
        report = processor.process_zip(userfile.file, outzip)
        
        
    
    @staticmethod
    def make_return_file(infilename):
        """ Return a file which the user can download
        
        This file is not automatically deleted when it falls out of scope.
        
        """
        
        prodir = pathlib.PosixPath(config.processed_root)
        p = pathlib.Path(infilename)
        stem = p.stem
        suffix = p.suffix
        m = regex.match(r'(.*)_\d\d-\d\d-\d\d_\d\d:\d\d', stem, regex.I)
        if m:
            stem = m[1]
        
        
        stem += datetime.datetime.now().strftime("_%d-%m-%y_%H:%M:%S")
        
        # It's more-or-less impossible for this to fail since the filename
        # contains a timestamp. So it would be needed in the same second
        # for two people to upload an identically named file.
        try:
            return prodir.joinpath(stem).with_suffix(suffix).open('xb')
        except FileExistsError:
            pass
        
        logger.info('The universe is feeling silly today.')
        return tempfile.NamedTemporaryFile('wb', prefix=stem + '.',
                    suffux=suffix, dir=config.processed_root, delete=False)
    
    janitor_lock = RLock()
    
    @staticmethod
    def clear_stale_downloads(max_age=3600):
        """ Eliminate stale downloads """
        prodir = pathlib.PosixPath(config.processed_root)
        
        with Tools.janitor_lock:
            for file in prodir.glob('*'):
                if not file.is_file:
                    continue
                age = time.time() - file.stat().st_mtime
                if age > max_age:
                    file.unlink()

def process_odt(data):
    """ With ODT we are interested in content.xml """
    outdata = io.BytesIO()
    inodt = ZipFile(io.BytesIO(data), 'r')
    outodt = ZipFile(outdata, 'w')
    for zi in inodt.filelist:
        zfile = inodt.open(zi, 'r')
        if zi.filename == 'content.xml':
            doc = lxml.etree.parse(zfile)
            zdata = lxml.etree.tostring(doc, xml_declaration=True, encoding='UTF-8')
        else:
            zdata = zfile.read()
        outodt.writestr(zi, zdata)
    inodt.close()
    outodt.close()
    return outdata.getvalue()

foo = process_odt(open('thai.odt', 'rb').read())
open('bar.odt', 'wb').write(foo)