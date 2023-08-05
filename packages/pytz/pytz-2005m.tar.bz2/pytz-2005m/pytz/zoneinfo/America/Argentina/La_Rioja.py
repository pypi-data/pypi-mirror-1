'''tzinfo timezone information for America/Argentina/La_Rioja.'''
from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as d
from pytz.tzinfo import memorized_ttinfo as i

class La_Rioja(DstTzInfo):
    '''America/Argentina/La_Rioja timezone definition. See datetime.tzinfo for details'''

    zone = 'America/Argentina/La_Rioja'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1920,5,1,4,16,48),
d(1930,12,1,4,0,0),
d(1931,4,1,3,0,0),
d(1931,10,15,4,0,0),
d(1932,3,1,3,0,0),
d(1932,11,1,4,0,0),
d(1933,3,1,3,0,0),
d(1933,11,1,4,0,0),
d(1934,3,1,3,0,0),
d(1934,11,1,4,0,0),
d(1935,3,1,3,0,0),
d(1935,11,1,4,0,0),
d(1936,3,1,3,0,0),
d(1936,11,1,4,0,0),
d(1937,3,1,3,0,0),
d(1937,11,1,4,0,0),
d(1938,3,1,3,0,0),
d(1938,11,1,4,0,0),
d(1939,3,1,3,0,0),
d(1939,11,1,4,0,0),
d(1940,3,1,3,0,0),
d(1940,7,1,4,0,0),
d(1941,6,15,3,0,0),
d(1941,10,15,4,0,0),
d(1943,8,1,3,0,0),
d(1943,10,15,4,0,0),
d(1946,3,1,3,0,0),
d(1946,10,1,4,0,0),
d(1963,10,1,3,0,0),
d(1963,12,15,4,0,0),
d(1964,3,1,3,0,0),
d(1964,10,15,4,0,0),
d(1965,3,1,3,0,0),
d(1965,10,15,4,0,0),
d(1966,3,1,3,0,0),
d(1966,10,15,4,0,0),
d(1967,4,2,3,0,0),
d(1967,10,1,4,0,0),
d(1968,4,7,3,0,0),
d(1968,10,6,4,0,0),
d(1969,4,6,3,0,0),
d(1969,10,5,4,0,0),
d(1974,1,23,3,0,0),
d(1974,5,1,2,0,0),
d(1988,12,1,3,0,0),
d(1989,3,5,2,0,0),
d(1989,10,15,3,0,0),
d(1990,3,4,2,0,0),
d(1990,10,21,3,0,0),
d(1991,3,1,2,0,0),
d(1991,5,7,4,0,0),
d(1991,10,20,3,0,0),
d(1992,3,1,2,0,0),
d(1992,10,18,3,0,0),
d(1993,3,7,2,0,0),
d(1999,10,3,3,0,0),
d(2000,3,3,3,0,0),
d(2004,6,1,3,0,0),
d(2004,6,20,4,0,0),
        ]

    _transition_info = [
i(-15420,0,'CMT'),
i(-14400,0,'ART'),
i(-10800,3600,'ARST'),
i(-14400,0,'ART'),
i(-10800,3600,'ARST'),
i(-14400,0,'ART'),
i(-10800,3600,'ARST'),
i(-14400,0,'ART'),
i(-10800,3600,'ARST'),
i(-14400,0,'ART'),
i(-10800,3600,'ARST'),
i(-14400,0,'ART'),
i(-10800,3600,'ARST'),
i(-14400,0,'ART'),
i(-10800,3600,'ARST'),
i(-14400,0,'ART'),
i(-10800,3600,'ARST'),
i(-14400,0,'ART'),
i(-10800,3600,'ARST'),
i(-14400,0,'ART'),
i(-10800,3600,'ARST'),
i(-14400,0,'ART'),
i(-10800,3600,'ARST'),
i(-14400,0,'ART'),
i(-10800,3600,'ARST'),
i(-14400,0,'ART'),
i(-10800,3600,'ARST'),
i(-14400,0,'ART'),
i(-10800,3600,'ARST'),
i(-14400,0,'ART'),
i(-10800,3600,'ARST'),
i(-14400,0,'ART'),
i(-10800,3600,'ARST'),
i(-14400,0,'ART'),
i(-10800,3600,'ARST'),
i(-14400,0,'ART'),
i(-10800,3600,'ARST'),
i(-14400,0,'ART'),
i(-10800,3600,'ARST'),
i(-14400,0,'ART'),
i(-10800,3600,'ARST'),
i(-14400,0,'ART'),
i(-10800,0,'ART'),
i(-7200,3600,'ARST'),
i(-10800,0,'ART'),
i(-7200,3600,'ARST'),
i(-10800,0,'ART'),
i(-7200,3600,'ARST'),
i(-10800,0,'ART'),
i(-7200,3600,'ARST'),
i(-14400,0,'WART'),
i(-10800,0,'ART'),
i(-7200,3600,'ARST'),
i(-10800,0,'ART'),
i(-7200,3600,'ARST'),
i(-10800,0,'ART'),
i(-10800,0,'ARST'),
i(-10800,0,'ART'),
i(-14400,0,'WART'),
i(-10800,0,'ART'),
        ]

La_Rioja = La_Rioja()

