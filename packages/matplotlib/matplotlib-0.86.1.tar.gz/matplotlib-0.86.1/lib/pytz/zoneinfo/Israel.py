'''tzinfo timezone information for Israel.'''
from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as d
from pytz.tzinfo import memorized_ttinfo as i

class Israel(DstTzInfo):
    '''Israel timezone definition. See datetime.tzinfo for details'''

    _zone = 'Israel'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1917,12,31,21,39,20),
d(1940,5,31,22,0,0),
d(1942,10,31,21,0,0),
d(1943,4,1,0,0,0),
d(1943,10,31,21,0,0),
d(1944,3,31,22,0,0),
d(1944,10,31,21,0,0),
d(1945,4,15,22,0,0),
d(1945,10,31,23,0,0),
d(1946,4,16,0,0,0),
d(1946,10,31,21,0,0),
d(1948,5,22,22,0,0),
d(1948,8,31,20,0,0),
d(1948,10,31,23,0,0),
d(1949,4,30,22,0,0),
d(1949,10,31,23,0,0),
d(1950,4,15,22,0,0),
d(1950,9,15,0,0,0),
d(1951,3,31,22,0,0),
d(1951,11,11,0,0,0),
d(1952,4,20,0,0,0),
d(1952,10,19,0,0,0),
d(1953,4,12,0,0,0),
d(1953,9,13,0,0,0),
d(1954,6,12,22,0,0),
d(1954,9,11,21,0,0),
d(1955,6,11,0,0,0),
d(1955,9,10,21,0,0),
d(1956,6,2,22,0,0),
d(1956,9,30,0,0,0),
d(1957,4,29,0,0,0),
d(1957,9,21,21,0,0),
d(1974,7,6,22,0,0),
d(1974,10,12,21,0,0),
d(1975,4,19,22,0,0),
d(1975,8,30,21,0,0),
d(1985,4,13,22,0,0),
d(1985,9,14,21,0,0),
d(1986,5,17,22,0,0),
d(1986,9,6,21,0,0),
d(1987,4,14,22,0,0),
d(1987,9,12,21,0,0),
d(1988,4,8,22,0,0),
d(1988,9,2,21,0,0),
d(1989,4,29,22,0,0),
d(1989,9,2,21,0,0),
d(1990,3,24,22,0,0),
d(1990,8,25,21,0,0),
d(1991,3,23,22,0,0),
d(1991,8,31,21,0,0),
d(1992,3,28,22,0,0),
d(1992,9,5,21,0,0),
d(1993,4,1,22,0,0),
d(1993,9,4,21,0,0),
d(1994,3,31,22,0,0),
d(1994,8,27,21,0,0),
d(1995,3,30,22,0,0),
d(1995,9,2,21,0,0),
d(1996,3,14,22,0,0),
d(1996,9,15,21,0,0),
d(1997,3,20,22,0,0),
d(1997,9,13,21,0,0),
d(1998,3,19,22,0,0),
d(1998,9,5,21,0,0),
d(1999,4,2,0,0,0),
d(1999,9,2,23,0,0),
d(2000,4,14,0,0,0),
d(2000,10,5,22,0,0),
d(2001,4,8,23,0,0),
d(2001,9,23,22,0,0),
d(2002,3,28,23,0,0),
d(2002,10,6,22,0,0),
d(2003,3,27,23,0,0),
d(2003,10,2,22,0,0),
d(2004,4,6,23,0,0),
d(2004,9,21,22,0,0),
d(2005,3,31,23,0,0),
d(2005,9,30,22,0,0),
d(2006,3,31,23,0,0),
d(2006,9,30,22,0,0),
d(2007,3,31,23,0,0),
d(2007,9,30,22,0,0),
d(2008,3,31,23,0,0),
d(2008,9,30,22,0,0),
d(2009,3,31,23,0,0),
d(2009,9,30,22,0,0),
d(2010,3,31,23,0,0),
d(2010,9,30,22,0,0),
d(2011,3,31,23,0,0),
d(2011,9,30,22,0,0),
d(2012,3,31,23,0,0),
d(2012,9,30,22,0,0),
d(2013,3,31,23,0,0),
d(2013,9,30,22,0,0),
d(2014,3,31,23,0,0),
d(2014,9,30,22,0,0),
d(2015,3,31,23,0,0),
d(2015,9,30,22,0,0),
d(2016,3,31,23,0,0),
d(2016,9,30,22,0,0),
d(2017,3,31,23,0,0),
d(2017,9,30,22,0,0),
d(2018,3,31,23,0,0),
d(2018,9,30,22,0,0),
d(2019,3,31,23,0,0),
d(2019,9,30,22,0,0),
d(2020,3,31,23,0,0),
d(2020,9,30,22,0,0),
d(2021,3,31,23,0,0),
d(2021,9,30,22,0,0),
d(2022,3,31,23,0,0),
d(2022,9,30,22,0,0),
d(2023,3,31,23,0,0),
d(2023,9,30,22,0,0),
d(2024,3,31,23,0,0),
d(2024,9,30,22,0,0),
d(2025,3,31,23,0,0),
d(2025,9,30,22,0,0),
d(2026,3,31,23,0,0),
d(2026,9,30,22,0,0),
d(2027,3,31,23,0,0),
d(2027,9,30,22,0,0),
d(2028,3,31,23,0,0),
d(2028,9,30,22,0,0),
d(2029,3,31,23,0,0),
d(2029,9,30,22,0,0),
d(2030,3,31,23,0,0),
d(2030,9,30,22,0,0),
d(2031,3,31,23,0,0),
d(2031,9,30,22,0,0),
d(2032,3,31,23,0,0),
d(2032,9,30,22,0,0),
d(2033,3,31,23,0,0),
d(2033,9,30,22,0,0),
d(2034,3,31,23,0,0),
d(2034,9,30,22,0,0),
d(2035,3,31,23,0,0),
d(2035,9,30,22,0,0),
d(2036,3,31,23,0,0),
d(2036,9,30,22,0,0),
d(2037,3,31,23,0,0),
d(2037,9,30,22,0,0),
        ]

    _transition_info = [
i(8460,0,'JMT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(14400,7200,'IDDT'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
i(10800,3600,'IDT'),
i(7200,0,'IST'),
        ]

Israel = Israel()

