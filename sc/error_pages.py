''' Error Pages for when Things Go Wrong (tm)

These should be dependent on as little as possible so that they can
be reliably delivered. For instance, using jinja2 template is probably
not a good idea for internal server errors!

'''


html_template = '''<html><head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>500 Internal Server Error</title>
<style>
body {{
  max-width: 40em;
  margin: auto;
}}
#traceback {{
    font-family: monospace;
}}
h1, h2 {{
    text-align: center;
}}
</style>
</head>
<body>
<h1> Sutta Central proudly presents a:</h1>
<h2>500 Internal Server Error</h2>
<div id="message">{message}</div>
<div id="traceback">
{traceback}
</div>

<p>If you are an ordinary user, try refreshing this page a few times.
<p>Even if it doesn't start working, our monitoring service will notice
that error pages are being generated and automatically send a message
to the programmers.
</body>
</html>'''

def error_page_404(status, message, traceback, version):
    return (sc.static_dir / '404.html').open('r', encoding='utf-8').read()

def error_page_500(status, message, traceback, version):
    return html_template.format(message=message, traceback=traceback)

def custom_500(message, traceback):
    template = '''<html><head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>500 Internal Server Error</title>
</head>
<body>
<h2>500 Internal Server Error</h2>

</body>
</html>'''
    return html_template.format(message=message, traceback=traceback)
