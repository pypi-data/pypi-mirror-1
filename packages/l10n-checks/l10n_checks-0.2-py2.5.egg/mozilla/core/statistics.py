from operator import truediv
from collections import defaultdict

class intdict(defaultdict):
      def __init__(self):
        defaultdict.__init__(self, int)

class Statistics:
  ''' 
  Class for collecting, parsing and returning statistics
  '''
  
  def __init__(self, locale, reference=None):
    self.locale = locale
    self.reference = reference
    self.statistics = intdict()
    
  def add_stat(self, type, amount):
    '''
    Add a statistic
    @param type: type of the statistic information
    @param amount: how many items of that type should be added
    '''
    if isinstance(amount, (int, long)):
      try:
        self.statistics[type] += amount
      except KeyError:
        self.statistics[type] = amount
    else:
      raise Exception('ERROR: "amount" must be of type int or long')
    
  def get_stat(self, type):
    '''
    Get the statistics for the given type
    @param type: type of statistics
    '''
    try:
      return self.statistics[type]
    except KeyError:
      raise KeyError('ERROR: There are no statistics for ' + type)

  def get_statistics(self):
    '''
    Get all saved statistics
    '''
    return self.statistics

  def get_percentage(self, par1, par2):
    '''
    Count the percentage: par2 / (par1+par2)
    @param par1: int or list of ints
    @param par2: int or list of ints
    '''
    if isinstance(par1, list):
      element1 = 0
      for item in par1:
        element1+=self.get_stat(item)
    else:
      element1 = self.get_stat(par1)
    if isinstance(par2, list):
      element2 = 0
      for item in par2:
        element2+=self.get_stat(item)
    else:
      element2 = self.get_stat(par2)
    try:
      if (element1 + element2 > 0):
        return truediv(int(truediv(element2, (element2 + element1)) * 100000), 1000)
      else:
        raise ZeroDivisionError
    except KeyError, e:
      raise KeyError(str(e))
    
  def dump_percentage(self, par1, par2):
    '''
    Dump the percentage: par2 / (par1+par2)
    @param par1: int or list of ints
    @param par2: int or list of ints
    @return: string
    '''
    try:
      return str(str(self.get_percentage(par1, par2)) + '% of entries changed\n')
    except KeyError:
      return ''
    except ZeroDivisionError:
      return ''

  def dump_statistics(self):
    '''
    Dump the statistics to a string
    @return: string
    '''
    string = []
    string.append('\n' + self.locale + ':\n')
    keys = self.statistics.keys()
    string.extend([(key + ': ' + str(self.get_stat(key)) + '\n') for key in keys if self.get_stat(key) > 0])
    string.sort()
    return ''.join(string)

  def to_json(self):
    '''
    Dump the statistics to a JSON object
    @return: JSON
    '''
    values = {}
    for key in self.statistics.keys():
      if self.get_stat(key) > 0:
        values[key] = str(self.get_stat(key))
    return {'children' : [self.locale, {'children' : [values]}]}
