'''tzinfo timezone information for Canada/Pacific.'''
from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as d
from pytz.tzinfo import memorized_ttinfo as i

class Pacific(DstTzInfo):
    '''Canada/Pacific timezone definition. See datetime.tzinfo for details'''

    _zone = 'Canada/Pacific'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1918,4,14,10,0,0),
d(1918,10,31,9,0,0),
d(1942,2,9,10,0,0),
d(1945,8,14,23,0,0),
d(1945,9,30,9,0,0),
d(1946,4,28,10,0,0),
d(1946,10,13,9,0,0),
d(1947,4,27,10,0,0),
d(1947,9,28,9,0,0),
d(1948,4,25,10,0,0),
d(1948,9,26,9,0,0),
d(1949,4,24,10,0,0),
d(1949,9,25,9,0,0),
d(1950,4,30,10,0,0),
d(1950,9,24,9,0,0),
d(1951,4,29,10,0,0),
d(1951,9,30,9,0,0),
d(1952,4,27,10,0,0),
d(1952,9,28,9,0,0),
d(1953,4,26,10,0,0),
d(1953,9,27,9,0,0),
d(1954,4,25,10,0,0),
d(1954,9,26,9,0,0),
d(1955,4,24,10,0,0),
d(1955,9,25,9,0,0),
d(1956,4,29,10,0,0),
d(1956,9,30,9,0,0),
d(1957,4,28,10,0,0),
d(1957,9,29,9,0,0),
d(1958,4,27,10,0,0),
d(1958,9,28,9,0,0),
d(1959,4,26,10,0,0),
d(1959,9,27,9,0,0),
d(1960,4,24,10,0,0),
d(1960,9,25,9,0,0),
d(1961,4,30,10,0,0),
d(1961,9,24,9,0,0),
d(1962,4,29,10,0,0),
d(1962,10,28,9,0,0),
d(1963,4,28,10,0,0),
d(1963,10,27,9,0,0),
d(1964,4,26,10,0,0),
d(1964,10,25,9,0,0),
d(1965,4,25,10,0,0),
d(1965,10,31,9,0,0),
d(1966,4,24,10,0,0),
d(1966,10,30,9,0,0),
d(1967,4,30,10,0,0),
d(1967,10,29,9,0,0),
d(1968,4,28,10,0,0),
d(1968,10,27,9,0,0),
d(1969,4,27,10,0,0),
d(1969,10,26,9,0,0),
d(1970,4,26,10,0,0),
d(1970,10,25,9,0,0),
d(1971,4,25,10,0,0),
d(1971,10,31,9,0,0),
d(1972,4,30,10,0,0),
d(1972,10,29,9,0,0),
d(1973,4,29,10,0,0),
d(1973,10,28,9,0,0),
d(1974,4,28,10,0,0),
d(1974,10,27,9,0,0),
d(1975,4,27,10,0,0),
d(1975,10,26,9,0,0),
d(1976,4,25,10,0,0),
d(1976,10,31,9,0,0),
d(1977,4,24,10,0,0),
d(1977,10,30,9,0,0),
d(1978,4,30,10,0,0),
d(1978,10,29,9,0,0),
d(1979,4,29,10,0,0),
d(1979,10,28,9,0,0),
d(1980,4,27,10,0,0),
d(1980,10,26,9,0,0),
d(1981,4,26,10,0,0),
d(1981,10,25,9,0,0),
d(1982,4,25,10,0,0),
d(1982,10,31,9,0,0),
d(1983,4,24,10,0,0),
d(1983,10,30,9,0,0),
d(1984,4,29,10,0,0),
d(1984,10,28,9,0,0),
d(1985,4,28,10,0,0),
d(1985,10,27,9,0,0),
d(1986,4,27,10,0,0),
d(1986,10,26,9,0,0),
d(1987,4,5,10,0,0),
d(1987,10,25,9,0,0),
d(1988,4,3,10,0,0),
d(1988,10,30,9,0,0),
d(1989,4,2,10,0,0),
d(1989,10,29,9,0,0),
d(1990,4,1,10,0,0),
d(1990,10,28,9,0,0),
d(1991,4,7,10,0,0),
d(1991,10,27,9,0,0),
d(1992,4,5,10,0,0),
d(1992,10,25,9,0,0),
d(1993,4,4,10,0,0),
d(1993,10,31,9,0,0),
d(1994,4,3,10,0,0),
d(1994,10,30,9,0,0),
d(1995,4,2,10,0,0),
d(1995,10,29,9,0,0),
d(1996,4,7,10,0,0),
d(1996,10,27,9,0,0),
d(1997,4,6,10,0,0),
d(1997,10,26,9,0,0),
d(1998,4,5,10,0,0),
d(1998,10,25,9,0,0),
d(1999,4,4,10,0,0),
d(1999,10,31,9,0,0),
d(2000,4,2,10,0,0),
d(2000,10,29,9,0,0),
d(2001,4,1,10,0,0),
d(2001,10,28,9,0,0),
d(2002,4,7,10,0,0),
d(2002,10,27,9,0,0),
d(2003,4,6,10,0,0),
d(2003,10,26,9,0,0),
d(2004,4,4,10,0,0),
d(2004,10,31,9,0,0),
d(2005,4,3,10,0,0),
d(2005,10,30,9,0,0),
d(2006,4,2,10,0,0),
d(2006,10,29,9,0,0),
d(2007,4,1,10,0,0),
d(2007,10,28,9,0,0),
d(2008,4,6,10,0,0),
d(2008,10,26,9,0,0),
d(2009,4,5,10,0,0),
d(2009,10,25,9,0,0),
d(2010,4,4,10,0,0),
d(2010,10,31,9,0,0),
d(2011,4,3,10,0,0),
d(2011,10,30,9,0,0),
d(2012,4,1,10,0,0),
d(2012,10,28,9,0,0),
d(2013,4,7,10,0,0),
d(2013,10,27,9,0,0),
d(2014,4,6,10,0,0),
d(2014,10,26,9,0,0),
d(2015,4,5,10,0,0),
d(2015,10,25,9,0,0),
d(2016,4,3,10,0,0),
d(2016,10,30,9,0,0),
d(2017,4,2,10,0,0),
d(2017,10,29,9,0,0),
d(2018,4,1,10,0,0),
d(2018,10,28,9,0,0),
d(2019,4,7,10,0,0),
d(2019,10,27,9,0,0),
d(2020,4,5,10,0,0),
d(2020,10,25,9,0,0),
d(2021,4,4,10,0,0),
d(2021,10,31,9,0,0),
d(2022,4,3,10,0,0),
d(2022,10,30,9,0,0),
d(2023,4,2,10,0,0),
d(2023,10,29,9,0,0),
d(2024,4,7,10,0,0),
d(2024,10,27,9,0,0),
d(2025,4,6,10,0,0),
d(2025,10,26,9,0,0),
d(2026,4,5,10,0,0),
d(2026,10,25,9,0,0),
d(2027,4,4,10,0,0),
d(2027,10,31,9,0,0),
d(2028,4,2,10,0,0),
d(2028,10,29,9,0,0),
d(2029,4,1,10,0,0),
d(2029,10,28,9,0,0),
d(2030,4,7,10,0,0),
d(2030,10,27,9,0,0),
d(2031,4,6,10,0,0),
d(2031,10,26,9,0,0),
d(2032,4,4,10,0,0),
d(2032,10,31,9,0,0),
d(2033,4,3,10,0,0),
d(2033,10,30,9,0,0),
d(2034,4,2,10,0,0),
d(2034,10,29,9,0,0),
d(2035,4,1,10,0,0),
d(2035,10,28,9,0,0),
d(2036,4,6,10,0,0),
d(2036,10,26,9,0,0),
d(2037,4,5,10,0,0),
d(2037,10,25,9,0,0),
        ]

    _transition_info = [
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PWT'),
i(-25200,3600,'PPT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
i(-25200,3600,'PDT'),
i(-28800,0,'PST'),
        ]

Pacific = Pacific()

