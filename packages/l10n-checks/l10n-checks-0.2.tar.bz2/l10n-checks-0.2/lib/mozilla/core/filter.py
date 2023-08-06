import os.path
from urlparse import urlparse, urljoin
from urllib import pathname2url, url2pathname

class Filter(object):
  '''
  Class for reading and using the filter.py file
  '''

  def __init__(self, inipath):
    '''
    @param inipath: we assume, that the filter.py file is in the same folder 
    like the l10n.ini file
    '''
    self.filters = []
    drive, tail = os.path.splitdrive(inipath)
    filterpath = drive + url2pathname(urlparse(urljoin(pathname2url(tail),
                                                       'filter.py'))[2])
    self.addFilterFrom(filterpath)
  
  def addFilterFrom(self, filterpath):
    '''
    Method which adds filters to the filter list
    @param filterpath: path to a filter file
    '''
    if not os.path.exists(filterpath):
      raise IOError("The path: " +filterpath+ 
                      " to filter.py is wrong - the file does not exist there")
    l = {}
    execfile(filterpath, {}, l)
    if 'test' not in l or not callable(l['test']):
      raise NameError("filter.py does not have a 'test' method")
    self.filters.append(l['test'])
  
  def filter(self, module, filepath, entity = None):
    '''
    Method which performs the filter-search
    @param module: module-path
    @param filepath: filepath (without the module-part)
    @param entity: (optional) Entity ID
    @return: boolean value. False means: found in the filterlist - filter that.
    True means: do not filter that
    '''
    for f in self.filters:
      try: 
        if not f(pathname2url(module), pathname2url(filepath), entity):
          return False
      except Exception, e:
        raise Exception("Error in filter.py: " +str(e))
    return True
