from battery_monitor import core


def test_basic_status_structure():
    status = core.get_basic_battery_status()
    if status is not None:
        assert 'percent' in status
        assert 'plugged' in status
        assert 'secsleft' in status


def test_version_present():
    version = core.__version__
    assert isinstance(version, str)
    assert len(version.split('.')) == 3