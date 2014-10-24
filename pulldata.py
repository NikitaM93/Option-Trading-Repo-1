import urllib2
import datetime
import math
import numpy as np
import matplotlib.pyplot as plt
try:
    # py3
    from urllib.request import Request, urlopen
    from urllib.parse import urlencode
except ImportError:
    # py2
    from urllib2 import Request, urlopen
    from urllib import urlencode

logreturns = []
variancecalcs = [] 
annualvolprime = float()
annualvolprime1 = []
pi = 3.14159265358979 

daysToMaturityPrime = float()
rate = .004
q = float()
spot = float()
#strike = float()
#realOptionPrice = float()

impliedvols = []
months = []

adjclose = [] 
date = []
opent = []
high = []
low = []
close = []
volume = []

g_price = []
g_bid = []
g_ask = []
g_mid = []
g_open_int = []
g_strike = []

urlToVisit = "http://ichart.finance.yahoo.com/table.csv?s="
start = datetime.date(2014, 1, 1)
end = datetime.date.today()

def readFile():
    f = open('file.txt', 'r')
    lines = f.readlines()
    f.close()
    
    for l in lines:
        s = l.split()
        g_price.append(float(s[0]))
        g_bid.append(float(s[2]))
        g_ask.append(float(s[3]))
        g_open_int.append(float(s[5]))
        g_strike.append(float(s[6]))
        
    i = 0
    while i < len(g_bid):
        mid = (g_ask[i] + g_bid[i]) / 2
        g_mid.append(mid)
        i += 1
    
    #for i in g_strike:
    #    print 'strike', i
    #for i in g_mid:
    #    print 'mid', i
        
def makeUrl(stock, start, end):
    a = start
    b = end
    dateUrl = '%s&a=%d&b=%d&c=%d&d=%d&e=%d&f=%d&g=d&ignore=.csv'% (stock, a.month-1, a.day, a.year, b.month-1, b.day, b.year)
    return urlToVisit+dateUrl

def pullData(stock):
    get_quote(stock)
    readFile()
    try: 
        print "Currently pulling", stock
        stockUrl = makeUrl(stock, start, end)
        stockFile = []
        try:
            sourceCode = urllib2.urlopen(stockUrl).read()
            splitSource = sourceCode.split('\n')
            
            for eachLine in splitSource:
                splitLine = eachLine.split(',')
                if len(splitLine) == 7:
                    if 'values' not in eachLine:
                        stockFile.append(eachLine)
        except Exception, e:
            print str(e), 'failed to organize pulled data'
    except Exception, e:
        print str(e), 'failed to pull stock historical data'
        
    try:
        for line in stockFile:
            s = line.split(',')

            if s[0] == 'Date' or s[1] == 'Open' or s[2] == 'High' or s[3] == 'Low' or s[4] == 'Close' or s[5] == 'Volume' or s[6] == 'Adj Close':
                pass
            else:
                date_obj = datetime.datetime.strptime(s[0], '%Y-%m-%d').date()
                date.append(date_obj)
                opent.append(s[1])
                high.append(s[2])
                low.append(s[3])
                close.append(s[4])
                low.append(s[5])
                adjclose.append(s[6])
    except Exception, e:
        print str(e), 'error'

    
    impliedVolWithStikes(adjclose, g_strike)
        
        
def _request(symbol, stat):
    url = 'http://finance.yahoo.com/d/quotes.csv?s=%s&f=%s' % (symbol, stat)
    req = Request(url)
    resp = urlopen(req)
    content = resp.read().decode().strip()
    return content
    
def get_quote(symbol):
    ids = 'yl1'
    values = _request(symbol, ids).split(',')
    global q
    global spot
    q = float(values[0])
    spot = float(values[1])
    
def impliedVolWithStikes(adjclose, strikes):
    logreturn(adjclose)
    variancecalc(logreturns)
    annualvol(stdev(varianceaverage(variancecalcs)))
    print "Spot:                                    ", spot
    print "Historical annual volalitility for Call: ", annualvolprime
    i = 0
    while i < len(strikes):
        
        option = OptionPrice(spot, strikes[i], daysToMaturityPrime, annualvolprime, rate, q, "c")
        print "Price of Call: $", option
        
        impliedvol = annualvolimplied(option, g_mid[i], strikes[i])
    
        #print "Average of adjclose:                     ", average
        print "Strike:                                  ", strikes[i]
        print "Historical annual volalitility for Call: ", annualvolprime
        print "Implied annual volalitity for Call:      ", impliedvol
        print ""
        i += 1
    
    #greeks(spot, strike, daysToMaturityPrime, annualvolprime, rate, q, "c")
    
            
def timeToMaturity(year, month, day):
    maturityDate = datetime.date(year, month, day)
    difference = maturityDate - end
    global daysToMaturityPrime
    daysToMaturityPrime = (difference.total_seconds() / (3600 * 24))
    return daysToMaturityPrime
        
def OptionPrice(spot, strike, NbExp, vol, rate, q, optionType):
    # v = float()
    d1 = float()
    d2 = float()
    Nd1 = float()
    Nd2 = float()
    T = float()
        
    if NbExp < 0:
        return 0
    T = NbExp / 365
    if NbExp == 0:
        if optionType == "c":
            print "TESTTESTTESTTEST", long((math.max(spot - strike, 0)))
            return float((math.max(spot - strike, 0)))
        else:
            print "TESTTESTTESTTEST", long((math.max(spot - strike, 0)))
            return float((math.max(strike - spot, 0)))
                
    d1 = ((math.log(spot / strike)) + (rate - q + (vol * vol) / 2) * T) / (vol * math.sqrt(T))
    d2 = d1 - vol * math.sqrt(T)
    Nd1 = cdnf(d1)
    Nd2 = cdnf(d2)
    if optionType == "c":
        # call option
        return float((spot * math.exp(-q * T) * Nd1 - strike * math.exp(-rate * T) * Nd2))
    else:
        # put option
        return float((-spot * math.exp(-q * T) * (1 - Nd1) + strike * math.exp(-rate * T) * (1 - Nd2)))
  
def greeks(spot, strike, NbExp, vol, rate, q, optionType):
    dS = float()
    dv = float()
    dr = float()
    dt = float()
    delta = float()
    gamma = float()
    vega = float()
    theta = float()
    rho = float()
    dS = 0.01
    # 0.01 point move in spot
    dv = 0.0001
    # 0.01% move in vol
    dt = 1
    # 1 day
    dr = 0.0001
    # 1bps move
    if NbExp < 0:
        # print "TESTTESTTESTTEST";
        return 0
    #x = float((cls.OptionPrice(spot + dS, strike, NbExp, vol, rate, q, optionType)))
    #x2 = float(cls.OptionPrice(spot - dS, strike, NbExp, vol, rate, q, optionType))
    # print x;
    # print x2;
    # print dS;
    # print (x-x2)/(2*dS);
    delta = float(((OptionPrice(spot + dS, strike, NbExp, vol, rate, q, optionType) - OptionPrice(spot - dS, strike, NbExp, vol, rate, q, optionType)) / (2 * dS)))
    gamma = float(((OptionPrice(spot + dS, strike, NbExp, vol, rate, q, optionType) - 2 * OptionPrice(spot, strike, NbExp, vol, rate, q, optionType) + OptionPrice(spot - dS, strike, NbExp, vol, rate, q, optionType)) / (dS * dS)))
    vega = float(((OptionPrice(spot, strike, NbExp, vol + dv, rate, q, optionType) - OptionPrice(spot, strike, NbExp, vol - dv, rate, q, optionType)) / (2 * dv) / 100))
    rho = float(((OptionPrice(spot, strike, NbExp, vol, rate + dr, q, optionType) - OptionPrice(spot, strike, NbExp, vol, rate - dr, q, optionType)) / (2 * dr) / 1000))
    if NbExp == 0:
        # print "TESTTESTTESTTEST";
        theta = 0
    else:
        theta = float(((OptionPrice(spot, strike, NbExp - dt, vol, rate, q, optionType) - OptionPrice(spot, strike, NbExp + dt, vol, rate, q, optionType)) / (2 * dt)))
    print "delta: ", delta
    print "gamma: ", gamma
    print "vega:  ", vega
    print "rho>:  ", rho
    print "theta: ", theta
    return 0
                 
def cdnf(x):
    neg = 1 if (x < 0) else 0
    if neg == 1:
        x *= -1
    k = (1 / (1 + 0.2316419 * x))
    y = ((((1.330274429 * k - 1.821255978) * k + 1.781477937) * k - 0.356563782) * k + 0.319381530) * k
    y = 1.0 - 0.398942280401 * math.exp(-0.5 * x * x) * y
    return (1 - neg) * y + neg * (1 - y)
        
def logreturn(adjclose):
    i = 0
    while i < len(adjclose) - 1:
        x = math.log(float(adjclose[i])/float(adjclose[i+1]))
        global logreturns
        logreturns.append(x)
        i += 1
        
def averagelog(logreturns):
    sum = 0
    counter = 0
    i = 0
    while i < len(logreturns) - 1:
        y = logreturns[i]
        sum += y
        counter += 1
        i += 1
    x = sum / counter
    return x
    
def variancecalc(logreturns):
    i = 0
    avg = averagelog(logreturns)
    while i < len(logreturns) - 1:
        y = logreturns[i]
        yprime = y - avg
        global variancecalcs
        variancecalcs.append(math.pow(yprime, 2))
        i += 1

def varianceaverage(variancecalc):
    sum = 0
    counter = 0
    i = 0
    while i < len(variancecalc) - 1:
        y = variancecalc[i]
        sum += y
        counter += 1
        i += 1
    #counter should be n-1 to get an unbiased estimate
    x = sum / (len(variancecalc) - 1)
    #print "**********************************"
    #print "VarAvrg:", x
    return x


def stdev(varianceAvrg):
    return math.sqrt(varianceAvrg)


def annualvol(stdev):
    annualvol = math.sqrt(252) * stdev
    global annualvolprime 
    annualvolprime = annualvol
    #this should add historial vols by month in sequence
    annualvolprime1.append(annualvol)
    return annualvol
    
def annualvol2(stdev):
    return math.sqrt(daysToMaturityPrime) * stdev
    
def annualvolimplied(modelOption, realOption, strike):
        volimplied = stdev(varianceaverage(variancecalcs))
        annualvolimplied = 0
        real = realOption
        model = modelOption
        if real == model:
            annualvolimplied = annualvol2(volimplied)
        elif real > model:
            while (real > model):
                volimplied += 0.00001
                model = OptionPrice(spot, strike, daysToMaturityPrime, annualvol2(volimplied), rate, q, "c")
                annualvolimplied = annualvol2(volimplied)
                #print 'real > model', annualvolimplied
                if annualvolimplied < 0:
                    print 'ERROR: OUT OF THE MONEY'
                    break
        else:
            while (real < model):
                volimplied -= 0.00001
                model = OptionPrice(spot, strike, daysToMaturityPrime, annualvol2(volimplied), rate, q, "c")
                annualvolimplied = annualvol2(volimplied)
                #print 'real < model', annualvolimplied
                if annualvolimplied < 0:
                    print 'ERROR: OUT OF THE MONEY'
                    break
        
        # this should add implied vols by month in sequence        
        impliedvols.append(annualvolimplied)
        return annualvolimplied
        
while True:
    stock = raw_input('Stock to pull: ')
    # spot = float(raw_input('Spot: '))
    #strike = float(raw_input('Strike: '))
    #realOptionPrice = float(raw_input('Real Option Price: '))
    daysToMaturityPrime = float(raw_input('Days to Maturity: '))
    #rate = float(raw_input('Risk-free Rate: '))
    # q = float(raw_input('Div/yield: '))
    
    pullData(stock)