from paste.script.templates import Template, vars
import datetime

class RelmanWebConsoleTemplate(Template):
    _template_dir = "ctl/templates/webconsole"   
    summary = "ReleaseManager WebConsole"

    vars = [
        var('version', 'Version', default='0.1a0'),
        var('description', 'One-line description of the widget'),
        var('long_description', 'Multi-line description (in reST)'),
        var('author', 'Author name'),
        var('author_email', 'Author email'),
        var('url', 'URL of homepage'),
        var('license_name', 'License name'),
    ]

    def run(self, command, output_dir, vars):
        vars['year'] = str(datetime.datetime.now().year)
        vars['package'] = vars['widget_name'] or vars['package']
        super(RelmanWebConsoleTemplate, self).run(command, output_dir, vars)
