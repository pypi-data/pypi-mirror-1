import copy
import socket
import random
import string
import os, sys
from paste.script import templates

var = templates.var
recipe = 'collective.buildbot'

class Template(templates.Template):
    summary = "Build and workload test project"
    required_templates = []
    use_cheetah = True
    egg_plugin = [recipe]

    vars = [var('project_name', 'Project name'),
        var('port', 'Slaves listening port', default='9050')]

class Funkbot(templates.Template):
    summary = "Buildbot and Funkload ready buildout"
    required_templates = []
    use_cheetah = True
    _template_dir = 'templates/funkbot'
    egg_plugin = [recipe]

    vars = [var('vcs', 'VCS used', default='svn'),
            var('vcs_url', 'Repoze URL'),
            var('email', 'Reports delivery adress')]

    def pre(self, command, output_dir, vars):
        vars['vcs_user'] = ''
        vars['vcs_user_password'] = ''
        vars['recipe'] = recipe
        vars['directory'] = '${buildout:directory}'
        vars['hostname'] = socket.gethostname()
        vars['password'] = ''.join([random.choice(string.ascii_letters) for i in range(8)])
        vars['pythonpath'] = os.path.dirname(sys.executable)
        vars['aport'] = '8080'
        vars['pport'] = '8000'

    def post(self, *args, **kwargs):
        print "==================================================="
        print "Local application settings complete"
        print "Please check the conf files"
        print "We advice you to read the README"
        print "==================================================="
