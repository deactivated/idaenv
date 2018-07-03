from __future__ import print_function

import re
import ast
import os
import hashlib
import pkg_resources

from collections import namedtuple

from .utils import get_virtualenv_path


MODULE_TYPES = {"plugins", "loaders", "procs"}


PLUGIN_TEMPLATE = """
import pkg_resources

def PLUGIN_ENTRY():
    ep = pkg_resources.load_entry_point(%(dist)r, %(group)r, %(name)r)
    return ep()
"""

PROC_TEMPLATE = """
import pkg_resources

__ep = pkg_resources.load_entry_point(%(dist)r, %(group)r, %(name)r)
from __ep import *
"""


LOADER_TEMPLATE = """
import pkg_resources

__ep = pkg_resources.load_entry_point(%(dist)r, %(group)r, %(name)r)
from __ep import *
"""


EntryPointInfo = namedtuple("EntryPointInfo", "dist group name")


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
        pkg_resources._initialize_master_working_set()

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
        active_modules = [ep for ep in cur_modules
                          if ep in wrapper_set]

        # Delete wrappers for uninstalled modules
        to_delete = [(ep, path) for ep, path in wrappers
                     if ep not in cur_modules]

        # Create wrappers for new modules
        to_create = [ep for ep in cur_modules
                     if ep not in wrapper_set]

        return {
            "active": active_modules,
            "delete": to_delete,
            "create": to_create
        }

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

        dst_path = os.path.join(self.wrapper_dir(module_type),
                                self.wrapper_name(ep_info))
        print("Writing wrapper to %r..." % dst_path)
        with open(dst_path, "w") as wf:
            wf.write(wrapper)

    def entry_point_name(self, module_type):
        return "idapython_" + module_type

    def find_installed_modules(self, module_type):
        entry_point_group = self.entry_point_name(module_type)
        cur_modules = set()
        for ep in pkg_resources.iter_entry_points(entry_point_group):
            cur_modules.add(EntryPointInfo(ep.dist.key,
                                           entry_point_group,
                                           ep.name))
        return cur_modules

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

        m = re.search(r"load_entry_point(\(.*?\))", content)
        if m:
            ep = ast.literal_eval(m.group(1))
            if (isinstance(ep, tuple) and
                    len(ep) == 3 and
                    all(isinstance(elt, str) for elt in ep)):
                return EntryPointInfo(*ep)

    def wrapper_name(self, ep_info):
        def clean(s):
            s = re.sub(r"(?<=[a-z])[A-Z]",
                       lambda m: "_" + m.group(0).lower(), s)
            s = s.lower()
            s = re.sub(r"[^a-zA-Z0-9_]", "", s)
            s = s.strip("_")
            return s

        dist_part = clean(ep_info.dist[:15])
        name_part = clean(ep_info.name[:15])
        sha_part = hashlib.sha1("_".join(ep_info)).hexdigest()[:6]
        return "%s_%s_%s.py" % (dist_part, name_part, sha_part)


class VenvPluginManager(PluginManager):

    def __init__(self):
        cur_env = get_virtualenv_path()
        if not cur_env:
            raise RuntimeError("Not in virtualenv.")

        ida_path = os.path.join(cur_env, "ida")
        super(VenvPluginManager, self).__init__(ida_path)
