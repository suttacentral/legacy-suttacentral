import unittest
import io
from zipfile import ZipFile

import sc
from sc.tools import *


from tests.helper import SCTestCase

def tidy_available():
    from subprocess import Popen, PIPE, DEVNULL
    try:
        cmd = [sc.config.app['tidyprogram'], '-v']
        with Popen(cmd, stdin=None, stdout=PIPE, stderr=DEVNULL) as tidy:
            return b'HTML5' in tidy.communicate()[0]
    except FileNotFoundError:
        pass
    return False

class UnitsTest(unittest.TestCase):
    def test1plus1(self):
        self.assertEqual(1 + 1, 2) # Calibrate universe
    def setUp(self):
        self.badhtml = io.BytesIO(b'''<html><body><section><p>foobar<b>spam<b> spammity</b> spam
    <i>spammity <b> foo </i> baz </b><p>
    <li style="background:red"> <em>One</em>
    <li style="background: #f00"> Two
    <li style="background: red; font-style:italic"> Three
    <div> This is stupid </dov>
    </head>
        ''')
    
    libxml2html = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title></title>
</head>
<body>
<section>
<p>foobar<b>spam<b> spammity</b> spam
<i>spammity <b> foo </b></i> baz </b></p>
<p>
</p>
<li style="background:red"> <em>One</em>
</li>
<li style="background: #f00"> Two
</li>
<li style="background: red; font-style:italic"> Three
<div> This is stupid 
</div>
</li>
</section>
</body>
</html>
'''
    tidyhtml = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title></title>
</head>
<body>
<section>
<p>foobar<b>spam<b> spammity</b> spam
<i>spammity <b> foo </b></i> baz </b></p>
<p>
</p>
<li style="background:red"> <em>One</em>
</li>
<li style="background: #f00"> Two
</li>
<li style="background: red; font-style:italic"> Three
<div> This is stupid 
</div>
</li>
</section>
</body>
</html>
'''
    
    crumpledhtml = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title></title>
<style type="text/css">/* Unmodified rules */

/* Automatically Generated Classes */
.Bold {font-weight: bold}
.Center {margin: auto}
.Italic {font-style: italic}
.Red {background: red}
</style>
</head>
<body>
<section>
<p>foobar<strong>spam</strong> spammity spam <em>spammity <strong>foo</strong></em> <strong>baz</strong></p>
<ul>
<li class="Italic Red">One</li>
<li class="Red">Two</li>
<li class="Italic Red">Three
<div>This is stupid</div>
</li>
</ul>
</section>
</body>
</html>
'''
    
    maxDiff = None
    
    def testcleanup(self):
        cp = webtools.CleanupProcessor()
        cp.entry = webtools.Report.Entry()
        result = cp.process_html(self.badhtml)
        self.assertEqual(result.decode(), self.libxml2html)
    
    @unittest.skipUnless(tidy_available(), 
        "Tidy not available, or not HTML5 version")
    def test_tidy(self):
        options = {'cleanup': 'html5tidy', 'tidy-level':'moderate'}
        cp = webtools.CleanupProcessor(**options)
        cp.entry = webtools.Report.Entry()
        result = cp.process_html(self.badhtml)
        self.assertEqual(result.decode(), self.tidyhtml)
    
    @unittest.skipUnless(tidy_available(), 
        "Tidy not available, or not HTML5 version")
    def test_crumple(self):
        options = {'cleanup':'descriptiveclasses'}
        cp = webtools.CleanupProcessor(**options)
        cp.entry = webtools.Report.Entry()
        
        result = cp.process_html(cp.preprocess_file(self.badhtml))
        self.assertEqual(result.decode(), self.crumpledhtml)
        
    def test_finalize(self):
        pass
    
    def test_csxconvert(self):
        # This zip contains an entry on frogs in txt (latin1)
        # html (utf-8) and odt (utf-8)
        
        ff = (sc.config.test_samples_dir / 'ff.zip').open('rb')
        csxp = webtools.CSXProcessor()
        result = csxp.process_zip(ff, ff.name)
        
        # Affirm result is a valid ZipFile
        z = ZipFile(result.result.fileobj)
        
        # Affirm content is now utf8
        text = z.read('ff-latin1.txt').decode(encoding='UTF-8')
        
        # 'Maṇḍūka', 'Nīlamaṇḍūka', 'Uddhumāyikā'
        
        # And it has been properly transcoded.
        self.assertIn('Maṇḍūka', text)
        
        html = z.read('ff-utf8.html').decode(encoding='UTF-8')
        self.assertIn('Nīlamaṇḍūka', text)
        
        # This doesn't completely test odt but confirms that
        # it basically worked.
        odt = z.open('ff.odt')
        odt = io.BytesIO(odt.read()) # Needs to be seekable
        
        odtz = ZipFile(odt)
        content = odtz.read('content.xml').decode(encoding='UTF-8')
        self.assertIn('Uddhumāyikā', content)
        

