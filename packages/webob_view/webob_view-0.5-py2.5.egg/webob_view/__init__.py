from paste.script import templates

var = templates.var

class WebobViewTemplate(templates.Template):
    _template_dir = 'template'
    summary = "a simple view with webob"
    vars = [
        var('description', 'One-line description of the package'),
        var('author', 'Author name'),
        var('author_email', 'Author email'),
        var('url', 'URL of homepage'),
        var('port', 'port to serve paste')
        ] 
