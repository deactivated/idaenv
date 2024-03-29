from . import manager
from .cmd_utils import ArgumentParser


def cmd_update(mgr, opts):
    def print_plan(changes):
        if changes["create"]:
            print("  Updated:")
            for ep in changes["create"]:
                print("    - %s.%s" % (ep.dist, ep.name))

        if changes["delete"]:
            print("  Uninstalled:")
            for ep, path in changes["delete"]:
                print("    - %s.%s" % (ep.dist, ep.name))

    changed = False
    for mtype in ["plugins", "loaders", "procs"]:
        plan = mgr.plan_update(mtype)
        if plan["create"] or plan["delete"]:
            print("%s:" % mtype.capitalize())
            mgr.execute_update(mtype, plan)
            print_plan(plan)
            changed = True

    if not changed:
        print("No changes.")


def cmd_status(mgr, opts):
    def print_plan(changes):
        if changes["active"]:
            print("  Active:")
            for ep in changes["active"]:
                print("    - %s.%s" % (ep.dist, ep.name))

        if changes["create"]:
            print("  Need Update:")
            for ep in changes["create"]:
                print("    - %s.%s" % (ep.dist, ep.name))

        if changes["delete"]:
            print("  Uninstalled:")
            for ep, path in changes["delete"]:
                print("    - %s.%s" % (ep.dist, ep.name))

    for mtype in ["plugins", "loaders", "procs"]:
        plan = mgr.plan_update(mtype)
        if any(v for v in plan.values()):
            print("%s:" % mtype.capitalize())
            print_plan(plan)


def cmd_prefix(mgr, opts):
    print(mgr.user_dir)


def cmd_disable(mgr, opts):
    def print_plan(changes):
        if changes["delete"]:
            print("Uninstalled:")
            for ep, path in changes["delete"]:
                print("  - %s.%s" % (ep.dist, ep.name))

    for mtype in ["plugins", "loaders", "procs"]:
        wrapper = mgr.find_module_wrapper(mtype, opts.module_name)
        if wrapper is not None:
            plan = mgr.plan_delete([wrapper])
            print_plan(plan)
            mgr.execute_update(mtype, plan)


def main():
    ap = ArgumentParser()
    sps = ap.add_subparsers()

    sp = sps.add_parser("update", help="Update installed IDA modules.")
    sp.set_defaults(func=cmd_update)

    sp = sps.add_parser(
        "status", aliases=["list", "ls"], help="List installed IDA modules."
    )
    sp.set_defaults(func=cmd_status)

    sp = sps.add_parser("prefix", help="Print the idaenv install prefix.")
    sp.set_defaults(func=cmd_prefix)

    sp = sps.add_parser("disable", help="Disable an IDA module.")
    sp.add_argument("module_name")
    sp.set_defaults(func=cmd_disable)

    opts = ap.parse_args()
    if "func" not in opts:
        opts.func = cmd_status

    mgr = manager.get_default_manager()
    opts.func(mgr, opts)
