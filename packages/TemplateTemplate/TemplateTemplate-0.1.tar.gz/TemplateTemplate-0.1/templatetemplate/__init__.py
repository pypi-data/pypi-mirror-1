from paste.script import templates

var = templates.var

class PasteScriptTemplateTemplate(templates.Template):
    _template_dir = 'template'
    summary = "a template for creating PasteScript templates"
    vars = [
        var('description', 'One-line description of the package'),
        var('author', 'Author name'),
        var('author_email', 'Author email'),
        var('url', 'URL of homepage'),
        ] 
