"""
Automatic plugin loader.
"""

from .manager import PluginManager


class PluginLoader:
    """
    IDAPython Plugin Loader
    """
    def __init__(self):
        self.manager = PluginManager()

    def install(self):
        "Install IDB open hook and initialize user directory."
        self.manager.install()
        import idaapi

        print("Installing plugin loader...")
        self.initialize_temp_dir()
        self.update_plugin_info()

        idaapi.notify_when(idaapi.NW_OPENIDB, self.idb_open_hook)
        idaapi.notify_when(idaapi.NW_TERMIDA, self.ida_term_hook)

    def idb_open_hook(self, nw=None, old_db=None):
        "Hook called when an IDB is opened."
        # self.update_plugin_info()
        pass

    def ida_term_hook(self, nw_code=None):
        "Hook called when an IDA is terminated."
        pass


# Default global plugin loader instance
_plugin_loader = PluginLoader()


def install_plugin_loader():
    "Watch installed IDA plugins and reload them when opening an IDB."
    global _plugin_loader
    _plugin_loader.install()
