'''tzinfo timezone information for Asia/Hovd.'''
from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as d
from pytz.tzinfo import memorized_ttinfo as i

class Hovd(DstTzInfo):
    '''Asia/Hovd timezone definition. See datetime.tzinfo for details'''

    zone = 'Asia/Hovd'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1905,7,31,17,53,24),
d(1977,12,31,18,0,0),
d(1983,3,31,17,0,0),
d(1983,9,30,16,0,0),
d(1984,3,31,17,0,0),
d(1984,9,29,16,0,0),
d(1985,3,30,17,0,0),
d(1985,9,28,16,0,0),
d(1986,3,29,17,0,0),
d(1986,9,27,16,0,0),
d(1987,3,28,17,0,0),
d(1987,9,26,16,0,0),
d(1988,3,26,17,0,0),
d(1988,9,24,16,0,0),
d(1989,3,25,17,0,0),
d(1989,9,23,16,0,0),
d(1990,3,24,17,0,0),
d(1990,9,29,16,0,0),
d(1991,3,30,17,0,0),
d(1991,9,28,16,0,0),
d(1992,3,28,17,0,0),
d(1992,9,26,16,0,0),
d(1993,3,27,17,0,0),
d(1993,9,25,16,0,0),
d(1994,3,26,17,0,0),
d(1994,9,24,16,0,0),
d(1995,3,25,17,0,0),
d(1995,9,23,16,0,0),
d(1996,3,30,17,0,0),
d(1996,9,28,16,0,0),
d(1997,3,29,17,0,0),
d(1997,9,27,16,0,0),
d(1998,3,28,17,0,0),
d(1998,9,26,16,0,0),
d(2001,4,27,19,0,0),
d(2001,9,28,18,0,0),
d(2002,3,29,19,0,0),
d(2002,9,27,18,0,0),
d(2003,3,28,19,0,0),
d(2003,9,26,18,0,0),
d(2004,3,26,19,0,0),
d(2004,9,24,18,0,0),
d(2005,3,25,19,0,0),
d(2005,9,23,18,0,0),
d(2006,3,24,19,0,0),
d(2006,9,29,18,0,0),
d(2007,3,30,19,0,0),
d(2007,9,28,18,0,0),
d(2008,3,28,19,0,0),
d(2008,9,26,18,0,0),
d(2009,3,27,19,0,0),
d(2009,9,25,18,0,0),
d(2010,3,26,19,0,0),
d(2010,9,24,18,0,0),
d(2011,3,25,19,0,0),
d(2011,9,23,18,0,0),
d(2012,3,30,19,0,0),
d(2012,9,28,18,0,0),
d(2013,3,29,19,0,0),
d(2013,9,27,18,0,0),
d(2014,3,28,19,0,0),
d(2014,9,26,18,0,0),
d(2015,3,27,19,0,0),
d(2015,9,25,18,0,0),
d(2016,3,25,19,0,0),
d(2016,9,23,18,0,0),
d(2017,3,24,19,0,0),
d(2017,9,29,18,0,0),
d(2018,3,30,19,0,0),
d(2018,9,28,18,0,0),
d(2019,3,29,19,0,0),
d(2019,9,27,18,0,0),
d(2020,3,27,19,0,0),
d(2020,9,25,18,0,0),
d(2021,3,26,19,0,0),
d(2021,9,24,18,0,0),
d(2022,3,25,19,0,0),
d(2022,9,23,18,0,0),
d(2023,3,24,19,0,0),
d(2023,9,29,18,0,0),
d(2024,3,29,19,0,0),
d(2024,9,27,18,0,0),
d(2025,3,28,19,0,0),
d(2025,9,26,18,0,0),
d(2026,3,27,19,0,0),
d(2026,9,25,18,0,0),
d(2027,3,26,19,0,0),
d(2027,9,24,18,0,0),
d(2028,3,24,19,0,0),
d(2028,9,29,18,0,0),
d(2029,3,30,19,0,0),
d(2029,9,28,18,0,0),
d(2030,3,29,19,0,0),
d(2030,9,27,18,0,0),
d(2031,3,28,19,0,0),
d(2031,9,26,18,0,0),
d(2032,3,26,19,0,0),
d(2032,9,24,18,0,0),
d(2033,3,25,19,0,0),
d(2033,9,23,18,0,0),
d(2034,3,24,19,0,0),
d(2034,9,29,18,0,0),
d(2035,3,30,19,0,0),
d(2035,9,28,18,0,0),
d(2036,3,28,19,0,0),
d(2036,9,26,18,0,0),
d(2037,3,27,19,0,0),
d(2037,9,25,18,0,0),
        ]

    _transition_info = [
i(22020,0,'LMT'),
i(21600,0,'HOVT'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
i(28800,3600,'HOVST'),
i(25200,0,'HOVT'),
        ]

Hovd = Hovd()

