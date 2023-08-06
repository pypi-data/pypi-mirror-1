from silme.core \
  import Structure,Blob,Entity,Comment,EntityList,Package
from silme.diff import *
import silme.format
from mozilla.core.statistics import Statistics
from operator import attrgetter, itemgetter
from urlparse import urlparse, urljoin
from mozilla.core.merge import Merge
import re
import os
from urllib import pathname2url
import codecs

class MozDiffFormatParser():
  name = "Mozilla diff reader/writer"
  extensions = ['mozdiff']
  encoding = None
  fallback = None

  @classmethod
  def dump_objectdiff(cls, objectdiff, statistics, indent=0):
    '''
    Method not (yet) needed or used with compare-locales
    '''
    string = u''
    if objectdiff.diff:
      pass
    else:
      pass
    return string


  @classmethod
  def dump_l10nobjectdiff (cls, l10nobjectdiff, l10nobject, statistics, logs,
                         indent=0, optionpack=None, relativepath=None):
      return cls.dump_entitylistdiff(l10nobjectdiff.entitylistdiff(), 
                                     entitylist=l10nobject.entitylist(),
                                     indent=indent, optionpack=optionpack,
                                     relativepath=relativepath)

  @classmethod
  def dump_entitylistdiff(cls, entitylistdiff, entitylist, statistics, logs,
                         indent=0, optionpack=None, relativepath=None):
    '''
    This method analyzes, transforms, makes statistics of a given 
    EntityListDiff (or StructureDiff)
    @param entitylistdiff: EntityListDiff (or StructureDiff) to transform
    @param entitylist: EntityList (or l10nObject) of the locale used in the 
    diff. Needed to access informations not present in the diff
    @param statistics: instance of the Statistics class
    @param logs: logs regarding that object
    @param indent: int value. Indent to be used in the diff
    @param optionpack: (optional) Instance of the mozilla.core.main.CompareInit
     class
    @param relativepath: (optional) internal parameter used by the method
    '''
    #if isinstance(entitylistdiff, StructureDiff):
    #  entitylistdiff = entitylistdiff.entitylistdiff()
    diff = []
    keyRE = re.compile('[kK]ey')
    if not isinstance(entitylistdiff, BlobDiff):
      for item in entitylistdiff.entities().values():
        '''output of removed, added, modified or unmodified items'''
        if isinstance(item, Entity):
          if 'removed' in item.params['diff_flags']:
            statistics.add_stat('obsoleteEntities', 1)
            diff.append((item.id, '-'))
          elif 'added' in item.params['diff_flags']:
            statistics.add_stat('missingEntities', 1)
            statistics.add_stat('total', 1)
            diff.append((item.id, '+'))
          elif 'unmodified' in item.params['diff_flags']:
            #diff.append((item.id+':\t'+item.get_value(), 'unmodified: '))
            if not keyRE.search(item.id):
              statistics.add_stat('unmodifiedEntities', 1)
              statistics.add_stat('total', 1)
              if optionpack.checkvalidity and len(item.value) > 1:
                # perform some label tests
                cls.check_validity(diff, item, entitylistdiff, 
                                  statistics, optionpack)
            else:
              statistics.add_stat('keys', 1)
              # perform some access keys test:
              if optionpack.accesskeys:
                cls.check_accesskeys(diff, item, entitylistdiff, 
                                    statistics, optionpack)
        else:
          #diff.append((item.id, 'modified: '))
          if not keyRE.search(item.id):
            statistics.add_stat('changedEntities', 1)
            statistics.add_stat('total', 1)
            if optionpack.checkvalidity and len(item.get_value()[0]) > 1:
              # perform some label tests
              cls.check_validity(diff, item, entitylistdiff, 
                                statistics, optionpack)
          else:
            statistics.add_stat('keys', 1)
            # perform some access keys test:
            if optionpack.accesskeys:
              cls.check_accesskeys(diff, item, entitylistdiff, 
                                  statistics, optionpack)
    diff.extend(MozDiffFormatParser.append_logs(logs, statistics, optionpack))
    diff.sort(key=itemgetter(0))
    # merge missing entities
    if optionpack.merge is not None:
      if not isinstance(entitylistdiff, BlobDiff):
        added = entitylistdiff.entities('added')
        removed = entitylistdiff.entities('removed')
        if len(added) > 0:
          Merge.basic_merge(optionpack, added, entitylist, relativepath,
                           removed, entitylistdiff.uri)
      else:
        pass
        # TODO: we need the original object here...
        #Merge.object_merge(optionpack, obj, relativepath)
    ##
    return diff

  @classmethod
  def make_l10npackagediff(cls, l10npackagediff, l10npackagelocale,
                          l10npackagereference, statistics, indent=2,
                          optionpack=None, relativepath=None):
    '''
    This method analyzes, transforms and makes statistics of a given 
    L10nPackageDiff
    @param l10npackagediff: L10nPackageDiff to transform
    @param l10npackagelocale: L10nPackage of the locale used in the 
    L10nPackageDiff. Needed to access informations not present in the diff
    @param l10npackagereference: L10nPackage of the reference locale used in 
    the L10nPackageDiff. Needed to access informations not present in the diff
    @param statistics: instance of the Statistics class
    @param indent: (optional) int value. Indent to be used in the diff
    @param optionpack: (optional) Instance of the mozilla.core.main.CompareInit
     class
    @param relativepath: (optional) internal parameter used by the method
    '''
    diff = []
    onelevel = []
    if l10npackagediff.id:
      diff.append(l10npackagediff.id)
    if relativepath is not None:
      relativepath = os.path.join(relativepath, l10npackagediff.id)
    else:
      relativepath = l10npackagediff.id
    objects = []
    packages = []
    # try to find objects which didn't make it into the diff
    if l10npackagelocale is not None:
      for object in l10npackagelocale.structures():
        if not l10npackagediff.has_structure(object.id):
          logs = MozDiffFormatParser.append_logs(object.get_logs(), statistics,
                                                optionpack)
          if len(logs) > 0:
            objects.append((object.id, logs))
    if l10npackagereference is not None:
      for object in l10npackagereference.structures():
        if not l10npackagediff.has_structure(object.id):
          # TODO: what to do with problems in the reference...
          pass
    ##
    # try to find packages which didn't make it into the diff
    if l10npackagelocale is not None:
      for package in l10npackagelocale.packages():
        if not l10npackagediff.has_package(package.id):
          logs = \
          MozDiffFormatParser.append_logs\
          (package.get_logs(recursive=True), statistics, optionpack)
          if len(logs) > 0:
            # TODO: MAKE OBJECTS/PACKAGES RECURSIVELY, INSTEAD OF PACKING EVERY
            # MESSAGE INTO ONE PACKAGE
            packages.append((package.id, logs))
    if l10npackagereference is not None:
      for package in l10npackagereference.packages():
        if not l10npackagediff.has_package(package.id):
          # TODO: what to do with problems in the reference...
          pass
    # process objects
    for object in l10npackagediff.structures():
      # take logs from Objects
      if l10npackagelocale is not None \
      and l10npackagelocale.has_structure(object.id):
        objectlocalelogs = l10npackagelocale.structure(object.id).get_logs()
      else:
        objectlocalelogs = None
      if l10npackagereference is not None \
      and l10npackagereference.has_structure(object.id):
        objectreferencelogs = \
        l10npackagereference.structure(object.id).get_logs()
      else:
        objectreferencelogs = None
      if l10npackagediff.structure_type(object.id) is 'added':
        objects.append((object.id, u'// add and localize this file'))
        statistics.add_stat('missingFiles', 1)
        if not isinstance(object, Blob):
          statistics.add_stat('missingEntitiesInMissingFiles',
                             len(object.entities()))
          statistics.add_stat('total', len(object.entities()))
          # merge
          if optionpack.merge is not None:
            Merge.basic_merge(optionpack, object.entities(),
                             l10npackagereference.structure(object.id),
                             relativepath, None, None, object.id)
        else:
          # merge
          if optionpack.merge is not None:
            Merge.object_merge(optionpack, object, relativepath)
      elif l10npackagediff.structure_type(object.id) is 'removed':
        objects.append((object.id, u'// remove this file'))
        statistics.add_stat('obsoleteFiles', 1)
      elif (l10npackagediff.structure_type(object.id) is 'modified'):
          if l10npackagereference is not None:
            refentlist = l10npackagereference.structure(object.id)
          else:
            refentlist = None
          l10nobjectdiff = \
          cls.dump_entitylistdiff(object,
                                 entitylist=refentlist,
                                 statistics=statistics,
                                 logs=objectlocalelogs,
                                 indent=indent+2,
                                 optionpack=optionpack,
                                 relativepath=relativepath)
          if len(l10nobjectdiff) > 0:
            objects.append((object.id, l10nobjectdiff))
    # process packages
    for package in l10npackagediff.packages():
      if (l10npackagediff.package_type(package.id) is 'added') \
      or (l10npackagediff.package_type(package.id) is 'modified'):
        if l10npackagediff.package_type(package.id) is 'added':
          statistics.add_stat('missingFolders', 1)
          # in this case package is a Package and 
          # not a PackageDiff, so we need to make a fake diff
          l10npackage = Package()
          packagediff = l10npackage.diff(package)
          packagediff.id = package.id
          package = packagediff
          ##
        if l10npackagelocale is not None \
        and l10npackagelocale.has_package(package.id):
          subl10npackagelocale = l10npackagelocale.package(package.id)
        else:
          subl10npackagelocale = None
        if l10npackagereference is not None \
        and l10npackagereference.has_package(package.id):
          subl10npackagereference = l10npackagereference.package(package.id)
        else:
          subl10npackagereference = None
        pack = \
        cls.make_l10npackagediff(package,
                                subl10npackagelocale,
                                subl10npackagereference,
                                statistics=statistics, indent=indent+2,
                                optionpack=optionpack,
                                relativepath=relativepath)
        if len(pack) > 1: # because: 1 == package.id
          packages.append(pack)
      elif l10npackagediff.package_type(package.id) is 'removed':
        statistics.add_stat('obsoleteFolders', 1)
        # in this case package is a Package and 
        # not a PackageDiff, so we need to make a fake diff
        l10npackage = Package()
        packagediff = package.diff(l10npackage)
        if len(packagediff.structures()) > 0 \
        or len(packagediff.packages()) > 0:
          packagediff.id = package.id
          package = packagediff
          ##
          if l10npackagelocale is not None \
          and l10npackagelocale.has_package(package.id):
            subl10npackagelocale = l10npackagelocale.package(package.id)
          else:
            subl10npackagelocale = None
          if l10npackagereference is not None \
          and l10npackagereference.has_package(package.id):
            subl10npackagereference = \
            l10npackagereference.package(package.id)
          else:
            subl10npackagereference = None
          pack = \
          cls.make_l10npackagediff(package,
                                  subl10npackagelocale,
                                  subl10npackagereference,
                                  statistics=statistics, indent=indent+2,
                                  optionpack=optionpack,
                                  relativepath=relativepath)
          if len(pack) > 1: # because: 1 == package.id
            packages.append(pack)
        else:
          packages.append((package.id, u'// remove this folder'))
    if len(objects) > 0:
      onelevel.extend(objects)
    if len(packages) > 0:
      onelevel.extend(packages)
    onelevel.sort(key=itemgetter(0))
    diff.extend(onelevel)
    return diff

  @classmethod
  def dump_l10npackagediff(cls, l10npackagediff, l10npackagelocale,
                          l10npackagereference, statistics, indent=2,
                          optionpack=None, output=0):
    '''
    This method analyzes, transforms, makes statistics of a given 
    L10nPackageDiff and returns a already formatted string.
    @param l10npackagediff: L10nPackageDiff to transform
    @param l10npackagelocale: L10nPackage of the locale used in the 
    L10nPackageDiff. Needed to access informations not present in the diff
    @param l10npackagereference: L10nPackage of the reference locale used in 
    the L10nPackageDiff. Needed to access informations not present in the diff
    @param statistics: instance of the Statistics class
    @param indent: (optional) int value. Indent to be used in the diff
    @param optionpack: (optional) Instance of the mozilla.core.main.CompareInit
     class
    @param output: (optional) int value for choosing the output style
    '''
    return ''.join(cls.serialize(cls.make_l10npackagediff(l10npackagediff,
                                 l10npackagelocale, l10npackagereference,
                                 statistics=statistics, indent=indent,
                                 optionpack=optionpack),
                   indent=indent, output=output))

  @classmethod
  def serialize(cls, difflist, indent=0, output=0, space=u' ', 
                previouspath=None):
    '''
    This method formats an already preprocessed diff.
    
    @param difflist: preprocessed diff list
    @param output: (optional) int value for choosing the output style. 
    0 = tree, 1 = full tree, 2 = full path in one line
    @param indent: (optional) int value. Indent to be used in the diff
    @param optionpack: (optional) Instance of the mozilla.core.main.CompareInit
     class
    @param space: (optional) 
    @param previouspath: (optional) internal parameter used by the method
    '''
    string = []
    if output is 0:
      while len(difflist) > 0:
        # Entry is a folder
        if isinstance(difflist, list):
         if len(difflist) > 2:
          folder = None
          only_lists = True
          for i in difflist:
            if isinstance(i, str) or isinstance(i, unicode):
              folder = difflist.pop(difflist.index(i))
            elif not isinstance(i, list):
              only_lists = False
          if folder and only_lists is False:
            if previouspath:
              string.append(u'\n')
              indent+=2
              previouspath = None
            string.append(u'' + (space * indent) + folder + '\n')
          elif folder and only_lists is True:
            if previouspath:
              string.append(u'/' + folder + '\n')
              previouspath=None
            else:
              string.append(u'' + (space * indent) + folder + '\n')
         elif len(difflist) == 2:
          for i in difflist:
            if isinstance(i, str) or isinstance(i, unicode):
             if previouspath:
              string.append(u'/' + difflist.pop(difflist.index(i)) + '')
             else:
              string.append(u'' + (space * indent) + \
                            difflist.pop(difflist.index(i)) + '')
              previouspath=True
         item = None
         while len(difflist) >= 1:
            item = difflist.pop(0)
            if previouspath:
              string.append(u''.join(cls.serialize(difflist=item, 
                                                   indent=(indent), 
                            output=output, previouspath=previouspath)))
            else:
              string.append(u''.join(cls.serialize(difflist=item, 
                                                   indent=(indent+2), 
                            output=output, previouspath=previouspath)))
        elif isinstance(difflist, tuple):
          # Entry is a file
          if isinstance(difflist[1], unicode):
            if previouspath:
              string.append(u'/' + difflist[0] + '\n' + space * (indent + 4) \
                            + difflist[1] + '\n')
              previouspath = None
            else:
              string.append(u'' + (space * indent) + difflist[0] + '\n' + \
                            space * (indent + 4) + difflist[1] + '\n')
            difflist = ''
          #'''Entry is a list of entities'''
          elif isinstance(difflist[1], list): 
            # difflist[0] is a file name, difflist[1] is a list of entities
            if previouspath:
              string.append(u'/' + difflist[0] + '\n')
              previouspath = None
            else:
              string.append(u'' + (space * indent) + difflist[0] + '\n')
            while len(difflist[1]) > 0:
              entity = difflist[1].pop(0)
              string.append(u'' + space * (indent + 4) + entity[1] + \
                            entity[0] + '\n')
            difflist = ''
          else:
            difflist = ''
        else:
          difflist = ''
    elif output is 1:
      while len(difflist) > 0:
        # Entry is a folder
        if isinstance(difflist, list):
          for i in difflist:
            if isinstance(i, str) or isinstance(i, unicode):
              string.append(u'' + (space*indent) + \
                            difflist.pop(difflist.index(i)) + '\n')
              break
          item = None
          while len(difflist) >= 1:
            item = difflist.pop(0)
            string.append(u''.join(cls.serialize(difflist=item, 
                                                 indent=(indent+2), 
                          output=output, previouspath=previouspath)))
        elif isinstance(difflist, tuple):
          if isinstance(difflist[1], unicode):
            string.append(u'' + (space*indent) + difflist[0] + '\n' + \
                          space*(indent+4) + difflist[1] + '\n')
            difflist=''
          # Entry is a list of entities
          elif isinstance(difflist[1], list): 
            # difflist[0] is a file name, difflist[1] is a list of entities
            string.append(u'' + (space*indent) + difflist[0] + '\n')
            while len(difflist[1]) > 0:
              entity = difflist[1].pop(0)
              string.append(u'' + space*(indent+4) + entity[1] + \
                            entity[0] + '\n')
            difflist=''
          else:
            difflist=''
        else:
          difflist=''
    elif output is 2:
      while len(difflist) > 0:
        # Entry is a folder 
        if isinstance(difflist, list):
          for i in difflist:
            if isinstance(i, str) or isinstance(i, unicode):
              if not previouspath:
                previouspath = space*indent + difflist.pop(difflist.index(i))
              else:
                previouspath += '/' + difflist.pop(difflist.index(i))
          item = None
          while len(difflist) >= 1:
            item = difflist.pop(0)
            string.append(u''.join(cls.serialize(difflist=item, indent=indent, 
                          output=output, previouspath=previouspath)))
        elif isinstance(difflist, tuple):
          if previouspath:
            string.append(u'' + previouspath + '/')
            previouspath = None
          #'''Entry is a file'''
          if isinstance(difflist[1], unicode):
            string.append(u'' + difflist[0] + '\n' + space*(indent+4) + \
                          difflist[1] + '\n')
            difflist=''
          #'''Entry is a list of entities'''
          elif isinstance(difflist[1], list): 
            string.append(u'' + difflist[0] + '\n')
            while len(difflist[1]) > 0:
              entity = difflist[1].pop(0)
              string.append(u'' + space*(indent+4) + entity[1] + \
                            entity[0] + '\n')
            difflist=''
          else:
            difflist=''
        else:
          difflist=''
    else:
      raise Exception('There is no output style under this number')
    return string
