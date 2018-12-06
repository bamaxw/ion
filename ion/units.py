'''Helper classes and functions facilitating dealing with various metrics'''


class EarthRadius: # pylint: disable=too-few-public-methods
    '''Earth Radius'''
    kilometers = 6371
    miles = 3959
    km = kilometers


def to_kb(byte_count: int) -> float:
    '''Converts bytes to kilobytes'''
    return byte_count / 1024
