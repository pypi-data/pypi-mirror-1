#!/usr/bin/env python
#
# Copyright (c) 2008-2009 by Enthought, Inc.
# All rights reserved.

import os, sys
import shutil
import subprocess
import zipfile
from distutils import log
from distutils.command.clean import clean
from distutils.errors import DistutilsSetupError

from setuptools import Command


DOC_DIR = os.path.join(os.path.abspath(os.getcwd()), 'docs')
SOURCE_DIR = os.path.join(DOC_DIR, 'source')
ZIP_FILE_NAME = 'html.zip'
HTML_ZIP = os.path.join(DOC_DIR,  ZIP_FILE_NAME)
BUILD_DIR = os.path.join(os.path.abspath(os.getcwd()), 'build')
TARGET_DIR = os.path.join(BUILD_DIR, 'docs')

def is_sphinx_installed():
    """
    Check to see if Sphinx is installed (based on a simple import).
    """
    required_sphinx_version = "0.4.2"
    try:
        import sphinx
        # FIXME: Once verlib is in the stdlib, use verlib's comparison
        if sphinx.__version__ < "required_sphinx_version":
            log.warn('Sphinx install of version >=%s could not be verified.'
                     % required_sphinx_version)
        return True
    except ImportError:
        return False


def create_html_zip(target, commit):
    """Create html_docs.zip in target directory. This is useful if the rst
    source files have recently been updated and a new zipped html file needs to
    be created for distribution. If commit is 1, html_docs.zip will replace
    the existing file in docs/ and be checked in to svn. This will only work if
    the user has commit access to svn.enthought.com/enthought.
    """
    html_source = os.path.join(TARGET_DIR, 'html')
    target_file = os.path.join(target, ZIP_FILE_NAME)

    if not os.path.exists(target):
        os.makedirs(target)
    if os.path.exists(target_file):
        os.remove(target_file)

    # ZIP_DEFLATED actually compresses the archive. However, there will be a
    # RuntimeError if zlib is not installed, so we check for it. ZIP_STORED
    # produces an uncompressed zip, but does not require zlib.
    try:
        zf = zipfile.ZipFile(target_file, 'w', compression=zipfile.ZIP_DEFLATED)
    except RuntimeError:
        zf = zipfile.ZipFile(target_file, 'w', compression=zipfile.ZIP_STORED)

    # "Subract" the root of the path to a file so that only the part of the
    # path necessary for the archive is left. Was originally in make_docs.py.
    # There may be a better way, but this works.
    length = len(os.path.abspath(html_source))
    subtract_base = lambda root: root[length+1:]
    for root, dirs, files in os.walk(html_source):
        baseless = subtract_base(root)
        if not '.doctrees' in baseless.split(os.sep):
            for f in files:
                zf.write(os.path.join(root, f), os.path.join('html',
                    baseless, f))
    zf.close()

    log.info("%s now ready." % target_file)

    if commit == 1:
        message = "Updating html docs zip file."
        subprocess.call(['svn', 'ci', zf.filename, '-m', message])
#        subprocess.call(['svn', 'st'])#, zf.filename])

def unzip_html_docs(src_path, dest_dir):
    """ Given a path to a zipfile, extract its contents to a given 'dest_dir'.
    """
    file = zipfile.ZipFile(src_path)
    for name in file.namelist():
        cur_name = os.path.join(dest_dir, name)
        cur_name = cur_name.replace('/', os.sep)
        if not os.path.exists(os.path.dirname(cur_name)):
            os.makedirs(os.path.dirname(cur_name))
        if not name.endswith('/'):
            out = open(cur_name, 'wb')
            out.write(file.read(name))
            out.flush()
            out.close()
    file.close()

def show_formats():
    DOC_FORMATS = {
        'html': (BuildDocs, [], "(default) create folder 'build/docs/html' "
            "with html documentation"),
        'latex': (BuildDocs, [], "create folder 'build/docs/latex' with latex "
            "source files "),
        'pdf': (BuildDocs, [], "make pdf file from generated latex in "
            "'build/docs/latex'. requires latex install with pdflatex command"),
        'html,latex,...': (None, [], "generate more than one format"),
        'all': (BuildDocs, [], "build html, latex, and pdf")
        }

    from distutils.fancy_getopt import FancyGetopt
    formats = []
    for format in DOC_FORMATS.keys():
        formats.append(("formats=" + format, None, DOC_FORMATS[format][2]))
    formats.sort()
    pretty_printer = FancyGetopt(formats)
    pretty_printer.print_help("Available doc formats:")

def get_source_dirs(doc_dir):
    source_dirs = []
    for root, dirnames, filenames in os.walk(doc_dir):
        if 'conf.py' in filenames:
            source_dirs.append(os.path.abspath(root))
            log.info('Using source directory %s' % root)
    return source_dirs

def list_docs_data_files(build_docs_loc, docs_location):
    """ List the files to add to a project by inspecting the documentation
        directory. This works only if called after the build step, as the files
        have to be built.

        returns a list of (install_dir, [data_files, ]) tuples.
    """
    if docs_location is None:
        docs_location = 'docs'
    return_list = []
    for root, dirs, files in os.walk(build_docs_loc, topdown=True):
        # Modify inplace the list of directories to walk
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        if len(files) == 0:
            continue
        install_dir = root.replace(build_docs_loc, docs_location)
        return_list.append(
            (install_dir, [os.path.join(root, f) for f in files]))
    return return_list


class BuildDocs(Command):

    description = "Build documentation from restructured text sources."

    user_options = [
        ('formats=', None, 'documentation formats to generate (comma-separated '
            'list)'),
        ]

    help_options = [
        ('help-formats', None, 'list available documentation formats',
            show_formats),
        ]

    def run(self):
        if is_sphinx_installed():
            from sphinx.application import Sphinx
            from sphinx.util.console import nocolor

            # Windows' poor cmd box doesn't understand ANSI sequences
            if not sys.stdout.isatty() or sys.platform == 'win32':
                nocolor()

            # Check to see if version information is provided in setup.py
            # If it is, it will override version information in conf.py.
            conf_overrides = {}
            version = self.distribution.get_version()
            if version != "0.0.0":
                conf_overrides['version'] = version
                conf_overrides['release'] = version

            for i in range(len(self.source_dirs)):
                for format in self.formats:
                    try:
                        builder_target = os.path.join(self.target_dir, format,
                            self.projects[i])
                        doctree_dir = os.path.join(builder_target, '.doctrees')

                        self.mkpath(doctree_dir)

                        # The sphinx interface requires 7 arguments: sourcedir,
                        # confdir, outdir, doctreedir, buildername,
                        # confoverrides, and status
                        app = Sphinx(self.source_dirs[i], self.source_dirs[i],
                            builder_target, doctree_dir, format, conf_overrides,
                            self.status_stream
                            )
                        app.builder.build_update()
                        if self.pdf_build and format == 'latex':
                            try:
                                os.chdir(builder_target)
                                subprocess.call(["make", "all-pdf"])
                                log.info("PDF doc created in %s."
                                    % builder_target)
                            except Exception, e:
                                log.error(e)

                    except IOError, e:
                        log.warn(e)

                    except Exception, e:
                        log.error('Unable to generate %s docs.' % format)
                        if format == 'html' and len(self.formats) == 1:
                            log.info("Installing %s html documentation from zip"
                                " file.\n" % self.distribution.get_name())
                            unzip_html_docs(HTML_ZIP, TARGET_DIR)

        else:
            if 'html' not in self.formats:
                log.error("Sphinx must be installed for RST doc conversion.")
            elif len(self.formats) > 1:
                # Unzip the docs into the 'html' folder.
                log.info("Installing %s html documentation from zip file. Cannot"
                    " generate other formats without Sphinx install.\n" \
                    % self.name)
                unzip_html_docs(HTML_ZIP, TARGET_DIR)
            else:
                # Unzip the docs into the 'html' folder.
                log.info("Installing %s html documentation from zip file.\n" \
                    % self.name)
                unzip_html_docs(HTML_ZIP, TARGET_DIR)

        # Using extend so the existing data_files doesn't get replaced
        if self.distribution.docs_in_egg:
            # This check is needed because of a setuptools or (numpy?) distutils bug that
            # is causing the easy_install process to stop adding subpackages. This may be
            # because setupdocs is being required by multiple packages in a dependency
            # chain; but really, who knows.
            if not self.distribution.data_files:
                self.distribution.data_files = []

            if self.distribution.docs_in_egg_location is None:
                doc_files = list_docs_data_files(self.target_dir,
                                        self.distribution.docs_dest)
            else:
                doc_files = list_docs_data_files(self.target_dir,
                                        self.distribution.docs_in_egg_location)

            self.distribution.data_files.extend(doc_files)


    def initialize_options (self):
        self.formats = None
        self.check = 0
        self.pdf_build = False
        self.source_dirs = None

    def finalize_options (self):
        self.name = self.distribution.get_name()
        self.ensure_string_list('formats')
        if self.formats == ['all']:
            self.formats = ['html', 'latex']
            self.pdf_build = True
        if self.formats is None:
            self.formats = ['html']
        if 'pdf' in self.formats:
            self.formats.remove('pdf')
            if 'latex' not in self.formats:
                self.formats.append('latex')
            self.pdf_build = True
        if self.source_dirs is None:
            if getattr(self.distribution, 'docs_source', None) is None:
                self.source_dirs = get_source_dirs(DOC_DIR)
            else:
                self.source_dirs = get_source_dirs(self.distribution.docs_source)

        if getattr(self.distribution, 'docs_dest', None) is None:
            self.target_dir = TARGET_DIR
        else:
            self.target_dir = os.path.join(BUILD_DIR, self.distribution.docs_dest)

        # This looks to see if there are multiple directories under docs/source
        self.projects = []
        for source in self.source_dirs:
            project = source.split(os.sep)[-1]
            if project != 'source':
                self.projects.append(project)
            else:
                self.projects = ['']
        self.status_stream = sys.stdout


class DistDocs(Command):

    description = "create a zip file of the html documentation"

    user_options = [
        ('dist-dir=', 'd', 'specify directory for zip output'),
        ('checkin', 'c', 'replace existing zip file and checkin to svn (only '
            'works if you have commit access)'),
        ('update', 'u', 'update the docs on the code.enthought.com website'),
        ('repo=', 'r', 'repository where web docs will be checked out and '
            'updated (default set in setup.cfg)'),
        ('ssh-server=', 's', 'server to log into when updating remote docs '
            ' (default set in setup.cfg)'),
        ('remote-dir=', 't', 'location of docs on remote server '
            ' (default set in setup.cfg)'),
        ('username=', None, 'username to specify for ssh login when updating '
            'CEC'),
        ]

    boolean_options = ['checkin', 'update']

    def run(self):
        if not is_sphinx_installed():
            log.error("Sphinx must be installed to build the docs for the "
                "zip-file.")
        else:
            try:
                if self.update == 1:
                    self.update_docs()
                else:
                    self.run_command('build_docs')
                    create_html_zip(self.dist_dir, self.checkin)
            except Exception, e:
                log.error(e)

    def update_docs(self):
        checkout_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)),
            TARGET_DIR)
        print self.repo
        if os.path.exists(checkout_dir):
            shutil.rmtree(checkout_dir)
        try:
            log.info("Getting fresh checkout from repository...")
            co_retcode = subprocess.call(['svn', 'co', self.repo, checkout_dir,
                '-q'])
            if co_retcode != 0:
                raise RuntimeError("subversion checkout failed.")
        except Exception, e:
            log.error(e)
            return

        self.reinitialize_command('build_docs', formats='all')
        self.run_command('build_docs')

        # Removed everything from the latex directory except the PDF, which
        # we want to check in.
        for root, dirs, files in os.walk(checkout_dir):
            # We don't want to remove the .svn directories, either.
            if '.svn' in root:
                continue
            for file in files:
                if 'latex' in root and not file.endswith('.pdf'):
                    os.remove(os.path.join(root, file))

        st_proc = subprocess.Popen(['svn', 'st', checkout_dir],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        st_proc.wait()
        st_out = st_proc.communicate()[0].split('\n')

        for st_message in st_out:
            if '.doctrees' not in st_message and st_message.startswith('?'):
                subprocess.call(['svn', 'add', st_message.split()[1]])

        try:
            ci_proc = subprocess.call(['svn', 'ci', checkout_dir, '-m',
                'Checking in html docs from setup.py command'])
            if ci_proc != 0:
                raise RuntimeError("Unable to perform svn commit.")
        except Exception, e:
            log.error(e)

        if self.username is None:
            self.username = raw_input("Please enter username for ssh access: ")
        try:
            ssh_proc = subprocess.call('ssh %s@%s " \
                cd %s \
                && svn up \
                && chmod -R g+w * \
                && chgrp -R apache *"' % (self.username, self.ssh_server,
                    self.remote_dir), shell=True)

            if ssh_proc != 0:
                raise RuntimeError("Update via ssh failed.")
            else:
                log.info("Website docs updated.")

        except:
            log.error("Unable to update the website via ssh.")

    def initialize_options(self):
        self.dist_dir = None
        self.checkin = 0
        self.update = 0
        self.username = None
        self.repo = None
        self.ssh_server = None
        self.remote_dir = None

    def finalize_options(self):
        if self.dist_dir is None:
            self.dist_dir = 'dist'
        if self.checkin:
            self.dist_dir = 'docs'
        if self.username is None:
            self.username = self.distribution.ssh_username
        if self.repo is None:
            self.repo = self.distribution.html_doc_repo
        if self.ssh_server is None:
            self.ssh_server = self.distribution.ssh_server
        if self.remote_dir is None:
            self.remote_dir = self.distribution.ssh_remote_dir


class MyClean(clean):
    """ A hook to remove the generated documentation when cleaning.

        We subclass distutils' clean command because neither numpy.distutils
        nor setuptools has an implementation.

    """

    def run(self):
        clean.run(self)
        if os.path.exists('build/docs'):
            log.info("Removing '%s' (and everything under it)" %
                                            'build/docs')
            shutil.rmtree('build/docs')


def check_bool(dist, attr, value):
    """Verify that value is True, False, 0, or 1"""
    if bool(value) != value:
        raise DistutilsSetupError(
            "%r must be a boolean value (got %r)" % (attr, value)
        )

def check_string(dist, attr, value):
    if not isinstance(value, basestring):
        raise DistutilsSetupError("%s must be a string" % attr)
