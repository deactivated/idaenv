import re
import email.parser
from collections import namedtuple

try:
    # Try the backport package
    import importlib_metadata as importlib_metadata

    pkg_resources = None
except ImportError:
    # Try importlib.metadata from stdlib otherwise
    import importlib.metadata as importlib_metadata

    pkg_resources = None
except ImportError:
    # Use pkg_resources if importlib.metadata isn't available
    importlib_metadata = None
    import pkg_resources


EntryPointInfo = namedtuple("EntryPointInfo", "dist group name module attr")


def refresh_entrypoint_caches():
    if pkg_resources is not None:
        pkg_resources._initialize_master_working_set()


def _importlib_entry_points_legacy(group_name):
    """
    The last version of importlib-metadata avilable for python 2.7 doesn't
    provide access to dist from the entrypoint object.
    """
    matching_eps = []
    for dist in importlib_metadata.distributions():
        for ep in dist.entry_points:
            if ep.group == group_name:
                ep.dist = dist
                matching_eps.append(ep)
    return matching_eps


def _importlib_entry_points(group_name):
    # Handle python 2.7
    if not hasattr(importlib_metadata.EntryPoint, "dist"):
        return _importlib_entry_points_legacy(group_name)

    # Handle more recent API change around entry_points enumeration
    eps = importlib_metadata.entry_points()
    if hasattr(eps, "select"):
        return eps.select(group=group_name)
    else:
        if group_name in eps:
            return eps[group_name]


def _importlib_iter_entry_point_info(group_name):
    eps = _importlib_entry_points(group_name)
    if eps is None:
        return
    for ep in eps:
        key = re.sub(r"[-_.]+", "-", ep.dist.metadata["Name"]).lower()
        yield EntryPointInfo(key, group_name, ep.name, ep.module, ep.attr)


def _pkg_resources_normalized_name(dist):
    metadata = dist.get_metadata(dist.PKG_INFO)
    parsed = email.parser.Parser().parsestr(metadata)
    key = re.sub(r"[-_.]+", "-", parsed["Name"]).lower()
    return key


def _pkg_resources_iter_entry_point_info(group_name):
    for ep in pkg_resources.iter_entry_points(group_name):
        attr = ep.attrs[0] if ep.attrs else ""
        yield EntryPointInfo(
            _pkg_resources_normalized_name(ep.dist),
            group_name,
            ep.name,
            ep.module_name,
            attr,
        )


def iter_entry_point_info(group_name):
    if importlib_metadata is not None:
        return _importlib_iter_entry_point_info(group_name)
    else:
        return _pkg_resources_iter_entry_point_info(group_name)
