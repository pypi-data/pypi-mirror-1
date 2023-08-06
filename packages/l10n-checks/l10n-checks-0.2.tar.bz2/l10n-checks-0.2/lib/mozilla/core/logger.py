import silme.core.logger
import silme.diff

def get_logs(self, type=None):
    if hasattr(self, 'logs'):
      if type is not None:
        return [pos for pos in self.logs if pos[0] in type]
      else:
        return self.logs
    return []

silme.core.logger.get_logs = get_logs

silme.core.EntityList.get_logs = get_logs

silme.core.Structure.get_logs = get_logs


silme.core.Blob.log = silme.core.logger.log
silme.core.Blob.get_logs = silme.core.logger.get_logs


silme.diff.list.EntityListDiff.log = silme.core.logger.log
silme.diff.list.EntityListDiff.get_logs = silme.core.logger.get_logs

silme.diff.blob.BlobDiff.log = silme.core.logger.log
silme.diff.blob.BlobDiff.get_logs = silme.core.logger.get_logs

silme.diff.StructureDiff.log = silme.core.logger.log
silme.diff.StructureDiff.get_logs = silme.core.logger.get_logs

silme.diff.PackageDiff.log = silme.core.logger.log
silme.diff.PackageDiff.get_logs = silme.core.logger.get_all_logs

@staticmethod
def append_logs(logs, statistics, optionpack=None):
  loglist = []
  if isinstance(logs, list):
    for log in logs:
      statistics.add_stat(log[0], 1)
      if optionpack is not None:
        if log[0] == 'WARNING' and optionpack.verbose < 2:
          continue
        elif log[0] == 'ERROR' and optionpack.verbose < 1:
          continue
      loglist.append((log[1], log[0]+': '))
  return loglist

import mozilla.fp.diff.mozdiff

mozilla.fp.diff.mozdiff.MozDiffFormatParser.append_logs = append_logs
