from one.libraries.guid.utils import validate_guid


def test_valid_guid():
    assert validate_guid("07742cab407e4e8089ebfd191acbb752") is True


def test_is_valid_dashed_guid():
    assert validate_guid("07742cab-407e-4e80-89eb-fd191acbb752") is True
