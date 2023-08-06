from silme.core import Package
from silme.core.logger import *
from mozilla.core.logger import *
from silme.diff import PackageDiff
from mozilla.core.filter import Filter
import silme.format
from silme.io.file import *
from mozilla.io.file import *
from silme.io.jar import *
from mozilla.fp.diff.mozdiff import *
from mozilla.core.l10nconfigparser import L10nConfigParser
from urllib import pathname2url, url2pathname
import mozilla.core.testing
from collections import defaultdict
from mozilla.core.mainhelper import *
from mozilla.core.zip import *
from mozilla.core.manifestparser import *

class Resultset(object):
  '''
  Class for storing compare-locales results.
  '''
  def __init__(self):
    '''
    @ivar details: dict, stores output of the method 
    mozdiff.makeL10nPackageDiff()
    @ivar summary: defaultdict, stores statistics separately for every language 
    as intdicts
    @ivar stat_cats: dict, stores used statistics categories separately for 
    every language
    @ivar statistics: instance of Statistics class, stores statistics separately 
    for every language
    '''
    self.details = {}
    self.summary = defaultdict()
    self.stat_cats = {}
    self.statistics = {}

class CompareInit(object):
  '''
  CompareInit class stores all provided command line options and some other
  options.
  @param reference: (optional) the reference locale. Default is en-US
  @param inipath: (optional) path to l10n.ini or an extension (xpi)
  @param l10nbase: (optional) the base directory with all locales in it
  @param locales: (optional) locale list
  @param fp: (optional) file parser instance
  @param turbo: (optional) boolean value. If True: only tests for missing and obsolete
  items will be done
  @param accesskeys: (optional) boolean value. If True: access keys test will be performed
  @param mercurial: (optional) boolean value: If True: Mercurial clone or 
  pull && update -C will be performed
  @param merge: (optional) accepts a path as value
  @param testreference: (optional) boolean value. If True: tests will be run on the 
  reference locale itself
  @param output: (optional) integer value. Changes the display style
  @param inputtype: (optional) sets the input type. Default is source
  @param checkvalidity: (optional) boolean value. If True: label tests will be performed
  @param verbose: (optional) integer value. Sets the verbose level
  @param compatibility: (optional) boolean value. If True: works in compare-locales 
  0.5/0.6 compatibility mode 
  @param returnmode: (optional): how mozilla.core.comparelocales.compareLocales
  will return the results: either 'dump' (prints to the command line) or 
  'array' (returns an array. The first value are the results, the second the 
  statistics)
  @param returnvalue: what mozilla.core.comparelocales.compareLocales
  will return: 
      'full:' formatted text with results and statistics
      'results': just the results, as text
      'statistics': just the statistics, as text
      'full_json:' JSON with results and statistics
      'results_json': just the results, as JSON
      'statistics_json': just the statistics, as JSON
  '''
  def __init__(self, reference='en-US', inipath=None, l10nbase=None,
               locales=None, fp=None, turbo=False,
               accesskeys=False, mercurial=False, merge=None,
               testreference=False, output=0, inputtype='source',
               checkvalidity=False, verbose=5, compatibility=False,
               returnmode='dump', returnvalue='full', force=False,
               forcelocaledir=False):
    self.reference = reference
    self.inipath = inipath
    self.l10nbase = l10nbase
    self.locales = locales
    self.fp = fp
    self.turbo = turbo
    self.accesskeys = accesskeys
    self.mercurial = mercurial
    self.merge = merge
    self.testreference = testreference
    self.output = output
    self.inputtype = inputtype
    self.checkvalidity = checkvalidity
    self.verbose = verbose
    self.compatibility = compatibility
    self.returnmode = returnmode
    self.returnvalue = returnvalue
    self.force = force
    self.forcelocaledir = forcelocaledir


def optionhelper(optionpack):
  '''
  Method for gathering needed information
  @param optionpack: instance of mozilla.core.main.CompareInit
  '''
  if optionpack.inputtype == 'source':
    '''Parse the l10n.ini file'''
    configparser = L10nConfigParser(pathname2url(optionpack.inipath))
    configparser.loadConfigs()
    '''dirs: directories with l10n files'''
    optionpack.dirs = configparser.directories()
    '''if doing all locales at once'''
    if optionpack.locales[0] == 'all':
      optionpack.locales.extend(configparser.allLocales())
      optionpack.locales.remove('all')
    optionpack.rcsClient = silme.io.Manager.get('file')
    '''we assume that filter.py is in the same path like l10n.ini'''
    try:
      optionpack.filter_py = Filter(optionpack.inipath)
    except Exception, e:
      optionpack.filter_py = None
      print "ERROR: Loading filter.py failed. Filtering turned off."
    '''EXPERIMENTAL: Read and update Mercurial repositories'''
    if optionpack.mercurial:
      from mozilla.core.hglayer import HgLayer
      HgLayer.run(optionpack.l10nbase, locales=optionpack.locales)
      HgLayer.run(configparser.baseurl)
    ''' '''
  elif optionpack.inputtype == 'dir':
    optionpack.rcsClient = silme.io.Manager.get('file')
  elif optionpack.inputtype == 'file':
    optionpack.rcsClient = silme.io.Manager.get('file')
  elif optionpack.inputtype == 'jar':
    raise Exception('Not implemented, yet')
  elif optionpack.inputtype == 'xpi':
    optionpack.xpi = ZipHandler(optionpack.inipath)
    try:
      optionpack.manifest =\
      ManifestParser.get_locales(optionpack.xpi.read('chrome.manifest','utf_8'))
    except KeyError, e: 
      raise KeyError('Could not find the chrome.manifest file in the ' +
                     'following archive: ' + optionpack.inipath +
                     ' ! Incompatible extension? ')
    optionpack.rcsClient = silme.io.Manager.get('jar')
    if optionpack.locales is None or not len(optionpack.locales) > 0:
      optionpack.locales = []
      for locale in optionpack.manifest.keys():
        if locale != optionpack.reference:
          optionpack.locales.append(locale)
      if len(optionpack.locales) is 0:
        print 'WARNING: This extension seems to be not localized.'
    optionpack.filter_py = None
  else:
    raise TypeError('There is not such an input type')
  optionpack.locales.sort()
  if optionpack.fp is None:
    optionpack.fp = silme.format.Manager.get('mozdiff', 'diff')
  if optionpack.turbo:
    optionpack.values=False
    optionpack.flags = ['added','removed','modified', 'replaced']
  else:
    optionpack.values=True
    optionpack.flags = ['added','removed','modified', 'replaced', 'unmodified']
  optionpack.objectType = 'entitylist' # object type to work with

def doCompare(optionpack):
  '''
  Method for reading and diffing of provided input.
  @param optionpack: instance of mozilla.core.main.CompareInit
  @return: instance of the Resultset class
  '''
  l10ndiffpackages = PackageDiff()
  l10npackages = Package()
  l10npackagesreference = Package()
  resultset = Resultset()
  for locale in optionpack.locales:
    localediffpackage = PackageDiff()
    localediffpackage.id = locale
    localel10npackage = Package()
    localel10npackage.id = locale
    referencel10npackage = Package()
    referencel10npackage.id = optionpack.reference
    
    if optionpack.inputtype == 'source':
      localediffpackage, localel10npackage, referencel10npackage = \
          read_and_compare_source(optionpack, locale, localediffpackage, localel10npackage,
                   referencel10npackage, l10npackagesreference)
    elif optionpack.inputtype == 'xpi':
      localediffpackage, localel10npackage, referencel10npackage = \
          read_and_compare_xpi(optionpack, locale, localediffpackage, localel10npackage,
                   referencel10npackage, l10npackagesreference)
    elif optionpack.inputtype == 'file':
      localediffpackage, localel10npackage, referencel10npackage = \
          read_and_compare_file(optionpack, locale, localediffpackage, localel10npackage,
                   referencel10npackage, l10npackagesreference)
    elif optionpack.inputtype == 'dir':
      localediffpackage, localel10npackage, referencel10npackage = \
          read_and_compare_dir(optionpack, locale, localediffpackage, localel10npackage,
                   referencel10npackage, l10npackagesreference)
    
    localediffpackage.id = locale
    l10ndiffpackages.add_package(localediffpackage)
    l10ndiffpackages.id = None
    l10npackages.add_package(localel10npackage)
    referencel10npackage.id = optionpack.reference
    l10npackagesreference = referencel10npackage
    if optionpack.checkvalidity:
      try:
        optionpack.fp.pyenchant_dict_init(locale)
      except OSError, e:
        l10ndiffpackages.package(locale).\
        log("WARNING", 'path: ' + os.path.join(optionpack.l10nbase, locale) + \
            '; type: OSError: ' + str(e))
        print 'WARNING: ' + 'path: ' + \
              os.path.join(optionpack.l10nbase, locale) + \
              '; type: OSError: ' + str(e)
        optionpack.checkvalidity = False
      except Exception, e:
        l10ndiffpackages.package(locale).\
        log("WARNING", 'path: ' + os.path.join(optionpack.l10nbase, locale) + \
            '; type: Exception' + str(e))
        print 'WARNING: ' + 'path: ' + \
              os.path.join(optionpack.l10nbase, locale) + \
              '; type: Exception: ' + str(e)
        optionpack.checkvalidity = False
    statistics = Statistics(locale, optionpack.reference)
    resultset.details[locale] = \
    optionpack.fp.make_l10npackagediff(l10ndiffpackages.package(locale),
                                      l10npackages.package(locale),
                                      l10npackagesreference,
                                      statistics=statistics, indent=0,
                                      optionpack=optionpack)
    resultset.stat_cats[locale] = statistics.get_statistics().keys()
    resultset.statistics[locale] = statistics
    resultset.summary[locale] = statistics.get_statistics()
  return resultset
