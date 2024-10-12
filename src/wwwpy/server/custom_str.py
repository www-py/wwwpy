class CustomStr(str):
    pass


def get_root_folder_or_fail() -> CustomStr:
    import sys
    only_custom = [p for p in sys.path if isinstance(p, CustomStr)]

    if len(only_custom) != 1:
        raise ValueError('Cannot find root folder')

    return only_custom[0]
