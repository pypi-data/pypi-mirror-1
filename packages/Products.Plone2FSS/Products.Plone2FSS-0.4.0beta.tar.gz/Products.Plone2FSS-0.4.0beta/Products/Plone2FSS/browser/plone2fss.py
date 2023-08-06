# -*- coding: utf-8 -*-

import os

from zope.interface import implements
from zope.component import getUtility
from Products.Five.browser import BrowserView
from Products.CMFCore import utils
from Products.CMFCore.utils import getToolByName

from Products.Archetypes.Field import FileField, StringField, TextField

from Products.Archetypes.Storage import AttributeStorage
from Products.Archetypes.Storage.annotation import AnnotationStorage

try:
    from iw.fss.FileSystemStorage import FileSystemStorage
    from iw.fss.interfaces import IConf
    eggified_version = True
except ImportError:
    # May be plone 2.5.5
    from Products.FileSystemStorage.FileSystemStorage import FileSystemStorage
    eggified_version = False

from DateTime import DateTime

STD_CONTENT_TYPE_ERROR = "Sorry, don't know how to export a %s content type to a valid FSS format"

class Plone2FSS(BrowserView):
    """View for the form that dump contents in a valid FSS format onto server filesystem"""
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.default_content_types = ['File', 'Image', 'News Item']
        self.default_image_field_formats = ['listing','icon','tile','thumb','mini','preview','large']
        request.set('disable_border', True)


class Plone2FSSExport(BrowserView):
    """View for the export procedure"""
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.default_content_types = ['File', 'Image', 'News Item']
        self.default_image_field_formats = ['listing','icon','tile','thumb','mini','preview','large']
    
    def __call__(self):
        request = self.request        
        context = self.context
        putils = getToolByName(context, 'plone_utils')
        
        if request.form.get('to_fss'):
            content_types = request.form.get('content_types', self.default_content_types)
            sub_objects = self._getSubObjects(content_types)
            filesystem_output_dir = request.form.get('filesystem_output_dir', None)
            if not filesystem_output_dir:
                raise "Please, specify an output filesystem directory"
            strategy_type = request.form.get('strategy_type')
            
            cnt = self.export(sub_objects, filesystem_output_dir, strategy_type)
            putils.addPortalMessage("%s contents exported." % cnt)
        elif request.form.get('attr2fss'):
            content_types = request.form.get('content_types', self.default_content_types)
            sub_objects = self._getSubObjects(content_types)
            cnt = self._migrateToFSStorage(sub_objects)
            if cnt==0:
                putils.addPortalMessage("No contents storage changed. Is FileSystemStorage installed? Are content types using it?")
            else:
                putils.addPortalMessage("%s contents exported from AttributeStorage to FileSystemStorage." % cnt)
        request.response.redirect(context.absolute_url())
        
        
    def _getSubObjects(self, content_types):
        """Query the catalog to get all valid content types below the current level"""
        context = self.context
        physical_path = '/'.join(context.getPhysicalPath())
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(portal_type=content_types,
                          path=physical_path)
        return results

    def export(self, brains, filesystem_output_dir, strategy_type='directory'):
        '''
        @param brains: brain objects to export
        @param filesystem_output_dir: where store the files
        @return: a count of exported objects
        '''
        try:
            os.makedirs(filesystem_output_dir)
        except OSError:
            pass
        for brain in brains:
            print "Processing %s (%s)" % (brain.getPath(), brain.portal_type)
            if strategy_type=='flat':
                self._exportStrategyFlat(brain, filesystem_output_dir)
            elif strategy_type=='directory':
                self._exportStrategyDirectory(brain, filesystem_output_dir)
            elif strategy_type=='site1':
                self._exportStrategySite1(brain, filesystem_output_dir)
            elif strategy_type=='site2':
                raise ValueError("Strategy %s is not suppoted yet... Sorry!" % strategy_type)
            else:
                raise ValueError("Strategy not know: %s" % strategy_type)
        return len(brains)

    @classmethod
    def _createFile(cls, content, path):
        fh = open(path, 'w')
        fh.write(content)
        fh.close()

    def _createImageFormat(self, obj, brain, format, fs_path):
        """Create on the filesystem the exported version of a valid imae format"""
        traversed = obj.restrictedTraverse(brain.getPath()+'/image_%s' % format, default=None)
        if not traversed:
            print "The object at %s (%s) doesn't have the %s image format" % (brain.getPath(),
                                                                              obj.portal_type,
                                                                              format)
            return
        self._createFile(str(traversed.data), os.path.join(fs_path))

    def _exportStrategyFlat(self, brain, filesystem_output_dir):
        """
        Export an object in a flat-strategy format.
        
        By the way... for what stupid reason are you using this strategy?! :-)

        This is uidoftheobject_xxx for all in the same directory...

        @param brain: the brain from which get the file content
        @param filesystem_output_dir: directory where to store the data

        """

        obj = brain.getObject()
        uid = obj.UID()
        putils = getToolByName(self.context, 'plone_utils')

        if obj.portal_type=='File':
            if obj.restrictedTraverse(brain.getPath()+'/file',default=None):
                self._createFile(str(obj.getFile().data),
                                os.path.join(filesystem_output_dir,uid+'_file'))
        elif obj.portal_type=='Image' or obj.portal_type=='News Item':
            if obj.restrictedTraverse(brain.getPath()+'/image',default=None):
                self._createFile(str(obj.restrictedTraverse(brain.getPath()+'/image').data),
                                os.path.join(filesystem_output_dir,uid+'_image'))
                
                image_field_formats = self.request.get('image_field_formats', self.default_image_field_formats)
                for format in image_field_formats:
                    self._createImageFormat(obj, brain, format,
                                            os.path.join(filesystem_output_dir,uid+'_image_%s' % format))
        else:
            raise TypeError(STD_CONTENT_TYPE_ERROR)
        print "Exported %s to %s" % (uid, os.path.join(filesystem_output_dir))


    def _exportStrategyDirectory(self, brain, filesystem_output_dir):
        '''
        Export an object in a directory-strategy format
        This is ui/uido/uidoftheobject_xxx
        @param brain: the brain from which get the file content
        @param filesystem_output_dir: directory where to store the data
        
            Lets generate the test parameters.
            First the mockup brain
            >>> class MockBrain(object):
            ...     def __init__(self):
            ...         self.portal_type = 'File'
            ...         self._uid = 'abcd'*9
            ...     def UID(self):
            ...         return self._uid
            
            Then a temp directory where work onto
            >>> from temfile import mkdtemp
            >>> filesystem_output_dir = mkdtemp()
        '''
        obj = brain.getObject()
        uid = obj.UID()
        d1 = uid[:2]
        d2 = uid[:4]
        putils = getToolByName(self.context, 'plone_utils')
        try:
            os.mkdir(os.path.join(filesystem_output_dir,d1))
        except OSError:
            pass
        try:
            os.mkdir(os.path.join(filesystem_output_dir,d1,d2))
        except OSError:
            pass
        if obj.portal_type=='File':
            if obj.restrictedTraverse(brain.getPath()+'/file',default=None):
                self._createFile(str(obj.getFile().data),
                                os.path.join(filesystem_output_dir,d1,d2,uid+'_file'))
        elif obj.portal_type=='Image' or obj.portal_type=='News Item':
            if obj.restrictedTraverse(brain.getPath()+'/image',default=None):
                self._createFile(str(obj.restrictedTraverse(brain.getPath()+'/image').data),
                                os.path.join(filesystem_output_dir,d1,d2,uid+'_image'))

                image_field_formats = self.request.get('image_field_formats', self.default_image_field_formats)
                for format in image_field_formats:
                    self._createImageFormat(obj, brain, format,
                                            os.path.join(filesystem_output_dir,d1,d2,uid+'_image_%s' % format))
        else:
            raise TypeError(STD_CONTENT_TYPE_ERROR)
        print "Exported %s to %s" % (uid, os.path.join(filesystem_output_dir,d1,d2))


    def _exportStrategySite1(self, brain, filesystem_output_dir):
        '''
        Export an object in a site1-strategy format
        This is:

        plonedir1[/plonedir2/]/objectid[/image|file]/osfilename

        @param brain: the brain from which get the file content
        @param filesystem_output_dir: directory where to store the data
        
        TODO: some doctest please!
        '''
        obj = brain.getObject()
        path = brain.getPath().split("/")[2:]
        uid = obj.UID()

        dirpath = os.path.join(filesystem_output_dir, *path)
        try:
            os.makedirs(dirpath)
        except OSError:
            pass
        
        if brain.portal_type=='File':
            ct_type='file'
            try:
                fileContent = str(obj.getFile().data)
            except AttributeError:
                fileContent = None
            
            dirpath2 = os.path.join(dirpath, ct_type)
            try:
                os.makedirs(dirpath2)
            except OSError:
                pass      

            if not fileContent or not obj.getFilename():
                print "Skipping %s" % brain.getPath()
                return
    
            self._createFile(fileContent,
                os.path.join(dirpath2, obj.getFilename(ct_type)))

        elif brain.portal_type=='Image' or brain.portal_type=='News Item':
            image_field_formats = self.request.get('image_field_formats', self.default_image_field_formats)
            ct_types = ["image_%s" % x for x in image_field_formats]
            ct_types = ['image'] + ct_types
            for ct_type in ct_types:
                try:
                    fileContent = str(obj.restrictedTraverse(brain.getPath()+'/%s' % ct_type).data)
                except AttributeError:
                    fileContent = None

                dirpath2 = os.path.join(dirpath, ct_type)
                try:
                    os.makedirs(dirpath2)
                except OSError:
                    pass    

                if not fileContent or not obj.getFilename('image'):
                    print "Skipping %s (%s)" % (brain.getPath(), ct_type)
                    continue

                self._createFile(fileContent,
                    os.path.join(dirpath2, obj.getFilename('image')))

        else:
            raise TypeError(STD_CONTENT_TYPE_ERROR)

        print "Exported %s to %s" % (uid, dirpath)


    def _migrateToFSStorage(self, sub_objects):
        """
        This code is originally taken from the "migrationExample" original iw.fss script.
        
        Migrate File and Images FileFields to FSStorage
        
        /!\ Assertion is made that the schema definition has been migrated to define
        FSS as storage for interested fields.
        
        Return the number of touched contents.
        """
        if eggified_version:
            try:
                # BBB: this seems useless
                conf = getUtility(IConf, "globalconf")()        
            except AttributeError:
                raise ValueError, "Install and configure FileSystemStorage first!"

        brains = sub_objects

        # this defines are here to avoid instantiating a new one for each file
        # it is known to be harmless with those storages
        attr_storage = AttributeStorage()
        fss_storage = FileSystemStorage()
        # BBB: is safe again doing this for AnnotationStorage?
        ann_storage = AnnotationStorage()
        
        cnt = 0
        for b in brains:
            o = b.getObject()
            print '/'.join(o.getPhysicalPath()), ":"
    
            # ensure we have an UID
            # it should not happen on a standard plone site, but I've met the case
            # with some weird custom types
            # the UID code was valid on a Plone 2.1.2 bundle (AT 1.3.7)
            if o.UID() is None:
                o._register()
                o._updateCatalog(o.aq_parent)
                print "UID was None, set to: %s" % o.UID()
    
            changed = False
            for f in o.Schema().fields():
                # visit only FileFields with FileSystemStorage
                if not isinstance(f, FileField):
                    continue
                storage = f.getStorage()
                if not isinstance(storage, FileSystemStorage):
                    continue
                
                name = f.getName()
                print "'%s'" % name
                
                # skip if field has already a content
                if f.get_size(o) != 0:
                    print "already set"
                    continue
    
                # get content from old storage and delete old storage
                try:
                    content = attr_storage.get(name, o)
                    attr_storage.unset(name, o)
                except AttributeError:
                    try:
                        content = ann_storage.get(name, o)
                        ann_storage.unset(name, o)
                    except AttributeError:
                        print "No old value"
                        continue
                
                # no more possible exception
                changed = True
                
                fss_storage.initializeField(o, f) #FIXME: really needed?
                f.set(o, content)

                # unset empty files, this avoid empty files on disk
                if f.get_size(o) == 0:
                    print "unset"
                    f.set(o, "DELETE_FILE")
                    
                print "\n"
                
            if changed:
                cnt+=1

        return cnt


