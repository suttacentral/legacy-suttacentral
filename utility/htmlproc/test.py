import sys, unittest
sys.path.append('..')
from htmlproc import *
from tools.html import *



class TestHTMLProcessing(unittest.TestCase):
    dreadhtml = '''
<html><head><title>Foobar</title></head>
<body>
<div>
<h1>Spam glorious Spam!</h1>
<p>Everyone loves spam!</p>
</div>
<div class="foo">
<div class="bar">
<div id="morespam">
<div><b>Want spam?</b> <blink>Click here!</blink></div>
</div>
<div id="baz1">
<div class="content">
<div class="just kidding">
<div class="pusher">
<div class="hidden">This isn't important</div>
<div class="main-content">
<h1>An unrealistic example.</h1>
<p> This example is unrealistic</p>
<p> Because there is not nearly enough crap</p>
<p> preceeding the actual content</p>
<p> For realism there should be inline scripts</p>
<p> and inline style sheets</p>
<p> At least a hundred of them.</p>
</div>
</div>
</div>
</div>
</div>
<script>alert("Make it stop!")</script>
</div>
</div>
</body>
</html>'''

    contents='''<html>
<head><meta charset="utf8"><title>Foobar</title></head>
<body>
<div class="main-content">
<h1>An unrealistic example.</h1>
<p> This example is unrealistic</p>
<p> Because there is not nearly enough crap</p>
<p> preceeding the actual content</p>
<p> For realism there should be inline scripts</p>
<p> and inline style sheets</p>
<p> At least a hundred of them.</p>
</div>
</body>
</html>'''
    def setUp(self):
        self.dom = fromstring(self.dreadhtml)
    
    def test_top_and_tail_auto(self):
        top_and_tail(self.dom)
        self.assertEqual(str(self.dom), self.contents)
    
    def test_top_and_tail_select(self):
        top_and_tail(self.dom, 'div.main-content')
        self.assertEqual(str(self.dom), self.contents)
    
    def test_top_and_tail_fail(self):
        with self.assertRaises(CssSelectorFailed):
            top_and_tail(self.dom, '.god')
        with self.assertRaises(CssSelectorFailed):
            top_and_tail(self.dom, 'div.p')
        
        
if __name__ == '__main__':
    unittest.main()