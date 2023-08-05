'''tzinfo timezone information for Atlantic/Reykjavik.'''
from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as d
from pytz.tzinfo import memorized_ttinfo as i

class Reykjavik(DstTzInfo):
    '''Atlantic/Reykjavik timezone definition. See datetime.tzinfo for details'''

    zone = 'Atlantic/Reykjavik'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1908,1,1,1,27,48),
d(1917,2,20,0,0,0),
d(1917,10,21,1,0,0),
d(1918,2,20,0,0,0),
d(1918,11,16,1,0,0),
d(1939,4,30,0,0,0),
d(1939,11,29,2,0,0),
d(1940,2,25,3,0,0),
d(1940,11,3,2,0,0),
d(1941,3,2,2,0,0),
d(1941,11,2,2,0,0),
d(1942,3,8,2,0,0),
d(1942,10,25,2,0,0),
d(1943,3,7,2,0,0),
d(1943,10,24,2,0,0),
d(1944,3,5,2,0,0),
d(1944,10,22,2,0,0),
d(1945,3,4,2,0,0),
d(1945,10,28,2,0,0),
d(1946,3,3,2,0,0),
d(1946,10,27,2,0,0),
d(1947,4,6,2,0,0),
d(1947,10,26,2,0,0),
d(1948,4,4,2,0,0),
d(1948,10,24,2,0,0),
d(1949,4,3,2,0,0),
d(1949,10,30,2,0,0),
d(1950,4,2,2,0,0),
d(1950,10,22,2,0,0),
d(1951,4,1,2,0,0),
d(1951,10,28,2,0,0),
d(1952,4,6,2,0,0),
d(1952,10,26,2,0,0),
d(1953,4,5,2,0,0),
d(1953,10,25,2,0,0),
d(1954,4,4,2,0,0),
d(1954,10,24,2,0,0),
d(1955,4,3,2,0,0),
d(1955,10,23,2,0,0),
d(1956,4,1,2,0,0),
d(1956,10,28,2,0,0),
d(1957,4,7,2,0,0),
d(1957,10,27,2,0,0),
d(1958,4,6,2,0,0),
d(1958,10,26,2,0,0),
d(1959,4,5,2,0,0),
d(1959,10,25,2,0,0),
d(1960,4,3,2,0,0),
d(1960,10,23,2,0,0),
d(1961,4,2,2,0,0),
d(1961,10,22,2,0,0),
d(1962,4,1,2,0,0),
d(1962,10,28,2,0,0),
d(1963,4,7,2,0,0),
d(1963,10,27,2,0,0),
d(1964,4,5,2,0,0),
d(1964,10,25,2,0,0),
d(1965,4,4,2,0,0),
d(1965,10,24,2,0,0),
d(1966,4,3,2,0,0),
d(1966,10,23,2,0,0),
d(1967,4,2,2,0,0),
d(1967,10,29,2,0,0),
d(1968,4,7,2,0,0),
        ]

    _transition_info = [
i(-5280,0,'RMT'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,3600,'ISST'),
i(-3600,0,'IST'),
i(0,0,'GMT'),
        ]

Reykjavik = Reykjavik()

