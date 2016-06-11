import re
from .base import Base

class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)

        self.name = 'identifier'
        self.mark = '[I]'
        self.rank = 300
        self.debug_enabled = False
        self._cache = []

        self._gather_identifier()

    def _gather_identifier(self):
        for w in re.findall(r'[\w\d]+', '\n'.join(self.vim.current.buffer)):
            if w not in self._cache:
                self._cache.append(w)

    def on_event(self, context):
        self._gather_identifier()

    def gather_candidates(self, context):
        return [{'word': w, 'kind': 'identifier'} for w in self._cache]
