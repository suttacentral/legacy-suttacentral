import env, os, lxml.html, time, io, subprocess, regex
from html import escape
import cherrypy
from zipfile import ZipFile, ZIP_DEFLATED

def humansize(size_in_bytes):
    size = size_in_bytes
    for sizesfx in ('b', 'kb', 'mb', 'gb', 'tb', 'pb'):
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
        if (m > 9):
            out = '{}m'.format(m)
        else:
            out = '{}m {}s'.format(m, s)
    else:
        out = '{:.2g}s'.format(seconds)
    
    return out

class File:
    def index(self):
        return """<!DOCTYPE html><html><body>
<h2>Upload a file</h2>
<form action="upload" method="post" enctype="multipart/form-data">
filename: <input type="file" name="myFile" /><br />
<input name=duck type=text value="quack"><br>
<input type="submit" />
</form>
<h2>Download a file</h2>
</body></html>
"""
    index.exposed = True
    
    def upload(self, myFile, *args, **kwargs):
        outhtml = """<!DOCTYPE html>
<html>
<head>
<style> 
.warning {{color:darkgoldenrod}}
.error {{color:red}}
</style>
<body>
<div>
{}
</div>
<hr>
<div>
{}
</div>
<p> Processing took {}</p>
</body>
</html>"""
        start=time.time()
        size = humansize(os.stat(myFile.file.name).st_size)
        
        fileinfo = "<ul><li>File: {}<li> Size: {}<li>Type:{}</ul>".format(
            myFile.filename, size , myFile.content_type)
        content_info = ''
        if str(myFile.content_type) == 'application/zip':
            zf = ZipFile(myFile.file)
            outzip = ZipFile('foobar.zip', mode='w', compression=ZIP_DEFLATED)
            infos = []
            for zi in zf.infolist():
                if zi.filename.endswith('.html') or zi.filename.endswith('.htm'):
                    infos.append('<li>{} ({})'.format(zi.filename, humansize(zi.file_size)))
                    with zf.open(zi, 'r') as infile:
                        docroot = lxml.html.parse(infile)
                    
                    dom = docroot.getroot()
                    dom.attrib.clear()
                    lxml.html.xhtml_to_html(dom)
                    for e in dom.cssselect('meta[http-equiv], meta[charset], script, link'):
                        e.drop_tree()
                    dom.cssselect('head')[0].insert(0, dom.makeelement('meta', charset="utf8"))
                    out = lxml.html.tostring(dom, encoding='utf8', doctype='<!DOCTYPE html>')
                    
                    if 1:
                        tidy_cmd = [s for s in 'tidy --doctype html5 --output-html 1 --replace-color 1 --tidy-mark 0 --quiet 1 --drop-proprietary-attributes 1 --output-encoding utf8 --clean 1 --join-classes 1 --join-styles 1 --merge-divs 1 --merge-spans 1 -w 0 --logical-emphasis 1'.split(' ') if s]
                        tidy = subprocess.Popen(tidy_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        out, errors = tidy.communicate(input=out, timeout=5)
                        try:
                            tidy.kill()
                        except:
                            pass
                        if errors:
                            has_error = False
                            tidy_msg = ['<ul class="tidy">']
                            for line in escape(errors.decode()).split('\n'):
                                m = regex.match(r'(.*?)(Warning|Error)(.*)', line)
                                if m:
                                    if m[2] == 'Error':
                                        has_error = 1
                                    tidy_msg.append('<li>{}<b class="{}">{}</b>{}</li>'.format(m[1],m[2].lower(),m[2],m[3]))
                            tidy_msg.append('</ul>')
                            if has_error:
                                tidy_msg[0] = '<ul class="tidy errors">'
                            infos[-1] += '\n'.join(tidy_msg)
                    
                    outzip.writestr(zi, out)
            
            if infos:
                content_info='<ul>{}</ul>'.format("\n".join(infos))
            zf.close()
            outzip.close()
            
            
        return outhtml.format(fileinfo, content_info, humantime(time.time()-start))
    upload.exposed = True

server = cherrypy.quickstart(File())