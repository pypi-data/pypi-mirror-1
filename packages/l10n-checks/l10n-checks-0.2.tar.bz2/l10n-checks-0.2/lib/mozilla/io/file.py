import silme.io.file
import silme.io.clients
import os
import silme.format
from silme.core import EntityList, Package, Blob, Structure
from mozilla.core.filter import *

@classmethod
def get_l10nobjectfilter(cls, path, source=False, code='default', parser=None,
                        filter=None):
  '''
  Method which invokes the right get_l10nobject classmethod and filters 
  the results.
  '''
  l10nObject = cls.get_structure(path=path, source=source, code=code,
                                 parser=parser)
  # filter unneeded entities
  if filter is not None:
    entitylist = l10nObject.get_entitylist()
    for id in entitylist.keys():
      if not filter['filter'].filter(filter['module'],
                                     filter['relativepath'], id):
        l10nObject.remove_entity(id)
  return l10nObject

silme.io.clients.IOClient.get_l10nobjectfilter = get_l10nobjectfilter


@classmethod
def get_entitylistfilter(cls, path, source=False, code='default', parser=None,
                        filter=None):
  '''
  Method which invokes the right get_entitylist classmethod and filters 
  the results.
  '''
  try:
    entityList = cls.get_entitylist(path=path, source=source, code=code,
                                 parser=parser)
  except Exception, e:
    if str(e).find('not utf_8 like expected, but utf_8_sig') != -1:
      entityList = EntityList()
      entityList.id = os.path.basename(path)
      entityList.log('ERROR', path +': this File contains a Byte Order ' + \
                     'Mark (BOM)! Parsing file aborted! The information ' + \
                     'below may be incorrect...')
    else:
      raise Exception, e
    
  # filter unneeded entities
  if filter is not None:
    tempentlist = [] #workaround for not making entityList shorter while being in the for-loop below
    for id in entityList.ids():
      if not filter['filter'].filter(filter['module'],
                                     filter['relativepath'], id):
        tempentlist.append(id)
    for id in tempentlist:
      entityList.remove_entity(id)
  return entityList

silme.io.clients.IOClient.get_entitylistfilter = get_entitylistfilter


@classmethod
def get_package(cls, path,
                   code='default',
                   object_type='l10nobject',
                   source=False,
                   ignore=['CVS','.svn','.DS_Store', '.hg'],
                   filter=None):
  '''
  Method which overrides silme.io.file.FileClient.get_l10npackage 
  for the purpose of:
  1. Logging errors and warning instead of raising exceptions
  2. Filtering unneeded filed and folders BEFORE reading them
  '''
  # filter unneeded modules
  if filter is not None:
    relativepath = filter['relativepath']
    if not filter['filter'].filter(filter['module'], relativepath):
      return None
  l10nPackage = Package()
  l10nPackage.id = os.path.basename(path)
  l10nPackage.uri = path
  try:
    l = os.listdir(path)
  except OSError, e:
    raise OSError('Not a directory: ' + path + ': ' + str(e))
  except Exception, e:
    raise Exception('Could not load directory: ' + path + ': ' + str(e))
  for elem in l:
    p2 = os.path.join(path, elem)
    if elem in ignore:
      continue
    # filter unneeded directories and files
    if filter is not None:
      if not filter['filter'].filter(filter['module'],
                                     os.path.join(relativepath, elem)):
        continue
    if os.path.isdir(p2):
      if filter is not None:# and relativepath is not None:
        filter['relativepath'] = os.path.join(relativepath, elem)
      l10nPackage._packages[elem] = cls.get_package(p2,
                                                      code=code,
                                                      object_type=object_type,
                                                      source=source,
                                                      ignore=ignore,
                                                      filter=filter)
    else:
      try:
        parser = silme.format.Manager.get(path=elem)
      except Exception, e:
        try:
          l10nPackage._structures[elem] = cls.get_blob(p2, source=True)
          l10nPackage._structures[elem].log('WARNING', p2 + ': ' + str(e))
        except KeyError:
          l10nPackage._structures[elem] = Blob()
          l10nPackage._structures[elem].id = elem
          l10nPackage._structures[elem].log('ERROR', p2 + ': ' + str(e))
      else:
       if filter is not None and relativepath is not None:
         filter['relativepath'] = os.path.join(relativepath, elem)
       try:
         if object_type=='object':
           l10nPackage._structures[elem] = cls.get_blob(p2, source=True)
         elif object_type=='entitylist':
           l10nPackage._structures[elem] = cls.get_entitylistfilter(p2,
                                                               source=source,
                                                               code=code,
                                                               parser=parser,
                                                               filter=filter)
           if l10nPackage._structures[elem].encoding == 'utf_8_sig':
             l10nPackage._structures[elem].log('ERROR', 'this file '+
                 'starts with a UTF8-BOM, but the use of it is not allowed!')
         else: 
           l10nPackage._structures[elem] = cls.get_l10nobjectfilter(p2,
                                                               source=source,
                                                               code=code,
                                                               parser=parser,
                                                               filter=filter)
           if l10nPackage._structures[elem].encoding == 'utf_8_sig':
             l10nPackage._structures[elem].log('ERROR', 'this file '+
                 'starts with a UTF8-BOM, but the use of it is not allowed!')
       except UnicodeDecodeError, e:
         try:
           l10nPackage._structures[elem].log('ERROR', p2 + ': ' + str(e))
         except KeyError:
           l10nPackage._structures[elem] = Blob()
           l10nPackage._structures[elem].id = elem
           l10nPackage._structures[elem].log('ERROR', p2 + ': ' + str(e))
  return l10nPackage

silme.io.file.FileClient.get_package = get_package
