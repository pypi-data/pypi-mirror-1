
from xix.utils.config import configFactory
cfg = configFactory('loggrok-unittest.cfg')
fname = cfg.files.actions

# Globals for various tests
loggrok_actions_level_globs = {'fname' : fname}
loggrok_actions_messageCategory_globs = loggrok_actions_level_globs
loggrok_log_LogStream_entry_default_globs = {'filename' : cfg.files.entryTest}

