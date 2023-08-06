import os

import setuptools

from darcsver import darcsvermodule

class DarcsVer(setuptools.Command):
    description = "generate a version number from darcs history"
    user_options = [
        ('project-name', None, "name of the project as it appears in the project's release tags (default's the to the distribution name)"),
        ('version-file', None, "path to file into which the version number should be written (defaults to the package directory's _version.py)"),
        ('count-all-patches', None, "If true, count the total number of patches in all history.  If false, count the total number of patches since the most recent release tag."),
        ('quiet', 'q', "Be quiet (deprecated: use --loud instead)."),
        ('loud', 'v', "Be loud (the default is to be not-loud)."),
        ]

    def initialize_options(self):
        self.project_name = None
        self.version_file = None
        self.count_all_patches = None
        self.quiet = None
        self.loud = None

    def finalize_options(self):
        if self.project_name is None:
            self.project_name = self.distribution.get_name()

        if self.version_file is None:
            toppackage = ''
            # If there is a package with the same name as the project name and
            # there is a directory by that name then use that.
            packagedir = None
            if self.distribution.packages and self.project_name in self.distribution.packages:
                toppackage = self.project_name
                srcdir = ''
                if self.distribution.package_dir:
                    srcdir = self.distribution.package_dir.get(toppackage)
                    if not srcdir is None:
                        srcdir = self.distribution.package_dir.get('', '')
                packagedir = os.path.join(srcdir, toppackage)

            if packagedir is None or not os.path.isdir(packagedir):
                # Else, if there is a singly-rooted tree of packages, use the
                # root of that.
                if self.distribution.packages:
                    for package in self.distribution.packages:
                        if not toppackage:
                            toppackage = package
                        else:
                            if toppackage.startswith(package+"."):
                                toppackage = package
                            else:
                                if not package.startswith(toppackage+"."):
                                    # Not singly-rooted
                                    toppackage = ''
                                    break

                srcdir = ''
                if self.distribution.package_dir:
                    srcdir = self.distribution.package_dir.get(toppackage)
                    if srcdir is None:
                        srcdir = self.distribution.package_dir.get('', '')
                packagedir = os.path.join(srcdir, toppackage)

            self.version_file = os.path.join(packagedir, '_version.py')

    def run(self):
        if self.loud and not self.quiet:
            loud = True
        else:
            loud = False
        (rc, verstr) = darcsvermodule.update(self.project_name, self.version_file, self.count_all_patches, loud=loud, EXE_NAME="setup.py darcsver")
        self.distribution.metadata.version = verstr
