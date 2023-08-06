import pkg_resources
from paste.script import templates

var = templates.var

class BasicZope(templates.Template):
    _template_dir = 'templates/basic_zope'
    summary = "A Zope project"
    required_templates = ['basic_package']

class PloneCore(templates.Template):
    _template_dir = 'templates/plone_core'
    summary = "A Plone Core project"
    required_templates = []
    use_cheetah = True
    vars = [
        var('namespace_package', 'Namespace package', default='plone'),
        var('package', 'The package contained namespace package (like i18n)',
            default='example'),
        var('pythonproducts', 'Are you making a productsless Zope 2 Product?',
            default=False),
        var('version', 'Version', default='0.1'),
        var('description', 'One-line description of the package'),
        var('long_description', 'Multi-line description (in reST)'),
        var('author', 'Author name', default='Plone Foundation'),
        var('author_email', 'Author email',
            default='plone-developers@lists.sourceforge.net'),
        var('keywords', 'Space-separated keywords/tags'),
        var('url', 'URL of homepage',
            default='http://svn.plone.org/svn/plone/plone.i18n'),
        var('license_name', 'License name', default='GPL'),
        var('zip_safe', 'True/False: if the package can be distributed '
            'as a .zip file', default=False),
        ]

    def run(self, command, output_dirs, vars):
        del vars['package']
        super(PloneCore, self).run(command, output_dirs, vars)
