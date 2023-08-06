import os
from urlparse import urlparse
from urllib import url2pathname
try:
  from mercurial.dispatch import dispatch as hgrun
except ImportError, e:
  raise ImportError('Mercurial not found in the PYTHONPATH! ('+str(e)+')')

class HgLayer:
  '''
  Class for accessing a local Mercurial installation 
  '''

  @staticmethod
  def run(base, server='http://hg.mozilla.org/', locales=None):
    '''
    This method pulls and updates (with -C!) a given HG repository, or if 
    that repository does not exists locally, clones it.
    @attention: It assumes that the repository name is the basename of the 
    given local path!
    @param base: path to the local repository. If it does not exist, it will 
    be created
    @param server: (optional) complete url to the Mercurial server 
    (not to the repository). It must end with a slash!
    @param locales: (optional) list value. List of locales (hg repositories) 
    to use. 
    '''
    wd = os.getcwd()
    path = url2pathname(urlparse(base)[2])
    if not os.path.exists(path):
      os.makedirs(path)
    os.chdir(path)
    repository = os.path.split(path)
    if not repository[1]:
      repository = os.path.split(repository[0])
    lcdir = server + repository[1]
    if locales is not None:
      for locale in locales:
        lcrepo = lcdir + '/' + locale
        if os.path.isdir(os.path.join(os.getcwd(), locale)) \
        and os.path.isdir(os.path.join(os.getcwd(), locale, '.hg')):
          lcd = os.getcwd()
          os.chdir(os.path.join(os.getcwd(), locale))
          hgrun(['pull'])
          hgrun(['update', '-C'])
          os.chdir(lcd)
        else: 
          hgrun(['clone', lcrepo])
    else:
      if os.path.isdir(os.path.join(os.getcwd(), '.hg')):
        hgrun(['pull'])
        hgrun(['update', '-C'])
      else: 
        rcd = os.getcwd()
        os.chdir(repository[0])
        hgrun(['clone', lcdir])
        os.chdir(rcd)
    os.chdir(wd)
