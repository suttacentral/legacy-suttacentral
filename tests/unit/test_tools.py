import io
import unittest
from zipfile import ZipFile, ZIP_DEFLATED
from tempfile import NamedTemporaryFile
from collections import Counter

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

def create_zipfile(*files):
    """Create a zip from arguments. Each can either be a fileobject, or
    a filename, data tuple.
    
    The underlying temporary file will be collected automatically.
    
    """
    # BytesIO would also be reasonable, however, on the server, we have
    # an actual temporaryfile underlying the zip.
    outfile = NamedTemporaryFile(suffix='.zip')
    # ZIP_STORED isn't representive of normal content, so use ZIP_DEFLATED
    outzip = ZipFile(outfile, 'w', compression=ZIP_DEFLATED)
    num = 0
    for file in files:
        if hasattr(file, 'name'):
            outzip.write(file.name)
        elif len(file) == 2:
            name, data = file
            outzip.writestr(name, data)
        else:
            raise ValueError("Invalid input to create_zip, {}".format(file))
    outzip.close()
    outfile.seek(0)
    
    return outfile

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
        options = {'canonical-paths':'on'}
        inzip = create_zipfile(
            ['en/dn2.html', '<h1>The Fruits</h1><p>Thus<p>Rejoiced'],
            ['en/meta.html', 'Translated by Bhikkhu Foo'],
            ['dn1.html', '<h1>The Net</h1><p>Thus<p>Rejoiced'])
            
        
        cp = webtools.FinalizeProcessor(**options)
        result = cp.process_zip(inzip, inzip.name)
        
        meta_msg = Counter(e[0] for e in result[0].messages)
        self.assertEqual(meta_msg['info'], 1)
        dn1_msg = Counter(e[0] for e in result[1].messages)
        self.assertEqual(dn1_msg['error'], 3)
        dn2_msg = Counter(e[0] for e in result[2].messages)
        self.assertEqual(dn2_msg['warning'], 1)        
    
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
        
class EmdasharTest(unittest.TestCase):
    def setUp(self):
        self.logger = emdashar.SortedLogger()
        self.logger.file = io.StringIO()
        self.emdash = emdashar.Emdashar(logger=self.logger).emdash
    
    def test_quotes(self):
        samples =  [('<p>This is "misuse" of quotes</p>',
                  '<p>This is “misuse” of quotes</p>'),
                  
                  ('<p>"Another paragraph."</p>',
                  '<p>“Another paragraph.”</p>'),
                  
                  ('<b>"mismatched quotes”</b>',
                  '<b>“mismatched quotes”</b>'),
                  
                  ('<i>“This is a quote“.</i>',
                  '<i>“This is a quote”.</i>'),
                  ]
                  
        for wrong, right in samples:
            root = html.fromstring(wrong)
            self.emdash(root)
            self.assertEqual(str(root), right)
    
    def test_dashes(self):
        samples = [('<p>See 1-10</p>', '<p>See 1–10</p>'),
                    ('<p>Foo--bar</p>', '<p>Foo—bar</p>'),
                    ('<p>See 11—13</p>', '<p>See 11–13</p>'),
                    ('<p>"spam." - "baz."</p>', '<p>“spam.”—“baz.”</p>'),
                    ('<p>“spam.” - “baz.”</p>', '<p>“spam.”—“baz.”</p>'),
                    ]
        
        for wrong, right in samples:
            root = html.fromstring(wrong)
            self.emdash(root)
            self.assertEqual(str(root), right)
    
    def test_longer(self):
        source = ('<p>"I admit," said he - when I mentioned to him this objection'
            '- "I admit the truth of your critic\'s facts, but I deny his '
            'conclusions. It is true that we have really in Flatland a Third '
            'unrecognized Dimension called `height,\' just as it is also true '
            'that you have really in Spaceland a Fourth unrecognized Dimension'
            ', called by no name at present, but which I will call '
            '`extra-height\'. But we can no more take cognizance of our '
            '`height\' then you can of your `extra-height\'. '
            'Even I - who have been in Spaceland, and have had the privilege '
            'of understanding for twenty-four hours the meaning of `height\' '
            '- even I cannot now comprehend it, nor realize it by the sense '
            'of sight or by any process of reason; I can but apprehend it by '
            'faith."</p>')
        root = html.fromstring(source)
        self.emdash(root)
        self.logger.flush()
        self.logger.file.seek(0)
        text = root.text_content()
        # We wont check the entire result, but will cherrypick some cases.
        self.assertEqual(text[0], '“')
        self.assertIn('”', text[-2:])
        self.assertIn('‘height,’', text)
        self.assertIn('‘extra-height’.', text)
        self.assertIn('critic’s', text)
        self.assertIn('Even I—who', text)
        self.assertIn('‘height’—even I', text)
        # Don't worry about the particulars, but check that something
        # is being logged.
        self.assertGreater(len(self.logger.file.readlines()), 8)