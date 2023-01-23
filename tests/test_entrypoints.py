from idaenv import entrypoints


def test_imports():
    assert (entrypoints.pkg_resources is None) ^ (
        entrypoints.importlib_metadata is None
    )

    # inject pkg_resources for later tests
    if entrypoints.pkg_resources is None:
        import pkg_resources
        entrypoints.pkg_resources = pkg_resources


def test_distinfo_pkg(distinfo_pkg):
    entrypoints.refresh_entrypoint_caches()
    pr_eps = list(entrypoints._pkg_resources_iter_entry_point_info("entries"))
    assert len(pr_eps) == 2
    if entrypoints.importlib_metadata is not None:
        il_eps = list(entrypoints._importlib_iter_entry_point_info("entries"))
        assert sorted(il_eps) == sorted(pr_eps)


def test_distinfo_pkg_dot_legacy(distinfo_pkg_with_dot_legacy):
    entrypoints.refresh_entrypoint_caches()
    pr_eps = list(entrypoints._pkg_resources_iter_entry_point_info("entries"))
    assert len(pr_eps) == 2

    if entrypoints.importlib_metadata is not None:
        il_eps = list(entrypoints._importlib_iter_entry_point_info("entries"))
        assert sorted(il_eps) == sorted(pr_eps)


def test_egginfo_pkg(egginfo_pkg):
    entrypoints.refresh_entrypoint_caches()
    pr_eps = list(entrypoints._pkg_resources_iter_entry_point_info("entries"))
    assert len(pr_eps) == 1

    if entrypoints.importlib_metadata is not None:
        il_eps = list(entrypoints._importlib_iter_entry_point_info("entries"))
        assert sorted(il_eps) == sorted(pr_eps)
