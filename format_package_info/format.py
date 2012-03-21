import os
import yum

class Format(object):
    def __init__(self, filepath):
        self.filepath = filepath
        self._packages = []
        self._package_data = {}
        self.yum_cache_path = '.yum'

    def parse(self):
        f = open(self.filepath, "r")
        for l in f:
            words = l.split(" ")
            pkgname = words[0].rstrip()
            if pkgname:
                self._packages.append(pkgname)
                self._package_data[pkgname] = {'url': '',
                                               'license': ''
                                              }

        f.close()

        self._packages.sort()

    def populate_package_data(self):
        yb = yum.YumBase()
        yb.doConfigSetup('yum.conf', root=os.getcwd(), init_plugins=False)
        for r in yb.repos.findRepos('*'):
            if r.id in ['rawhide']:
                r.enable()
            else:
                r.disable()

        yb._getRepos(doSetup = True)
        yb._getSacks(['x86_64', 'noarch'])
        yb.doRepoSetup()
        yb.conf.cache = 1
        pkgs = yb.pkgSack.returnPackages()
        for pkg in pkgs:
            if pkg.name in self._package_data:
                pd = self._package_data[pkg.name]
                pd['url'] = pkg.url
                pd['license'] = pkg.license

    def print_formatted_packages(self):
        for pkgname in self._packages:
            pd = self._package_data[pkgname]
            print "    %li"
            url = pd['url']
            if not url:
                url = '#needs_to_be_filled_in'
            license = pd['license']
 
            print '      = link_to "%s", "%s"' % (pkgname, url)
            if license:
                print "      (%s)" % license

    def run(self):
        self.parse()              
        self.populate_package_data()
        self.print_formatted_packages()
