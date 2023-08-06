import os
import pkg_resources
import re
import zc.buildout.easy_install
import zc.recipe.egg
import zc.recipe.testrunner


def string2list(string, default):
    result = string and string.split() or default
    return [item.strip() for item in result]


RUNNER_PREFIX = 'runner-'


class Recipe(object):

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

        if not 'max_jobs' in options:
            options['max_jobs'] = '1'

        self.include = string2list(self.options.get('include', ''), [])
        self.exclude = string2list(self.options.get('exclude', ''), [])
        self.wanted_packages = self._wanted_packages()

        self.script = self.options.get('script', self.name)

        # gather options to be passed to the underlying testrunner
        self.testrunner_options = {}
        for opt in self.options:
            if opt.startswith(RUNNER_PREFIX):
                runner_opt = opt[len(RUNNER_PREFIX):]
                self.testrunner_options[runner_opt] = self.options[opt]

    def install(self):
        return self.update()

    def update(self):
        installed = []
        installed.extend(self._install_testrunners())
        installed.extend(self._install_run_script())
        return installed

    def _install_testrunners(self):
        installed = []
        for package in self.wanted_packages:
            ws = self._working_set(package)
            package_ = ws.find(pkg_resources.Requirement.parse(package))
            extras = '[' + ','.join(package_.extras) + ']'

            options = self.testrunner_options.copy()
            options['eggs'] = package + extras

            recipe = zc.recipe.testrunner.TestRunner(
                self.buildout, '%s-%s' % (self.name, package), options)
            installed.extend(recipe.install())
        return installed

    def _install_run_script(self):
        bindir = self.buildout['buildout']['bin-directory']
        runners = ['%s-%s' % (self.name, package) for package
                        in self.wanted_packages]
        runners = [repr(os.path.join(bindir, runner)) for runner in runners]

        return zc.buildout.easy_install.scripts(
            [(self.script, 'z3c.recipe.compattest.runner', 'main')],
            self._working_set('z3c.recipe.compattest'),
            self.buildout['buildout']['executable'],
            bindir, arguments='%s, %s' % (self.options['max_jobs'],
                                          ', '.join(runners)))

    def _wanted_packages(self):
        projects = self.include
        for project in projects:
            for regex in self.exclude:
                if re.compile(regex).search(project):
                    projects.remove(project)
                    break
        return projects

    def _working_set(self, package):
        eggs = zc.recipe.egg.Egg(self.buildout, self.name, dict(eggs=package))
        _, ws = eggs.working_set()
        return ws
