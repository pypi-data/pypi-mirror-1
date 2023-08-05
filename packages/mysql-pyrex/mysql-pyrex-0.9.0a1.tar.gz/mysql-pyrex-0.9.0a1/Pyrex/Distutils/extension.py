# Modifying the base Extension class so we can specify pyrex_include_dirs.

import distutils.extension

class PyrexExtension (distutils.extension.Extension):

    def __init__(self, name, sources, **kwargs):
        self.pyrex_include_dirs = kwargs.pop('pyrex_include_dirs', [])
        self.compile_time_symbols = kwargs.pop('compile_time_symbols', {})
        distutils.extension.Extension.__init__(self, name, sources, **kwargs)
