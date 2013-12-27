import unittest
import io

from sc.tools import *

from tests.helper import SCTestCase

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
    
    # Tests disabled temporarily until we get tidy for travis
    
    #def test_tidy(self):
        #options = {'cleanup': 'html5tidy', 'tidy-level':'moderate'}
        #cp = webtools.CleanupProcessor(**options)
        #cp.entry = webtools.Report.Entry()
        #result = cp.process_html(self.badhtml)
        #self.assertEqual(result.decode(), self.tidyhtml)
        
    #def test_crumple(self):
        #options = {'cleanup':'descriptiveclasses'}
        #cp = webtools.CleanupProcessor(**options)
        #cp.entry = webtools.Report.Entry()
        
        #result = cp.process_html(cp.preprocess_file(self.badhtml))
        #self.assertEqual(result.decode(), self.crumpledhtml)
        
    def test_finalize(self):
        pass