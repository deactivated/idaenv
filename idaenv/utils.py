import sys
import os


IDAUSR_DEFAULTS = {
    "darwin": "$HOME/.idapro",
    "linux": "$HOME/.idapro",
    "win": "%APPDATA%/Hex-Rays/IDA Pro"
}


def real_path(path):
    abspath = os.path.abspath(path)
    if os.path.isdir(abspath):
        return abspath


def get_virtualenv_path():
    """
    Return the absolute path of the current virtualenv.  Return None if not in
    a virtualenv -- or if the apparent virtualenv path is nonsensical.
    """
    if hasattr(sys, 'real_prefix'):
        if sys.real_prefix != sys.prefix:
            return real_path(sys.prefix)

    elif hasattr(sys, 'base_prefix'):
        if sys.base_prefix != sys.prefix:
            return real_path(sys.prefix)


def get_platform():
    "Return a standardized platform name."
    if sys.platform.startswith("linux"):
        return "linux"
    if sys.platform.startswith("win"):
        return "win"
    if sys.platform.startswith("darwin"):
        return "darwin"

    raise RuntimeError("Surprising platform name.")


def get_default_ida_usr():
    "Return the default value of IDAUSR for the current system."
    return os.path.expandvars(IDAUSR_DEFAULTS[get_platform()])


def append_ida_usr(new_dir, preserve_default=True):
    "Append a directory to the IDAUSR environment variable."
    if "IDAUSR" in os.environ:
        path = os.pathsep.split(os.environ["IDAUSR"])
    else:
        if preserve_default:
            path = [get_default_ida_usr()]
        else:
            path = []

    path.append(new_dir)
    os.environ["IDAUSR"] = os.pathsep.join(path)
