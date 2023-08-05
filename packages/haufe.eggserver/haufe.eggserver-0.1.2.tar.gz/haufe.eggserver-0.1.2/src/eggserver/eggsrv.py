
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


class Master(grok.View):
    """ The master page template macro """
    # register this view for all objects
    grok.context(Interface)


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

        for name in os.listdir(package_dir):
            fullpath = os.path.join(package_dir, name)

            if '-dev' in name:
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

