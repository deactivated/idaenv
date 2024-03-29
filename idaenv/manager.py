from __future__ import print_function

import re
import ast
import os
import hashlib

from . import entrypoints
from .utils import get_virtualenv_path, get_default_ida_usr


MODULE_TYPES = {"plugins", "loaders", "procs"}


PLUGIN_TEMPLATE = """
# EntryPointInfo(%(dist)r, %(group)r, %(name)r, %(module)r, %(attr)r)

from %(module)s import %(attr)s

def PLUGIN_ENTRY():
    return %(attr)s()
"""

PROC_TEMPLATE = """
# EntryPointInfo(%(dist)r, %(group)r, %(name)r, %(module)r, %(attr)r)

from %(module)s import *
"""


LOADER_TEMPLATE = """
# EntryPointInfo(%(dist)r, %(group)r, %(name)r, %(module)r, %(attr)r)

from %(module)s import *
"""


class PluginManager(object):
    """
    IDAPython plugin manager.
    """

    template_map = {
        "plugins": PLUGIN_TEMPLATE,
        "procs": PROC_TEMPLATE,
        "loaders": LOADER_TEMPLATE,
    }

    wrapper_rx = r"^[a-zA-Z][a-zA-Z0-9_]*_[0-9a-fA-F]+\.py$"

    def __init__(self, user_dir):
        self.user_dir = user_dir
        self.initialize_user_dir(self.user_dir)

        # XXX: Doing this here is a bit of a hack; pkg_resources needs to be
        # re-initialized whenever a module is installed or removed.
        entrypoints.refresh_entrypoint_caches()

    def initialize_user_dir(self, user_dir):
        if not user_dir:
            raise ValueError("Invalid user directory.")

        if not os.path.isdir(user_dir):
            os.makedirs(user_dir)

        for module_type in MODULE_TYPES:
            subdir_path = self.wrapper_dir(module_type)
            if not os.path.isdir(subdir_path):
                os.mkdir(subdir_path)

    def update_plugins(self):
        "Update the list of installed IDA plugins and wrapper files."
        # Update module wrappers
        for module_type in MODULE_TYPES:
            plan = self.plan_update(module_type)
            self.execute_update(module_type, plan)

    def find_module_wrapper(self, module_type, module_name):
        "Locate a module wrapper by name."
        wrapper_dir = self.wrapper_dir(module_type)
        wrappers = self.find_wrappers(wrapper_dir)
        for ep, wrapper_path in wrappers:
            if "%s.%s" % (ep.dist, ep.name) == module_name:
                return (ep, wrapper_path)

    def plan_delete(self, wrappers):
        return {"create": [], "delete": list(wrappers)}

    def plan_update(self, module_type):
        "Plan actions for synchronization."
        if module_type not in MODULE_TYPES:
            raise ValueError("Invalid module type: %r" % module_type)

        # Scan installed modules
        cur_modules = self.find_installed_modules(module_type)

        # Scan installed wrappers
        wrapper_dir = self.wrapper_dir(module_type)
        wrappers = self.find_wrappers(wrapper_dir)
        wrapper_set = set(ep for ep, _ in wrappers)

        # Active modules don't need a change
        active_modules = [ep for ep in cur_modules if ep in wrapper_set]

        # Delete wrappers for uninstalled modules
        to_delete = [(ep, path) for ep, path in wrappers if ep not in cur_modules]

        # Create wrappers for new modules
        to_create = [ep for ep in cur_modules if ep not in wrapper_set]

        return {"active": active_modules, "delete": to_delete, "create": to_create}

    def execute_update(self, module_type, changes):
        # Delete uninstalled modules
        for ep, wrapper_path in changes["delete"]:
            os.remove(wrapper_path)

        # Create new wrappers
        for ep in changes["create"]:
            self.write_entry_point_wrapper(module_type, ep)

    def write_entry_point_wrapper(self, module_type, ep_info):
        "Create a wrapper file for IDA."
        wrapper = self.template_map[module_type] % ep_info._asdict()

        dst_path = os.path.join(
            self.wrapper_dir(module_type), self.wrapper_name(ep_info)
        )
        print("Writing wrapper to %r..." % dst_path)
        with open(dst_path, "w") as wf:
            wf.write(wrapper)

    def entry_point_name(self, module_type):
        return "idapython_" + module_type

    def find_installed_modules(self, module_type):
        entry_point_group = self.entry_point_name(module_type)
        return set(entrypoints.iter_entry_point_info(entry_point_group))

    def wrapper_dir(self, module_type):
        "Return path to wrappers for a given module type."
        return os.path.join(self.user_dir, module_type)

    def find_wrappers(self, subdir):
        "Return a list of wrappers in a directory."
        wrappers = []
        for name in os.listdir(subdir):
            path = os.path.join(subdir, name)
            if os.path.isfile(path) and re.match(self.wrapper_rx, name):
                info = self.read_wrapper_info(path)
                if info:
                    wrappers.append((info, path))
        return wrappers

    def read_wrapper_info(self, path):
        """
        Extract the entry point loaded by a wrapper.
        """
        with open(path, "r") as f:
            # Wrappers generated by this manager will be small.
            content = f.read(4096)

        m = re.search(r"EntryPointInfo(\(.*?\))", content)
        if m:
            ep = ast.literal_eval(m.group(1))
            if (
                isinstance(ep, tuple)
                and len(ep) == 5
                and all(isinstance(elt, str) for elt in ep)
            ):
                return entrypoints.EntryPointInfo(*ep)

    def wrapper_name(self, ep_info):
        def clean(s):
            s = re.sub(r"(?<=[a-z])[A-Z]", lambda m: "_" + m.group(0).lower(), s)
            s = s.lower()
            s = re.sub(r"[^a-zA-Z0-9_]", "", s)
            s = s.strip("_")
            return s

        dist_part = clean(ep_info.dist[:15])
        name_part = clean(ep_info.name[:15])
        sha_part = hashlib.sha1("_".join(ep_info).encode("utf8")).hexdigest()[:6]
        return "%s_%s_%s.py" % (dist_part, name_part, sha_part)


def get_default_manager(require_venv=False):
    """
    Initialize a plugin manager based on the current environment.
    """
    cur_env = get_virtualenv_path()
    if cur_env:
        ida_path = os.path.join(cur_env, "ida")
    elif require_venv:
        raise RuntimeError("Not in virtual environment.")
    else:
        print("Warning: operating outside of a virtual environment.")
        ida_path = get_default_ida_usr()

    return PluginManager(ida_path)
