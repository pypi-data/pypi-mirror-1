'''tzinfo timezone information for America/Indiana/Indianapolis.'''
from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as d
from pytz.tzinfo import memorized_ttinfo as i

class Indianapolis(DstTzInfo):
    '''America/Indiana/Indianapolis timezone definition. See datetime.tzinfo for details'''

    zone = 'America/Indiana/Indianapolis'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1918,3,31,8,0,0),
d(1918,10,27,7,0,0),
d(1919,3,30,8,0,0),
d(1919,10,26,7,0,0),
d(1941,6,22,8,0,0),
d(1941,9,28,7,0,0),
d(1942,2,9,8,0,0),
d(1945,8,14,23,0,0),
d(1945,9,30,7,0,0),
d(1946,4,28,8,0,0),
d(1946,9,29,7,0,0),
d(1947,4,27,8,0,0),
d(1947,9,28,7,0,0),
d(1948,4,25,8,0,0),
d(1948,9,26,7,0,0),
d(1949,4,24,8,0,0),
d(1949,9,25,7,0,0),
d(1950,4,30,8,0,0),
d(1950,9,24,7,0,0),
d(1951,4,29,8,0,0),
d(1951,9,30,7,0,0),
d(1952,4,27,8,0,0),
d(1952,9,28,7,0,0),
d(1953,4,26,8,0,0),
d(1953,9,27,7,0,0),
d(1954,4,25,8,0,0),
d(1954,9,26,7,0,0),
d(1955,4,24,8,0,0),
d(1957,9,29,7,0,0),
d(1958,4,27,8,0,0),
d(1969,4,27,7,0,0),
d(1969,10,26,6,0,0),
d(1970,4,26,7,0,0),
d(1970,10,25,6,0,0),
        ]

    _transition_info = [
i(-21600,0,'CST'),
i(-18000,3600,'CDT'),
i(-21600,0,'CST'),
i(-18000,3600,'CDT'),
i(-21600,0,'CST'),
i(-18000,3600,'CDT'),
i(-21600,0,'CST'),
i(-18000,3600,'CWT'),
i(-18000,3600,'CPT'),
i(-21600,0,'CST'),
i(-18000,3600,'CDT'),
i(-21600,0,'CST'),
i(-18000,3600,'CDT'),
i(-21600,0,'CST'),
i(-18000,3600,'CDT'),
i(-21600,0,'CST'),
i(-18000,3600,'CDT'),
i(-21600,0,'CST'),
i(-18000,3600,'CDT'),
i(-21600,0,'CST'),
i(-18000,3600,'CDT'),
i(-21600,0,'CST'),
i(-18000,3600,'CDT'),
i(-21600,0,'CST'),
i(-18000,3600,'CDT'),
i(-21600,0,'CST'),
i(-18000,3600,'CDT'),
i(-21600,0,'CST'),
i(-18000,0,'EST'),
i(-21600,0,'CST'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
i(-14400,3600,'EDT'),
i(-18000,0,'EST'),
        ]

Indianapolis = Indianapolis()

