from dm.apache.config import ApacheConfigBuilder

from desire.dictionarywords import SYSTEM_CONFIG_PATH
from desire.dictionarywords import PYTHONPATH
from desire.dictionarywords import MEDIA_PREFIX
from desire.dictionarywords import MEDIA_ROOT
from desire.dictionarywords import URI_PREFIX

class ApacheConfigBuilder(ApacheConfigBuilder):

    def createConfigContent(self):
        configVars = {}
        configVars['SYSTEM_CONFIG_PATH'] = self.dictionary[SYSTEM_CONFIG_PATH]
        configVars['PYTHON_PATH'] = self.noTrailSlash(self.dictionary[PYTHONPATH])
        if self.debug:
            configVars['PYTHON_DEBUG'] = 'On'
        else:
            configVars['PYTHON_DEBUG'] = 'Off'
        configVars['URI_PREFIX'] = self.noTrailSlash(self.dictionary[URI_PREFIX])
        configVars['MEDIA_PREFIX'] = self.noTrailSlash(self.dictionary[MEDIA_PREFIX])
        configVars['MEDIA_ROOT'] = self.noTrailSlash(self.dictionary[MEDIA_ROOT])

        configContent = """# Desire auto-generated configuration.
<Location "%(URI_PREFIX)s/">
  SetEnv DESIRE_SETTINGS %(SYSTEM_CONFIG_PATH)s
  SetEnv PYTHONPATH %(PYTHON_PATH)s
  SetEnv DJANGO_SETTINGS_MODULE desire.django.settings.main
  SetHandler python-program
  PythonPath "'%(PYTHON_PATH)s'.split(':') + sys.path"
  PythonHandler django.core.handlers.modpython
  PythonDebug %(PYTHON_DEBUG)s
</Location>
        """ % configVars
        if configVars['MEDIA_PREFIX']:
            configContent += """
# Media location.
Alias %(MEDIA_PREFIX)s/ %(MEDIA_ROOT)s/
<Location "%(MEDIA_PREFIX)s/">
  SetHandler None
</Location>
            """ % configVars

        return configContent

    def noTrailSlash(self, path):
        if path and path[-1] == '/':
            path.pop()
        return path

