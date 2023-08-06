import os
from silme.core import Structure, Comment

class Merge(object):
  '''
  Class for merging missing entities or whole objects
  '''

  @staticmethod
  def basic_merge(optionpack, missingentities, refentitylist, relativepath,
                 removedentities, urituple=None, id=None):
    '''
    This method appends missing entities. 
    If it gets a URI tuple, it will append the entities to an existing 
    l10n file. If it gets an object ID, it will make a new file.
    
    This method preserves an existing localized file and adds at the end 
    of the file an comment and after that the missing entities. 
    Because of that, the main purpose of this method is addition of missing 
    entities on a temporally basis.
    '''
    if urituple is not None and id is None:
      file = optionpack.rcsClient.get_structure(urituple[0])
      for entity in missingentities.values():
        if file.has_entity(entity.id):
          raise Exception('The file ' + urituple[0] + \
                          ' has changed. Merge aborted.')
    elif id is not None and urituple is None:
      file = Structure()
      file.id = id
    else:
      raise KeyError('Not enough or wrong arguments')
    file.add_string(u'\n\n')
    file.add_comment(Comment('\nEntities below were automatically added by ' + \
                            'compare-locales,\n based on ' + \
                            optionpack.reference + ' entities.\n'))
    file.add_string(u'\n\n')
    if isinstance(missingentities, dict):
      for item in missingentities.values():
        file.add_entity(item)
        file.add_string(u'\n')
    elif isinstance(missingentities, list):
      for item in missingentities:
        file.add_entity(item)
        file.add_string(u'\n')
    dirpath = os.path.join(optionpack.merge, relativepath)
    if not os.path.exists(dirpath):
      os.makedirs(dirpath)
    optionpack.rcsClient.write_object(file, dirpath)

  @staticmethod
  def object_merge(optionpack, object, relativepath):
    '''
    This method copies a whole missing Object. 
    It does not modify it in any way.
    '''
    dirpath = os.path.join(optionpack.merge, relativepath)
    if not os.path.exists(dirpath):
      os.makedirs(dirpath)
    optionpack.rcsClient.write_object(object, dirpath)
