import infrae.subversion
import os
import pkg_resources
import popen2
import re
import zc.buildout.easy_install
import zc.recipe.egg
import zc.recipe.testrunner


def string2list(string, default):
    result = string and string.split() or default
    return [item.strip() for item in result]


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

        self.script = self.options.get('script', 'test-%s' % self.name)

        self.svn_url = self.options.get('svn_url', None)
        if self.svn_url and self.svn_url[-1] != '/':
            self.svn_url += '/'
        self.svn_directory = self.options.get(
            'svn_directory', os.path.join(
            self.buildout['buildout']['parts-directory'], self.name))

    def install(self):
        if self.svn_url:
            if not os.path.exists(self.svn_directory):
                os.mkdir(self.svn_directory)
        return self.update()

    def update(self):
        installed = []

        if self.svn_url:
            zc.buildout.easy_install.distribution_cache = {}
            self._install_checkouts()

        installed.extend(self._install_testrunners())
        installed.extend(self._install_run_script())

        if self.svn_url:
            self._remove_develop_eggs()
            zc.buildout.easy_install.distribution_cache = {}

        return installed

    def _install_testrunners(self):
        installed = []
        for package in self.wanted_packages:
            try:
                ws = self._working_set(package)
                package_ = ws.find(pkg_resources.Requirement.parse(package))
                extras = '[' + ','.join(package_.extras) + ']'
            except zc.buildout.easy_install.MissingDistribution, e:
                if e.data[0].project_name == package and not self.svn_url:
                    # This package has a project in subversion but no
                    # release (yet). We'll ignore it for now.
                    print "No release found for %s. Ignoring." % package
                    self.wanted_packages.remove(package)
                    continue
                raise
            options = dict(eggs=package + extras)
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

    def _install_checkouts(self):
        self.develop_eggs = []

        eggdir = self.buildout['buildout']['develop-eggs-directory']
        egg_links = os.listdir(eggdir)
        installed_develop_eggs = [os.path.splitext(f)[0] for f in egg_links]

        checkout_list = []
        for package in self.wanted_packages:
            if package in installed_develop_eggs:
                continue
            working_copy = os.path.join(self.svn_directory, package)
            checkout_list.append('%s%s/trunk %s' % (self.svn_url, package,
                                                  package))
            self.develop_eggs.append(package)

        recipe = infrae.subversion.Recipe(self.buildout, self.name, dict(
            urls='\n'.join(checkout_list),
            location=self.svn_directory,
            as_eggs='true',
            no_warnings='true',
            ))
        recipe.newest = True
        recipe.update()

    def _remove_develop_eggs(self):
        eggdir = self.buildout['buildout']['develop-eggs-directory']
        for egg_link in os.listdir(eggdir):
            egg, _ = os.path.splitext(egg_link)
            if egg in self.develop_eggs:
                os.unlink(os.path.join(eggdir, egg_link))
