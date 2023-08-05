#!/usr/bin/env python
# Some functions to load a return data for the plot demos

from matplotlib.numerix import fromstring, argsort, take, array, resize
def get_two_stock_data():
    """
    load stock time and price data for two stocks The return values
    (d1,p1,d2,p2) are the trade time (in days) and prices for stocks 1
    and 2 (intc and aapl)
    """
    ticker1, ticker2 = 'INTC', 'AAPL'
    M1 = fromstring( file('data/%s.dat' % ticker1, 'rb').read(), 'd')

    M1 = resize(M1, (M1.shape[0]/2,2) )

    M2 = fromstring( file('data/%s.dat' % ticker2, 'rb').read(), 'd')
    M2 = resize(M1, (M2.shape[0]/2,2) )

    d1, p1 = M1[:,0], M1[:,1]
    d2, p2 = M2[:,0], M2[:,1]
    return (d1,p1,d2,p2)


def get_daily_data():
    """
    return stock1 and stock2 instances, each of which have attributes

      open, high, low, close, volume

    as numeric arrays
    
    """
    class C: pass

    def get_ticker(ticker):
        vals = []
        lines = file( 'data/%s.csv' % ticker ).readlines()
        for line in lines[1:]:
            vals.append([float(val) for val in line.split(',')[1:]])
            
        M = array(vals)
        c = C()
        c.open = M[:,0]
        c.high = M[:,1]
        c.low = M[:,2]
        c.close = M[:,3]
        c.volume = M[:,4]
        return c
    c1 = get_ticker('intc')
    c2 = get_ticker('msft')
    return c1, c2
