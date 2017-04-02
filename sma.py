import pandas_datareader.data as pdr
import pandas as pd
#import plotly.figure_factory as FF
#import plotly.plotly as py
#import matplotlib.pyplot as plt
from pyalgotrade import strategy
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.technical import ma
from pyalgotrade.technical import rsi

c31 = pdr.DataReader('C31.SI', 'yahoo','2000-01-01', '2017-03-01')
c31.ix['2010-01-18','High'],c31.ix['2010-01-18','Low'] = c31.ix['2010-01-18','Low'],c31.ix['2010-01-18','High']

path = '/Users/Cathy 1/Desktop/FE_project/C31.csv'
# for some interactive plots
# fig = FF.create_ohlc(c31.Open, c31.High, c31.Low, c31.Close, dates=c31.index)
# py.iplot(fig, filename='C31.SI')

class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, smaPeriod):
        super(MyStrategy, self).__init__(feed,1000)
        self.__position = None
        self.setUseAdjustedValues(True)
        #self.__rsi = rsi.RSI(feed[instrument].getCloseDataSeries(), 14)
        self.__sma = ma.SMA(feed[instrument].getCloseDataSeries(), 15)
        self.__instrument = instrument

    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        self.info('Buy at $%.2f'%(execInfo.getPrice()))
        
    def onEntryCanceld(self, position):
        self.__position = None

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        self.info('sell at $%.2f'%(execInfo.getPrice()))
        self.__position = None
    
    def onExitCanceled(self, position):
        # if the exit was canceled, resubmit it
        self.__position.exitMarket()
        
    def onBars(self, bars):
        if self.__sma[-1] is None:
            return
        bar = bars[self.__instrument]
        if self.__position is None:
            if bar.getPrice() > self.__sma[-1]:
                self.__position = self.enterLong(self.__instrument, 10, True)
        #self.info('%s %s %s'%(bar.getClose(), self.__rsi[-1], self.__sma[-1]))
        elif bar.getPrice() < self.__sma[-1] and not self.__position.exitActive():
            self.__position.exitMarket()
    
def run_strategy(smaPeriod):
    # Load the yahoo feed from the CSV file
    feed = yahoofeed.Feed()
    feed.addBarsFromCSV("Close", path)

    # Evaluate the strategy with the feed.
    myStrategy = MyStrategy(feed, "Close", smaPeriod)
    myStrategy.run()
    print "Final portfolio value: $%.2f" % myStrategy.getBroker().getEquity()

for i in range(10,30):
    run_strategy(i)
