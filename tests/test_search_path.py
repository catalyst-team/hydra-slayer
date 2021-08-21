from hydra_slayer.search_path import SearchPath, SearchPathEntry


# SearchPathEntry tests
def test_search_path_entry_from_description():
    """@TODO: Docs. Contribution is welcome."""
    assert SearchPathEntry(path="numpy", alias="numpy") == SearchPathEntry.from_description(
        "numpy"
    )
    assert SearchPathEntry(path="numpy", alias="np") == SearchPathEntry.from_description(
        ("numpy", "np")
    )
    assert SearchPathEntry(
        path="numpy.linalg", alias="linalg"
    ) == SearchPathEntry.from_description("numpy.linalg")
    assert SearchPathEntry(path="numpy.linalg", alias="npl") == SearchPathEntry.from_description(
        ("numpy.linalg", "npl")
    )


def test_search_path_entry_is_referenced_by_name():
    """@TODO: Docs. Contribution is welcome."""
    entry = SearchPathEntry(path="numpy", alias="numpy")
    assert entry.is_referenced_by("numpy.linalg")
    assert entry.is_referenced_by("numpy.linalg.norm")
    assert not entry.is_referenced_by("num")


def test_search_path_entry_resolve_by_name():
    """@TODO: Docs. Contribution is welcome."""
    entry = SearchPathEntry(path="numpy", alias="numpy")
    assert entry.resolve("numpy.linalg") == "numpy.linalg"


def test_search_path_is_referenced_by_alias():
    """@TODO: Docs. Contribution is welcome."""
    entry = SearchPathEntry(path="numpy", alias="np")
    assert entry.is_referenced_by("np")
    assert entry.is_referenced_by("np.linalg.norm")
    assert not entry.is_referenced_by("numpy")


def test_search_path_resolve_by_alias():
    """@TODO: Docs. Contribution is welcome."""
    entry = SearchPathEntry(path="numpy", alias="np")
    assert entry.resolve("np") == "numpy"
    assert entry.resolve("np.linalg.norm") == "numpy.linalg.norm"


def test_search_path_is_referenced_by_name_with_parent():
    """@TODO: Docs. Contribution is welcome."""
    entry = SearchPathEntry(path="numpy.linalg", alias="linalg")
    assert entry.is_referenced_by("linalg")
    assert entry.is_referenced_by("linalg.norm")
    assert not entry.is_referenced_by("numpy.linalg.norm")


def test_search_path_resolve_by_name_with_parent():
    """@TODO: Docs. Contribution is welcome."""
    entry = SearchPathEntry(path="numpy.linalg", alias="linalg")
    assert entry.resolve("linalg") == "numpy.linalg"
    assert entry.resolve("linalg.norm") == "numpy.linalg.norm"


def test_search_path_is_referenced_by_alias_with_parent():
    """@TODO: Docs. Contribution is welcome."""
    entry = SearchPathEntry(path="numpy.linalg", alias="npl")
    assert entry.is_referenced_by("npl")
    assert entry.is_referenced_by("npl.norm")
    assert not entry.is_referenced_by("numpy.linalg.norm")


def test_search_path_resolve_by_alias_with_parent():
    """@TODO: Docs. Contribution is welcome."""
    entry = SearchPathEntry(path="numpy.linalg", alias="npl")
    assert entry.resolve("npl") == "numpy.linalg"
    assert entry.resolve("npl.norm") == "numpy.linalg.norm"


# SearchPath tests
def test_search_path_from_description():
    """@TODO: Docs. Contribution is welcome."""
    assert SearchPath(
        [
            SearchPathEntry(path="numpy.linalg", alias="linalg"),
            SearchPathEntry(path="numpy.linalg", alias="npl"),
            SearchPathEntry(path="torch.nn", alias="nn"),
            SearchPathEntry(path="torch.nn.functional", alias="F"),
        ]
    ) == SearchPath.from_description(
        ["numpy.linalg", ("numpy.linalg", "npl"), "torch.nn", ("torch.nn.functional", "F")]
    )
