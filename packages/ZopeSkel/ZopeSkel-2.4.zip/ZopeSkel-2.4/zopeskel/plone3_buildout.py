from zopeskel.base import BaseTemplate
from zopeskel.base import var

class Plone3Buildout(BaseTemplate):
    _template_dir = 'templates/plone3_buildout'
    summary = "A buildout for Plone 3 projects"
    required_templates = []
    use_cheetah = True

    vars = [
        var('zope2_install',
            'Path to Zope 2 installation; leave blank to fetch one',
            default=''),
        var('plone_products_install',
            'Path to directory containing Plone products; leave blank to fetch one',
            default=''),
        var('zope_user',
            'Zope root admin user',
            default='admin'),
        var('zope_password',
            'Zope root admin password'),
        var('http_port',
            'HTTP port',
            default=8080),
        var('debug_mode',
            'Should debug mode be "on" or "off"?',
            default='off'),
        var('verbose_security',
            'Should verbose security be "on" or "off"?',
            default='off'),
        ]

    def post(self, command, output_dir, vars):
        print "-----------------------------------------------------------"
        print "Generation finished"
        print "You probably want to run python bootstrap.py and then edit"
        print "buildout.cfg before running bin/buildout -v"
        print
        print "See README.txt for details"
        print "-----------------------------------------------------------"



