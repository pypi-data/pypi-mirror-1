import unicodedata
import silme.format
from mozilla.core.statistics import Statistics
from mozilla.core.main import *
import copy
from mozilla.playground.hacks import *
import mozilla.fp.diff
import mozilla.core.compatibilityPack

try: 
  import json
except ImportError:
  import simplejson as json

mozilla.fp.diff.register(silme.format.Manager)

def compareLocales(optionpack):
  '''
  Method for accessing the compare-locales library 
  and dumping or returning the result.
  '''
  optionpack.fp = silme.format.Manager.get('mozdiff')
  results = []
  stats = []
  optionhelper(optionpack)
  
  # start the compare process
  if optionpack.compatibility:
    result = mozilla.core.main.compareApp(optionpack, optionpack.merge)
  else:
    result = doCompare(optionpack)

  # prepare results
  for locale in optionpack.locales:
    if result.details[locale] is not None and len(result.details[locale]) > 0:
      if optionpack.verbose > 0:
        if optionpack.returnvalue == 'full' or \
        optionpack.returnvalue == 'results':
          results.append(''.join(optionpack.fp.serialize(copy.deepcopy\
                                                    (result.details[locale]),
                                          output=optionpack.output,
                                          space=u'', indent=0)))
        if optionpack.returnvalue == 'full_json' or \
        optionpack.returnvalue == 'results_json':
          results.append(mozilla.core.main.toJSON(result.details[locale]))
  # prepare statistics
  for locale in optionpack.locales:
    if optionpack.returnvalue == 'full' or \
    optionpack.returnvalue == 'statistics':
      stats.append(result.statistics[locale].dump_statistics())
      if not optionpack.turbo:
        stats.append(result.statistics[locale].\
                    dump_percentage(['unmodifiedEntities',
                                    'missingEntities',
                                    'missingEntitiesInMissingFiles'],
                                   'changedEntities'))
    if optionpack.returnvalue == 'full_json' or \
    optionpack.returnvalue == 'statistics_json':
      stats.append(result.statistics[locale].to_json())

  if optionpack.returnmode == 'array':
    # return an array
    return [''.join(results).encode('utf_8'), ''.join(stats).encode('utf_8')]
  elif optionpack.returnvalue == 'full_json' or \
           optionpack.returnvalue == 'results_json' or \
           optionpack.returnvalue == 'statistics_json':
    if optionpack.returnvalue != 'statistics_json':
      print json.dumps(results, indent=2)
    if optionpack.returnvalue != 'results_json':
      print json.dumps(stats, indent=2)
  
  else:
    # dump the results to command line
    print ''.join(results).encode('utf_8')
    print ''.join(stats).encode('utf_8')
  