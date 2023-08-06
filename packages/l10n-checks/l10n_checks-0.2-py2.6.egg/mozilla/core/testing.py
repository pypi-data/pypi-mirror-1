import mozilla.fp.diff.mozdiff as mozdiff
from silme.core import *
from silme.diff import *
try:
  import enchant
  from enchant.tokenize import get_tokenizer
  pyenchant = True
except ImportError, e:
  pyenchant_error = str(e)
  pyenchant = False
import re
import os.path

@classmethod
def pyenchant_dict_init(cls, locale):
  '''
  Initialize PyEnchant with a dictionary for the given locale
  @param locale: name of the dictionary to be used
  '''
  if pyenchant:
    if enchant.dict_exists(locale):
      try:
        cls.tknzr = get_tokenizer(locale)
      except Exception, e:
        cls.tknzr = get_tokenizer('en_US')
      if os.path.isfile(locale + '-ignorelist.txt'):
        cls.dict = enchant.DictWithPWL(locale, locale + '-ignorelist.txt')
      else:
        cls.dict = enchant.Dict(locale)
    else:
      raise OSError('No spellchecker dictionary found for locale: ' + \
                    locale + '. Available spellcheckers: \n' + \
                    ', '.join(enchant.list_languages()))
  else:
    raise Exception('PyEnchant not available. Reason: ' + pyenchant_error + \
                    '\nSpellchecking will be deactivated.')
  
mozdiff.MozDiffFormatParser.pyenchant_dict_init = pyenchant_dict_init

@classmethod
def check_validity(cls, diff, item, entitylistdiff, statistics, 
                  optionpack=None):
  '''
  Check words with the given dictionary.
  
  @attention: PyEnchant, as of version 1.4.2, does not work with Mac OS X. 
  OS X support is on the authors TODO list... since 2006...
  @param diff: 
  @param item: 
  @param elementListDiff: 
  @param statistics: 
  @param optionpack: (optional) 
  '''
  if pyenchant:
    junk = ['\\n', '%S', '%s']
    if isinstance(item, Entity):
      labelval = item.get_value()
    elif isinstance(item, EntityDiff):
      labelval = item.get_value()[0]
    for i in junk:
      if labelval.count(i) > 0:
        labelval = labelval.replace(i,' ')
    words = [w[0] for w in cls.tknzr(labelval)]
    misspelled = []
    for word in words:
      if not cls.dict.check(word):
        misspelled.append(word)
    if len(misspelled) > 0:
      diff.append((item.id + ': probably misspelled word(s): ' + \
                   ', '.join(misspelled), '!'))
      statistics.add_stat('labels with misspelled words', 1)
  else:
    pass

mozdiff.MozDiffFormatParser.check_validity = check_validity

@classmethod
def check_accesskeys(cls, diff, item, entitylistdiff, statistics, 
                    optionpack=None):
  '''
  Many access keys tests
  @param diff: 
  @param item: 
  @param elementListDiff: 
  @param statistics: 
  @param optionpack: (optional) 
  '''
  accesskeyRE = re.compile('\.*[aA]ccess[kK]ey[0-9]*$')#|\.[aA]ccess$')
  commandkeyRE = re.compile('\.*[cC]ommand[kK]ey[0-9]*|[cC]md[0-9]*\.[kK]ey[0-9]*|\.*[kK]ey[cC]ode[0-9]*$')
  badkeynameRE = re.compile('[aA]ccess$|([^aA][^c][^c][^e][^s][^s])*[kK]ey$|\.*[aA][kK]ey[0-9]*$')
  badaccesskeyRE = re.compile('[pgqyjil]')
  if isinstance(item, Entity):
    val = item.value
  elif isinstance(item, EntityDiff):
    val = item.value()[0]
  if accesskeyRE.search(item.id):
    statistics.add_stat('accesskeys', 1)
    '''test if the access key consists only of one letter'''
    if len(val) > 1:
        diff.append((item.id + ':\tthis accesskey ('+val+') has more than ' + \
                     'one letter', '!'))
        statistics.add_stat('accesskeys with more than one letter', 1)
    '''test if illegal letters were used as access keys'''
    if badaccesskeyRE.search(val):
      diff.append((item.id + ':\tthis accesskey ('+val+') does not comply ' + \
                   'with the Mozilla accesskey policy https://developer.' + \
                   'mozilla.org/en/XUL_Accesskey_FAQ_and_Policies', '!'))
      statistics.add_stat('accesskeys outside of Mozilla policy', 1)
    label = accesskeyRE.split(item.id, maxsplit = 1)
    labelnames = ['', '.label', '.title', '.title2', 'Text', 'Label', 'Title']
    listkeys = entitylistdiff.keys()
    for name in labelnames:
      if label[0]+name in listkeys:
        label = label[0]+name
        break
    if not isinstance(label, list):
      if isinstance(entitylistdiff.entity(label), Entity):
        labelval = entitylistdiff.entity(label).value
      elif isinstance(entitylistdiff.entity(label), EntityDiff):
        labelval = entitylistdiff.entity(label).value()[0]
      '''test if the letter used as the access key is available 
      in the labels value'''
      if val not in labelval:
        if val.lower() in labelval.lower():
          diff.append((item.id + ':\tlocalized accesskey ('+val+') does ' + \
                       'not match localized label. Access keys are case ' + \
                       'sensitive (https://developer.mozilla.org/en/XUL_'+ \
                       'Accesskey_FAQ_and_Policies)!', '!'))
          statistics.add_stat('accesskeys not matching label (wrong case)', 1)
        else:
          diff.append((item.id + ':\tlocalized accesskey ('+val+') does ' + \
                       'not match localized label', '!'))
          statistics.add_stat('accesskeys not matching label', 1)
    else:
      '''test if there is a label with the same entity name 
      like the access key (without extension)'''
      if optionpack.testreference:
        diff.append((item.id + \
                     ':\taccesskey without a corresponding label', '!'))
        statistics.add_stat('accesskeys without corresponding labels', 1)
  '''test if the name of the key allows you to recognize if this is either 
  an access or a command key'''
  if optionpack.testreference:
    if not accesskeyRE.search(item.id) and not commandkeyRE.search(item.id) \
      and badkeynameRE.search(item.id) and len(val) == 1:
      diff.append((item.id + ':\tbad access/command key name. If you see ' + \
                   'the name: do you know if this an access or a command ' + \
                   'key?', '!'))
      statistics.add_stat('bad access/command keys names', 1)

mozdiff.MozDiffFormatParser.check_accesskeys = check_accesskeys
