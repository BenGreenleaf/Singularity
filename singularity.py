import ccxt



master_data = {
    'coinbasepro': {'BTC/USDT': [4.5,4], 'ETH/USDT': [2,1.5]},
    'binance': {'BTC/USDT':[5.5,5], 'ETH/USDT': [2.5,2]}
}
#First num buy, second num sell



#def updateData(exchange, pair, data):
    

#def profitableCheck(percen, exch1, curr1, curr2, exch2, curr3):


def withdepFee(inp, exch, curr, depoOwith):
    d = exch.fetch_transaction_fee(curr)
    withFee = d['withdraw'][0]
    depFee = d['deposit'][0]

    if depoOwith == 'deposit':
        return(inp-depFee)
    elif depoOwith == 'withdraw':
        return(inp-withFee)
    else:
        print("ERROR")

def transactionFee(inp, exch, symbol, side, price):
    exch.load_markets()
    cost = exch.calculate_fee(symbol=symbol, type='limit', side=side, price=price, takerOrMaker='maker', amount=inp)['cost']
    return(inp-cost)

def toFiat(symbol, hOl):
    # hOl = High or Low | High when selling | Low when buying
    exchanges = list(master_data.values())
    exchNum = 0

    valids = []
    temp = 0

    for exchInfo in exchanges:
        exchange = list(master_data)[exchNum]
        exchNum += 1

        pairNum = 0
        for pair in exchInfo.keys():
            f, s = pair.split("/")[0], pair.split("/")[1]
            if s == 'USD' and f == symbol:
                if hOl == 'High':
                    temp = (withdepFee(1, exchange, 'USD', 'withdraw'))
                    temp = list(exchInfo.values())[pairNum][1]*temp
                    valids.append(exchange, temp)
                elif hOl == 'Low':
                    temp = (withdepFee(1, exchange, 'USD', 'deposit'))
                    temp = list(exchInfo.values())[pairNum][0]/temp
                    valids.append(exchange, temp)

            pairNum += 1

    if len(valids)>0:
        if hOl == 'High':
            valids.sort(key=lambda x: x[1], reverse=True) #Need to check with fees here
            return(valids[0][0], valids[0][1])
        elif hOl == 'Low':
            valids.sort(key=lambda x: x[1], reverse=False) #Need to check with fees here
            return(valids[0][0], valids[0][1])
    else:
        if hOl == 'High':
            return(0.0000000000000001, 0.0000000000000001)
        elif hOl == 'Low':
            return(10000000000000000, 10000000000000000)

def arbCheck():

    exchanges = list(master_data.values())

    exchNum = 0

    tempManip = []

    for exchInfo in exchanges:
        exchange = list(master_data)[exchNum]
        exchNum += 1

        pairNum = 0
        for pair in exchInfo.keys():
            f, s = pair.split("/")[0], pair.split("/")[1]
            tags = [f,s,list(exchInfo.values())[pairNum][0],list(exchInfo.values())[pairNum][1],exchange]
            tempManip.append(tags)
            pairNum += 1

    for fDec in tempManip:
        for sDec in tempManip:
            compat = fDec[0] in sDec or fDec[1] in sDec
            if sDec != fDec and compat:
                if fDec[0] == sDec[0] and fDec[1] == sDec[1]:
                    #Same Pair | Buy for cheaper one, sell for more expensive one
                    # FIAT -> 1 -> 2 -> 2 -> 1 -> FIAT {1}
                    # FIAT -> 2 -> 1 -> 1 -> 2 -> FIAT {2}

                    #{1}
                    cexch, cprice = toFiat(fDec[0], 'Low') #BUY
                    fCryptoAm = 1/cprice #BUY
                    fCryptoAm = transactionFee(fCryptoAm, cexch, (fDec[0]+"/USD"), 'buy', cprice)

                    sCryptoAm = fCryptoAm*fDec[3] #SELL
                    sCryptoAm = transactionFee(sCryptoAm, fDec[4], (fDec[0]+"/"+fDec[1]), 'sell', fDec[3])

                    sCryptoAm = withdepFee(sCryptoAm, fDec[4], fDec[1], 'withdraw')
                    sCryptoAm = withdepFee(sCryptoAm, sDec[4], sDec[1], 'deposit')

                    tCryptoAm = sCryptoAm/sDec[2]#BUY
                    tCryptoAm = transactionFee(tCryptoAm, sDec[4], (sDec[0]+"/"+sDec[1]), 'buy', sDec[2])#BUY

                    scexch, scprice = toFiat(sDec[0], 'High') #SELL
                    fiatAm = tCryptoAm*scprice #SELL
                    fiatAm = transactionFee(fiatAm, scexch, (sDec[0]+"/USD"), 'sell', scprice)

                    profPer = ((fiatAm-1)/1)*100
                    print(profPer)


                    
                    #{2}
                    cexch, cprice = toFiat(fDec[1], 'Low') #BUY
                    fCryptoAm = 1/cprice #BUY
                    fCryptoAm = transactionFee(fCryptoAm, cexch, (fDec[1]+"/USD"), 'buy', cprice)

                    sCryptoAm = fCryptoAm/fDec[2] #BUY
                    sCryptoAm = transactionFee(sCryptoAm, fDec[4], (fDec[0]+"/"+fDec[1]), 'buy', fDec[2])

                    sCryptoAm = withdepFee(sCryptoAm, fDec[4], fDec[0], 'withdraw')
                    sCryptoAm = withdepFee(sCryptoAm, sDec[4], sDec[0], 'deposit')

                    tCryptoAm = sCryptoAm*sDec[3]#SELL
                    tCryptoAm = transactionFee(tCryptoAm, sDec[4], (sDec[0]+"/"+sDec[1]), 'sell', sDec[3])#BUY

                    scexch, scprice = toFiat(sDec[1], 'High') #SELL
                    fiatAm = tCryptoAm*scprice #SELL
                    fiatAm = transactionFee(fiatAm, scexch, (sDec[1]+"/USD"), 'sell', scprice)

                    profPer = ((fiatAm-1)/1)*100
                    print(profPer)

                elif fDec[0] == sDec[0]:
                    #I.E SOL/USDT SOL/BNC [CRYPTO -> CRYPTO -> CRYPTO]{1} |or| SOL/USD SOL/BNC [FIAT-> CRYPTO -> CRYPTO]{2} |or| SOL/BNC SOL/USD [CRYPTO -> CRYPTO -> FIAT]{3}

                    if fDec[1] == 'USD':
                        #{2}
                        fCryptoAm = (withdepFee(1, fDec[4], 'USD', 'deposit'))/fDec[2] #BUY
                        fCryptoAm = transactionFee(fCryptoAm, fDec[4], (fDec[0]+"/"+fDec[1]), 'buy', fDec[2])
                        fCryptoAm = withdepFee(fCryptoAm, fDec[4], fDec[0], 'withdraw')

                        sCryptoAm = fCryptoAm*sDec[3] #SELL
                        sCryptoAm = transactionFee(sCryptoAm, sDec[4], (sDec[0]+"/"+sDec[1]), 'sell', sDec[3])

                        cexch, cprice = toFiat(sDec[1], 'High') #SELL
                        if cexch != sDec[4]:
                            sCryptoAm = withdepFee(sCryptoAm, fDec[4], sDec[1], 'withdraw')
                            sCryptoAm = withdepFee(sCryptoAm, cexch, sDec[1], 'deposit')
                        fiatAm = sCryptoAm*cprice #SELL
                        fiatAm = transactionFee(fiatAm, cexch, (sDec[1]+"/USD"), 'sell', cprice)
                        profPer = ((fiatAm-1)/1)*100
                        print(profPer)

                    elif sDec[1] == 'USD':
                        #{3}
                        cexch, cprice = toFiat(fDec[1], 'Low') #BUY
                        fCryptoAm = 1/cprice #BUY
                        fCryptoAm = transactionFee(fCryptoAm, cexch, (fDec[1]+"/USD"), 'buy', cprice)

                        sCryptoAm = fCryptoAm/fDec[2] #BUY
                        sCryptoAm = transactionFee(sCryptoAm, fDec[4], (fDec[0]+"/"+fDec[1]), 'buy', fDec[2])

                        if fDec[4] != sDec[4]:
                            sCryptoAm = withdepFee(sCryptoAm, fDec[4], fDec[0], 'withdraw')
                            sCryptoAm = withdepFee(sCryptoAm, sDec[4], sDec[0], 'deposit')

                        fiatAm = sCryptoAm*sDec[3] #SELL
                        fiatAm = transactionFee(fiatAm, sDec[4], (sDec[0]+"/"+sDec[1]), 'buy', sDec[3])
                        fiatAm = withdepFee(fiatAm, sDec[4], 'USD', 'withdraw')

                        profPer = ((fiatAm-1)/1)*100
                        print(profPer)

                    else:
                        #{1}
                        fcexch, fcprice = toFiat(fDec[1], 'Low') #BUY
                        fCryptoAm = 1/fcprice #BUY
                        fCryptoAm = transactionFee(fCryptoAm, fcexch, (fDec[1]+"/USD"), 'buy', fcprice)

                        if fDec[4] != sDec[4]:
                            fCryptoAm = withdepFee(fCryptoAm, fDec[4], fDec[0], 'withdraw')
                            fCryptoAm = withdepFee(fCryptoAm, sDec[4], sDec[0], 'deposit')

                        sCryptoAm = fCryptoAm/fDec[2] #BUY
                        sCryptoAm = transactionFee(sCryptoAm, fDec[4], (fDec[0]+"/"+fDec[1]), 'buy', fDec[2])

                        tCryptoAm = sCryptoAm*sDec[3] #SELL
                        tCryptoAm = transactionFee(tCryptoAm, sDec[4], (sDec[0]+"/"+sDec[1]), 'sell', sDec[3])

                        scexch, scprice = toFiat(sDec[1], 'High') #SELL
                        fiatAm = tCryptoAm*scprice #SELL
                        fiatAm = transactionFee(fiatAm, scexch, (sDec[1]+"/USD"), 'sell', scprice)

                        profPer = ((fiatAm-1)/1)*100
                        print(profPer)

                elif fDec[1] == sDec[1]:
                    #I.E SOL/USD BTC/USD [DO NOT WANT THIS]{1} |or| BTC/SOL ETH/SOL [CRYPTO -> CRYPTO -> CRYPTO]{2}
                    if fDec[1] == 'USD':
                        #{1}
                        pass
                    else:
                        #{2}
                        fcexch, fcprice = toFiat(fDec[0], 'Low') #BUY
                        fCryptoAm = 1/fcprice #BUY
                        fCryptoAm = transactionFee(fCryptoAm, fcexch, (fDec[0]+"/USD"), 'buy', fcprice)

                        sCryptoAm = fCryptoAm*fDec[3] #SELL
                        sCryptoAm = transactionFee(sCryptoAm, fDec[4], (fDec[0]+"/"+fDec[1]), 'sell', fDec[3])

                        if fDec[4] != sDec[4]:
                            sCryptoAm = withdepFee(sCryptoAm, fDec[4], fDec[1], 'withdraw')
                            sCryptoAm = withdepFee(sCryptoAm, sDec[4], sDec[1], 'deposit')

                        tCryptoAm = sCryptoAm/sDec[2] #BUY
                        tCryptoAm = transactionFee(tCryptoAm, sDec[4], (sDec[0]+"/"+sDec[1]), 'buy', sDec[2])

                        scexch, scprice = toFiat(sDec[0], 'High') #SELL
                        fiatAm = tCryptoAm*scprice #SELL
                        fiatAm = transactionFee(fiatAm, scexch, (sDec[0]+"/USD"), 'sell', scprice)

                        profPer = ((fiatAm-1)/1)*100
                        print(profPer)

                elif fDec[0] == sDec[1]:
                    #I.E SOL/USD ETH/SOL [FIAT -> CRYPTO -> CRYPTO]{1}
                    #{1}
                    fCryptoAm = (withdepFee(1, fDec[4], 'USD', 'deposit'))/fDec[2] #BUY
                    fCryptoAm = transactionFee(fCryptoAm, fDec[4], (sDec[0]+"/USD"), 'buy', fDec[2])

                    if fDec[4] != sDec[4]:
                        fCryptoAm = withdepFee(fCryptoAm, fDec[4], fDec[0], 'withdraw')
                        fCryptoAm = withdepFee(fCryptoAm, sDec[4], sDec[1], 'deposit')

                    sCryptoAm = fCryptoAm/sDec[2] #BUY
                    sCryptoAm = transactionFee(sCryptoAm, sDec[4], (sDec[0]+"/"+sDec[1]), 'buy', sDec[2])

                    cexch, cprice = toFiat(sDec[0], 'High') #SELL
                    fiatAm = sCryptoAm*cprice #SELL
                    fiatAm = transactionFee(fiatAm, cexch, (sDec[0]+"/USD"), 'sell', cprice)

                    profPer = ((fiatAm-1)/1)*100
                    print(profPer)

                elif fDec[1] == sDec[0]:
                    #I.E SOL/ETH ETH/BTC [CRYPTO -> CRYPTO -> CRYPTO]{1}
                    #{1}
                    fcexch, fcprice = toFiat(fDec[0], 'Low') #BUY
                    fCryptoAm = (withdepFee(1, fDec[4], 'USD', 'deposit'))/fcprice #BUY
                    fCryptoAm = transactionFee(fCryptoAm, fcexch, (fDec[0]+"/USD"), 'buy', fcprice)

                    sCryptoAm = fCryptoAm*fDec[3] #SELL
                    sCryptoAm = transactionFee(sCryptoAm, fDec[4], (fDec[0]+"/"+fDec[1]), 'buy', fDec[3])

                    if fDec[4] != sDec[4]:
                        sCryptoAm = withdepFee(sCryptoAm, fDec[4],fDec[1], 'withdraw')
                        sCryptoAm = withdepFee(sCryptoAm, sDec[4],sDec[0], 'deposit')

                    tCryptoAm = sCryptoAm*sDec[3] #SELL
                    tCryptoAm = transactionFee(tCryptoAm, sDec[4], (sDec[0]+"/"+sDec[1]), 'sell', sDec[3])
                    
                    scexch, scprice = toFiat(sDec[1], 'High') #SELL
                    fiatAm = tCryptoAm*scprice #SELL
                    fiatAm = transactionFee(fiatAm, scexch, (sDec[1]+"/USD"), 'sell', scprice)

                    profPer = ((fiatAm-1)/1)*100
                    print(profPer)




#arbCheck()
exch = ccxt.binance({'options': {'defaultType': 'swap'}})
exch.load_markets()
#print(exch.markets)

d = exch.fetch_transaction_fee('USD')
#d = exch.calculate_fee(symbol='BTC/USD:BTC', type='limit', side='buy', amount=0.0012, takerOrMaker='maker', price='24566.51')

print(d['cost'])






        
