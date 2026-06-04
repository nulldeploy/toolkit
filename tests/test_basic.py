# tests/test_basic.py
def test_imports():
    from commands import scan, backup, monitor
    assert scan
    assert backup
    assert monitor