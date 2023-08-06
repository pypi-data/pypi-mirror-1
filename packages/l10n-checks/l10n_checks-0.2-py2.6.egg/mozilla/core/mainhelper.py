import os
import re
from silme.core import Package, EntityList, Structure
from silme.diff.package import *

def read_and_compare_source(optionpack, locale, localediffpackage,
                            localel10npackage, referencel10npackage,
                            l10npackagesreference):
    '''
    Method for importing files and folders to Silme-objects and diffing them.
    @param optionpack: instance of mozilla.core.main.CompareInit
    @param locale: the locale to compare
    @param localediffpackage: PackageDiff for the given locale
    @param localel10npackage: Package for the given locale
    @param referencel10npackage: (sub)Package for the reference locale
    @param l10npackagesreference: whole Package for reference locale
    '''
    for dir in optionpack.dirs:
      if (not dir['optional']) or (optionpack.force) or (dir['locales'] is None) or (locale in dir['locales']):
        path = os.path.split(dir['dir'])
        # Read reference Package
        if l10npackagesreference.has_package(path[1]):
          l10npackagereference = l10npackagesreference.package(path[1])
        else:
          if optionpack.filter_py is not None:
            filter = { 'filter' : optionpack.filter_py, 'relativepath' : '',
                      'module' : dir['dir']}
          else:
            filter = None
          '''en-US needs special treatment because of the file structure of "
          dir/locales/en-US" and not "locale/dir" like for other locales'''
          try:
            if not optionpack.forcelocaledir and optionpack.reference == 'en-US' and os.path.exists(os.path.join(dir['path'],
                                                             dir['dir'],
                                                             'locales', optionpack.reference)):
              l10npackagereference = \
              optionpack.rcsClient.get_package(os.path.join(dir['path'],
                                                               dir['dir'],
                                                               'locales',
                                                               optionpack.\
                                                               reference),
                                       object_type=optionpack.objectType,
                                       filter=filter)
            else:
              l10npackagereference = \
              optionpack.rcsClient.\
              get_package(os.path.join(optionpack.l10nbase,
                                          optionpack.reference,
                                          dir['dir']),
                             object_type=optionpack.objectType,
                             filter=filter)
          except OSError, e:
            l10npackagereference = Package()
        # Read Package for locale
        if optionpack.filter_py is not None:
          filter = { 'filter' : optionpack.filter_py, 'relativepath' : '',
                    'module' : dir['dir']}
        else:
          filter = None
        if not optionpack.forcelocaledir and  locale == 'en-US' and os.path.exists(os.path.join(dir['path'],
                                                             dir['dir'],
                                                             'locales', locale)):
          try:
            l10npackagelocale = \
            optionpack.rcsClient.get_package(os.path.join(dir['path'],
                                                             dir['dir'],
                                                             'locales', locale),
                                                object_type=optionpack.objectType,
                                                filter=filter)
          except OSError, e:
            l10npackagelocale = Package()
          l10npackagelocale.id = path[1]+'/locales/'+locale
        else:
          try:
            l10npackagelocale = \
            optionpack.rcsClient.get_package(os.path.join(optionpack.l10nbase,
                                                             locale,
                                                             dir['dir']),
                                                object_type=optionpack.objectType,
                                                filter=filter)
          except OSError, e:
            l10npackagelocale = Package()
            l10npackagelocale.id = path[1]
        l10ndiffpackage = l10npackagelocale.diff(l10npackagereference,
                           values=optionpack.values, flags=optionpack.flags)
        localediffpackage.add_package(l10ndiffpackage, path[0])
        localel10npackage.add_package(l10npackagelocale, path[0])
        l10npackagereference.id = l10npackagelocale.id
        if not referencel10npackage.has_package(l10npackagereference):
          referencel10npackage.add_package(l10npackagereference, path[0])
    return localediffpackage, localel10npackage, referencel10npackage


def read_and_compare_file(optionpack, locale, localediffpackage,
                            localel10npackage, referencel10npackage,
                            l10npackagesreference):
    '''
    Method for importing files to Silme-objects and diffing them.
    @param optionpack: instance of mozilla.core.main.CompareInit
    '''
    try:
      reffile = optionpack.rcsClient.get_entitylist(optionpack.l10nbase)
    except OSError, e:
      reffile = Entitylist()
    referencel10npackage.add_structure(reffile)
    
    try:
      localefile = optionpack.rcsClient.get_entitylist(optionpack.inipath)
    except OSError, e:
      localefile = EntityList()
    localel10npackage.add_structure(localefile)
    localel10npackage.id = locale
    
    localediffpackage = localel10npackage.diff(referencel10npackage,
                       values=optionpack.values, flags=optionpack.flags)

    return localediffpackage, localel10npackage, referencel10npackage


def read_and_compare_dir(optionpack, locale, localediffpackage,
                            localel10npackage, referencel10npackage,
                            l10npackagesreference):
    '''
    Method for importing directories to Silme-objects and diffing them.
    @param optionpack: instance of mozilla.core.main.CompareInit
    '''
    try:
      referencel10npackage = optionpack.rcsClient.get_package(optionpack.l10nbase,
                                                object_type=optionpack.objectType)
    except OSError, e:
      referencel10npackage = Package()
    
    try:
      localel10npackage = optionpack.rcsClient.get_package(optionpack.inipath,
                                                object_type=optionpack.objectType)
    except OSError, e:
      localel10npackage = Package()
    localel10npackage.id = locale
    
    localediffpackage = localel10npackage.diff(referencel10npackage,
                       values=optionpack.values, flags=optionpack.flags)

    return localediffpackage, localel10npackage, referencel10npackage




def read_and_compare_xpi(optionpack, locale, localediffpackages,
                         localel10npackages, referencel10npackages,
                         l10npackagesreference):
    try:
      loc = optionpack.manifest[locale]
    except KeyError:
      raise KeyError('This extension does not have the following locale: ' +
                     locale)

    for pos in loc.keys():
      type = loc[pos]['type']


      # test code for making a real file structure instead of a virtual one
      # Not used yet, because there is risk of conflicts (e.g., if we 
      # get more than one package with the same id...) that needs to be
      # investigated first
      if re.search(locale, loc[pos]['localepath']):
        intpath = loc[pos]['localepath'].split(locale)[1]
      else:
        intpath = loc[pos]['localepath']
      if intpath.startswith('/'):
        intpath = intpath[1:]
      if intpath.endswith('/'):
        intpath = intpath[:-1]
      if re.search('/', intpath):
        (intpath, id) = intpath.rsplit('/')
      else:
        id = intpath[:]
        intpath = None


      if type == 'jar':
        if not l10npackagesreference.has_package(optionpack.reference):
          optionpack.rcsClient.zfile =\
          optionpack.xpi.open_inlinearchive\
          (optionpack.manifest[optionpack.reference][pos]['jarpath'])
          try:
            l10npackagereference =\
            optionpack.rcsClient.get_package\
            (path=optionpack.manifest[optionpack.reference][pos]['localepath'],
             object_type=optionpack.objectType)
          except KeyError, e:
            raise KeyError('ERROR: The reference locale (' +
                           optionpack.reference +
                           ') could not be found in the package!')
          except UnicodeDecodeError, e:
            raise
            l10npackagereference = Package()
          l10npackagereference.id = pos
        else:
          try:
            l10npackagereference = l10npackagesreference.package\
                                   (optionpack.reference).package(pos)
          except KeyError, e:
            l10npackagereference = Package()
          except UnicodeDecodeError, e:
            raise
          l10npackagereference.id = pos
        optionpack.rcsClient.zfile =\
        optionpack.xpi.open_inlinearchive\
        (optionpack.manifest[locale][pos]['jarpath'])
        try:
          localel10npackage = optionpack.rcsClient.get_package\
          (path=optionpack.manifest[locale][pos]['localepath'],
          object_type=optionpack.objectType)
        except UnicodeDecodeError, e:
          raise
        
        for item in localel10npackage.structures():
          if (isinstance(item, EntityList) or isinstance(item, Structure)) and item.encoding == 'utf_8_sig':
            item.log('ERROR', 'this file '+
                 'starts with a UTF8-BOM, but the use of it is not allowed!')
        
        localel10npackage.id = pos
        localediffpackage = localel10npackage.diff(l10npackagereference, 
                           values=optionpack.values, flags=optionpack.flags)
        try:
          optionpack.rcsClient._close_jar()
        except KeyError, e:
          pass
      elif type == 'folder':
        if not l10npackagesreference.has_package(optionpack.reference):
          optionpack.rcsClient.zfile = optionpack.xpi.file
          try:
            l10npackagereference = optionpack.rcsClient.get_package\
            (path=optionpack.manifest[optionpack.reference][pos]['localepath'],
             object_type=optionpack.objectType)
          except KeyError, e:
            raise KeyError('ERROR: The reference locale (' +
                           optionpack.reference +
                           ') could not be found in the package!')
            l10npackagereference = Package()
          except UnicodeDecodeError, e:
            raise
          l10npackagereference.id = pos
        else:
          try:
            l10npackagereference = l10npackagesreference.package\
                                   (optionpack.reference).package(pos)
          except KeyError, e:
            l10npackagereference = Package()
          except UnicodeDecodeError, e:
            raise
          l10npackagereference.id = pos
        optionpack.rcsClient.zfile = optionpack.xpi.file
        try:
          localel10npackage = optionpack.rcsClient.get_package\
          (path=optionpack.manifest[locale][pos]['localepath'],
           object_type=optionpack.objectType)
        except UnicodeDecodeError, e:
          raise
        
        for item in localel10npackage.structures():
          if item.encoding == 'utf_8_sig':
            item.log('ERROR', 'this file '+
                 'starts with a UTF8-BOM, but the use of it is not allowed!')
        
        localel10npackage.id = pos
        localediffpackage = localel10npackage.diff(l10npackagereference, 
                           values=optionpack.values, flags=optionpack.flags)
      localediffpackages.add_package(localediffpackage)
      localel10npackages.add_package(localel10npackage)
      if not l10npackagesreference.has_package(l10npackagereference):
        l10npackagesreference.add_package(l10npackagereference)
    return localediffpackages, localel10npackages, l10npackagesreference
