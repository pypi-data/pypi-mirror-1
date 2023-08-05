import os
import glob
from paste.script.command import Command, BadCommand
from paste.script import pluginlib, copydir

class ServletCommand(Command):

    summary = "Create servlet"
    usage = 'SERVLET_NAME'

    min_args = 1
    max_args = 1
    default_verbosity = 1

    parser = Command.standard_parser(simulate=True, quiet=True,
                                     interactive=True, overwrite=True)
    parser.add_option('--no-servlet',
                      action='store_true',
                      dest='no_servlet',
                      help="Don't create a servlet; just template(s)")

    group_name = 'Paste WebKit'

    def command(self):
        servlet = self.args[0]
        if servlet.endswith('.py'):
            # Erase extensions
            servlet = servlet[:-3]
        if '.' in servlet:
            # Turn into directory name:
            servlet = servlet.replace('.', os.path.sep)
        if '/' != os.path.sep:
            servlet = servlet.replace('/', os.path.sep)
        parts = servlet.split(os.path.sep)
        name = parts[-1]
        base_package, base = self.web_dir()
        if not parts[:-1]:
            dir = ''
        elif len(parts[:-1]) == 1:
            dir = parts[0]
        else:
            dir = os.path.join(*parts[:-1])

        vars = {'name': name,
                'base_package': base_package}

        if not self.options.no_servlet:
            self.create_servlet(
                base_package, base, dir, name, vars)

        template_base = os.path.join(os.path.dirname(base), 'templates')
        if not os.path.exists(template_base):
            if self.verbose > 1:
                print 'No template directory %s' % template_base
            return

        blanks = glob.glob(os.path.join(base, template_base, 'blank.*'))
        if not blanks and self.verbose:
            print 'No blank templates found in %s' % self.shorten(template_base)

        for blank in blanks:
            self.create_blank(
                blank, template_base, dir, name, vars)

    def create_servlet(self, base_package, base, dir, name, vars):
        self.ensure_dir(os.path.join(base, dir))
        blank = os.path.join(base, 'blank.py')
        if not os.path.exists(blank):
            blank = os.path.join(os.path.dirname(__file__),
                                 'paster_templates',
                                 'blank_servlet.py_tmpl')
        f = open(blank, 'r')
        content = f.read()
        f.close()
        if blank.endswith('_tmpl'):
            content = copydir.substitute_content(content, vars,
                                                 filename=blank)
        dest = os.path.join(base, dir, '%s.py' % name)
        self.ensure_file(dest, content)

    def create_blank(self, blank, template_base, dir, name, vars):
        ext = os.path.splitext(blank)[1]
        f = open(blank, 'r')
        content = f.read()
        f.close()
        if ext.endswith('_tmpl'):
            content = copydir.substitute_content(
                content, vars, filename=blank)
            ext = ext[:-5]
        dest = os.path.join(template_base, dir, name + ext)
        self.ensure_dir(os.path.dirname(dest))
        self.ensure_file(dest, content)
            
    def web_dir(self):
        egg_info = pluginlib.find_egg_info_dir(os.getcwd())
        # @@: Should give error about egg_info when top_leve.txt missing
        f = open(os.path.join(egg_info, 'top_level.txt'))
        packages = [l.strip() for l in f.readlines()
                    if l.strip() and not l.strip().startswith('#')]
        f.close()
        # @@: This doesn't support deeper servlet directories,
        # or packages not kept at the top level.
        base = os.path.dirname(egg_info)
        possible = []
        for pkg in packages:
            d = os.path.join(base, pkg, 'web')
            if os.path.exists(d):
                possible.append((pkg, d))
        if not possible:
            raise BadCommand(
                "No web package found (looked in %s)"
                % ', '.join(packages))
        if len(possible) > 1:
            raise BadCommand(
                "Multiple web packages found (%s)" % possible)
        return possible[0]


    
        
