'''tzinfo timezone information for US/Indiana_minus_Starke.'''
from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as d
from pytz.tzinfo import memorized_ttinfo as i

class Indiana_minus_Starke(DstTzInfo):
    '''US/Indiana_minus_Starke timezone definition. See datetime.tzinfo for details'''

    _zone = 'US/Indiana_minus_Starke'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1918,3,31,8,0,0),
d(1918,10,27,7,0,0),
d(1919,3,30,8,0,0),
d(1919,10,26,7,0,0),
d(1942,2,9,8,0,0),
d(1945,8,14,23,0,0),
d(1945,9,30,7,0,0),
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
d(1955,10,30,7,0,0),
d(1956,4,29,8,0,0),
d(1956,10,28,7,0,0),
d(1957,4,28,8,0,0),
d(1957,9,29,7,0,0),
d(1958,4,27,8,0,0),
d(1958,9,28,7,0,0),
d(1959,4,26,8,0,0),
d(1959,10,25,7,0,0),
d(1960,4,24,8,0,0),
d(1960,10,30,7,0,0),
d(1961,4,30,8,0,0),
d(1961,10,29,7,0,0),
d(1962,4,29,8,0,0),
d(1963,10,27,7,0,0),
d(1967,4,30,8,0,0),
d(1967,10,29,7,0,0),
d(1968,4,28,8,0,0),
d(1968,10,27,7,0,0),
d(1969,4,27,8,0,0),
d(1969,10,26,7,0,0),
d(1970,4,26,8,0,0),
d(1970,10,25,7,0,0),
d(1971,4,25,8,0,0),
d(1971,10,31,7,0,0),
d(1972,4,30,8,0,0),
d(1972,10,29,7,0,0),
d(1973,4,29,8,0,0),
d(1973,10,28,7,0,0),
d(1974,1,6,8,0,0),
d(1974,10,27,7,0,0),
d(1975,2,23,8,0,0),
d(1975,10,26,7,0,0),
d(1976,4,25,8,0,0),
d(1976,10,31,7,0,0),
d(1977,4,24,8,0,0),
d(1977,10,30,7,0,0),
d(1978,4,30,8,0,0),
d(1978,10,29,7,0,0),
d(1979,4,29,8,0,0),
d(1979,10,28,7,0,0),
d(1980,4,27,8,0,0),
d(1980,10,26,7,0,0),
d(1981,4,26,8,0,0),
d(1981,10,25,7,0,0),
d(1982,4,25,8,0,0),
d(1982,10,31,7,0,0),
d(1983,4,24,8,0,0),
d(1983,10,30,7,0,0),
d(1984,4,29,8,0,0),
d(1984,10,28,7,0,0),
d(1985,4,28,8,0,0),
d(1985,10,27,7,0,0),
d(1986,4,27,8,0,0),
d(1986,10,26,7,0,0),
d(1987,4,5,8,0,0),
d(1987,10,25,7,0,0),
d(1988,4,3,8,0,0),
d(1988,10,30,7,0,0),
d(1989,4,2,8,0,0),
d(1989,10,29,7,0,0),
d(1990,4,1,8,0,0),
d(1990,10,28,7,0,0),
d(1991,4,7,8,0,0),
d(1991,10,27,7,0,0),
        ]

    _transition_info = [
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
i(-18000,0,'EST'),
        ]

Indiana_minus_Starke = Indiana_minus_Starke()

