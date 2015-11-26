import arc_cache


def test_import():
    """from arc_cache import arc_cache works"""
    assert 'arc_cache' in vars(arc_cache)
    assert callable(arc_cache.arc_cache)
