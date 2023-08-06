from App.Management import Tabs
from AccessControl import getSecurityManager, Unauthorized

# Monkeypatch to add a registry tab to the ZMI tabs.
# XXX Maybe just patch the root object?
def filtered_manage_options(self, REQUEST=None):
    tabs = self._old_filtered_manage_options(REQUEST)
    secman = getSecurityManager()
    if len(tabs) \
      and secman.checkPermission("View management screens", self.this()):
        tabs.append({'label': 'Component Registry',
                     'action': '@@registry.html'})
    return tabs

Tabs._old_filtered_manage_options = Tabs.filtered_manage_options
Tabs.filtered_manage_options = filtered_manage_options
