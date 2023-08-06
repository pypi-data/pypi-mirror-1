##########################################################################
# haufe.eggserver
# (C) 2008, Haufe Mediengruppe Freiburg, ZOPYX Ltd. & Co. KG
# Written by Andreas Jung
# Published under the Zope Public License V 2.1
##########################################################################s


import re
import os
import base64
import grok
import stat
import logging
from time import localtime, strftime
from zope.interface import Interface
from zope.interface import implements
from zope import schema
from zope.contenttype import guess_content_type
from util import *
import gocept.cache.method

LOG = logging.getLogger('haufe-eggsrv')


class ManageEggServer(grok.Permission):
    """ Generic manage permission """
    grok.name('haufe.eggserver.manage')


class IEggServer(Interface):

    title = schema.TextLine(title=u'Title of this instance', required=True)
    egg_directory = schema.TextLine(title=u'Path to local root directory for distribution files', required=True)


class eggserver(grok.Application, grok.Model):
    implements(IEggServer)
    egg_directory = '/'
    title = u'Title of your haufe.eggserver instance'


class EditForm(grok.EditForm):  
    grok.name('edit')
    grok.require('haufe.eggserver.manage')
    form_fields = grok.AutoFields(IEggServer)

    @grok.action('Apply changes')
    def applyChanges(self, **data):
        self.applyData(self.context, **data)
        self.redirect(self.url(self.context))

    @grok.action('Cancel')
    def returnToIndex(self, **data):
        self.redirect(self.url(self.context))


class Index(grok.View):
    grok.context(eggserver)

    def getPackageInfo(self):
        """ Return package infos as a list of dicts """
        result = list()

        for name in os.listdir(self.context.egg_directory):
            fullpath = os.path.join(self.context.egg_directory, name)
            if not os.path.isdir(fullpath):
                continue

            result.append(dict(name=name,
                         ))
        result.sort(lambda x,y: cmp(x['name'], y['name']))
        return result


class FileUpload(grok.View):
    """ Implements the setuptools upload protocol """

    grok.context(eggserver)
    grok.name('file_upload')

    def render(self):
        package = self.request['name']
        package_name = self.request['content'].filename
        dest_name = os.path.join(self.context.egg_directory, package, package_name)
        if os.path.exists(dest_name):
            self.request.response.setStatus(409) # Conflict
            return

        if not os.path.exists(os.path.dirname(dest_name)):
            os.makedirs(os.path.dirname(dest_name))
        open(dest_name, 'wb').write(self.request['content'].read())
        LOG.info('Uploaded %s' % dest_name)


class Download(grok.View):
    """ Download of a distribution file """

    def render(self):
        fullpath = os.path.join(self.context.egg_directory, self.request['package'], self.request['filename'])
        if os.path.exists(fullpath):
            mt, version = guess_content_type(fullpath)
            if mt in ('text/x-unknown-content-type',):
                mt = 'application/octet-stram'

            self.response.setHeader('content-type', mt)
            self.response.setHeader('content-disposition', 'attachment; filename="%s"' % self.request['filename'])
            return file(fullpath, 'rb')
        else:
            self.response.setStatus(404)


class Master(grok.View):
    """ The master page template macro """
    # register this view for all objects
    grok.context(Interface)


class Metadata(grok.View):
    """ Show package metadata """

    def getMetadata(self):
        from parse_pkg_info import parse_metadata
        egg_filename = os.path.join(self.context.egg_directory, 
                                    self.request['package'], 
                                    self.request['filename'])
        return parse_metadata(egg_filename)

    def rest2html(self, description):
        import rest
        description = ' ' * 8 + description
        description = '\n'.join([l[8:].rstrip() for l in description.split('\n')])
        return rest.HTML(description)


class Simple(grok.View):
    """ Provide a simple flat listing to be used with 
        easy_install/buildout.
    """

    # cache the listing for 300 seconds
    @gocept.cache.method.Memoize(300, ignore_self=True)
    def get_files(self):

        files = list()
        for dirname, dirnames, filenames in os.walk(self.context.egg_directory):
            for name in filenames:
                fullpath = os.path.join(dirname, name)
                if not os.path.isfile(fullpath):
                    continue

                package = dirname.replace(self.context.egg_directory + '/', '') 
                files.append(dict(package=package, name=name))
        files.sort(lambda x,y: cmp(x['name'], y['name'])) 
        return files


class PackageInfo(object):

    def __init__(self):
        self.releases = list()
        self.files = dict()


class ShowPackage(grok.View):
    grok.context(eggserver)

    def getPackageInfo(self):
        """ Return package infos as a list of dicts """

        result = list()
        package_dir = os.path.join(self.context.egg_directory, self.request['package'])

        release_packages = PackageInfo()
        dev_packages = PackageInfo()
        dev_packages.files['dev'] = list()

        for name in os.listdir(package_dir):
            fullpath = os.path.join(package_dir, name)

            if 'dev_' in name:
                # development package

                dev_packages.files['dev'].append(dict(name=name,
                                                      size=os.stat(fullpath)[stat.ST_SIZE],
                                                      mtime=strftime('%d.%m.%Y %H:%M:%S', localtime(os.stat(fullpath)[stat.ST_MTIME]),
                                                      )))

            else:
                # production distribution file
                version = None
                regex = re.compile(r'-(\d*.\d*.\d*)')
                mo = regex.search(name)
                if mo:
                    version = mo.group(1)
                else:
                    regex = re.compile(r'-(\d*.\d*)')
                    mo = regex.search(name)
                    if mo:
                        version = mo.group(1)


                if not version in release_packages.releases:
                    release_packages.releases.append(version)
                    release_packages.files[version] = list()

                release_packages.files[version].append(dict(name=name,
                                                            size=os.stat(fullpath)[stat.ST_SIZE],
                                                            mtime=strftime('%d.%m.%Y %H:%M:%S', localtime(os.stat(fullpath)[stat.ST_MTIME]),
                                                            )))
        release_packages.releases.sort()
        release_packages.releases.reverse()
        dev_packages.files.get('dev', []).sort()
        dev_packages.files.get('dev', []).reverse()
        return dict(releases=release_packages, dev=dev_packages)


class UploadHandler(grok.XMLRPC):
    """ XML-RPC upload handler for distribution files """

    def handle_upload(self, package, package_name, package_data, username):
        """ Upload a  package to the index server:
            'package' - dotted name of the package (e.g. haufe.foobar)
            'package_name' - distribution file name (e.g. haufe.foobar-1.0.0.tar.gz)
            'package_data' - binary data for distribution file (base64-encoded)
        """

        package_name = os.path.basename(package_name)
        dest_name = os.path.join(self.context.egg_directory, package, package_name)
        if os.path.exists(dest_name):
            raise ValueError('%s:%s already exists' % (package, package_name))

        if not os.path.exists(os.path.dirname(dest_name)):
            os.makedirs(os.path.dirname(dest_name))
        open(dest_name, 'wb').write(base64.decodestring(package_data))
        LOG.info('Uploaded %s by %s' % (dest_name, username))

