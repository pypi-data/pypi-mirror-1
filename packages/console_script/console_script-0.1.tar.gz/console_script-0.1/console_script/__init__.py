from paste.script import templates

var = templates.var

class console_script(templates.Template):
    _template_dir = 'template'
    summary = 'pastescript template for creating command line applications'
    vars = [
        var('description', 'One-line description of the package'),
        var('author', 'Author name'),
        var('author_email', 'Author email'),
        var('url', 'URL of homepage'),
        ] 
