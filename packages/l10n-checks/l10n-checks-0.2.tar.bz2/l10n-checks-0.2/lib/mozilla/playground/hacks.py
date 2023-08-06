from silme.core import Package, Structure, Blob, EntityList, Entity
from silme.diff.blob import BlobDiff
import silme.format
from silme.format import Manager
from silme.io.clients import IOClient, FileFormatClient
import os

silme.format.Manager.register('dtd', 'properties')

def objectdiffto (self, object, flags=None, values=True):
  '''
  override objectDiffTo, because the original one does not check 
  if object is of the same instance as self
  '''
  object_diff = BlobDiff()
  object_diff.id = self.id
  object_diff.uri = (self.uri, object.uri)
  if values == True:
    if not isinstance(object, Blob):
      object_diff.diff = None
    elif self.source == object.source:
      object_diff.diff = None
    else:
      object_diff.diff = True
  return object_diff

Blob.diff = objectdiffto



@classmethod
def dtd_parse_to_entitylist(cls, text, code='default'):
  '''
  override original method to find duplicates
  '''
  entityList = EntityList()
  text = cls.patterns['comment'].sub('', text)
  matchlist = cls.patterns['entity'].findall(text)
  for match in matchlist:
    if match[0] in entityList:
      entityList.log('ERROR', 'Entity ' + match[0] + ' is duplicated!')
    entityList.add_entity(Entity(match[0], match[1][1:-1], code))
  return entityList

silme.format.dtd.parser.DTDParser.parse_to_entitylist = dtd_parse_to_entitylist



@classmethod
def properties_parse_to_entitylist(cls, text, code='default'):
  '''
  override original method to find duplicates
  '''
  entitylist = EntityList()
  text = cls.patterns['comment'].sub('', text)
  matchlist = cls.patterns['entity'].findall(text)
  for match in matchlist:
    if match[0] in entitylist:
      entitylist.log('ERROR', 'Entity ' + match[0] + ' is duplicated!')
    entitylist.add_entity(Entity(match[0], match[1], code))
  return entitylist

silme.format.properties.parser.PropertiesParser.parse_to_entitylist = \
properties_parse_to_entitylist


@classmethod
def get_package(cls, path,
                    code='default',
                    object_type='l10nobject',
                    source=None,
                    ignore=['CVS','.svn','.DS_Store', '.hg']):
    (protocol, jarpath, ipath) = cls._explode_path(path)
    l10npackage = FileFormatClient.get_package(path, code, object_type, source, ignore)
    (b_source, oe_source) = cls._get_source_policy(source)

    if ipath:
        ipath = os.path.dirname(ipath)
    if not cls.zfile:
        try:
            cls._open_jar(jarpath)
        except Exception,e:
            raise Exception('Could not load a jar file: ' + jarpath + ': ' + str(e))
        # @var jar_open_stat: We need to know if the JAR-file was already open
        jar_open_stat = False
    else:
        jar_open_stat = True
    for name in cls.zfile.namelist():
        dirname = os.path.dirname(name)
        filename =    os.path.basename(name)
        # filter out dir entries or entries for dirs not in ipath
        if not filename or (ipath and not dirname.startswith(ipath)):
            continue

        relpath = dirname[len(ipath):] if ipath else dirname
        relpath = relpath[1:] if relpath.startswith('/') else relpath

        if cls._should_ignore(ignore, path=relpath, elem=[filename]):
            continue

        try:
            parser = Manager.get(path=filename)
        except KeyError, e:
            try:
                l10npackage.add_structure(cls.get_blob(name, source=True), relpath)
                l10npackage.element(filename).log('WARNING', filename + ': ' + str(e))
            except KeyError:
                newblob = Blob()
                newblob.encoding = 'utf8'
                newblob.id = filename
                newblob.log('ERROR', filename + ': ' + str(e))
                l10npackage.add_structure(newblob, relpath)
        else:
          try:
              if object_type=='blob':
                  l10npackage.add_structure(cls.get_blob(name, source=True), relpath)
              elif object_type=='entitylist':
                  l10npackage.add_structure(cls.get_entitylist(name, source=source,
                                          parser=parser), relpath)
              else:
                  l10npackage.add_structure(cls.get_structure(name, source=source,
                                          parser=parser), relpath)
          except UnicodeDecodeError, e:
            newblob = Blob()
            newblob.encoding = 'utf8'
            newblob.id = filename
            newblob.log('ERROR', filename + ': ' + str(e))
            l10npackage.add_structure(newblob, relpath)
    # close the JAR-file only, if it was opened in this method
    if not jar_open_stat:
        cls._close_jar()
    return l10npackage

silme.io.jar.JarClient.get_package = get_package