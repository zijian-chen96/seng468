def triggers(dataList2, cond):

    dataList = []
    dataList.extend(dataList2)

    command = ''
    if dataList[1] == 'SET_BUY_AMOUNT':
        command = 'SET_BUY_TRIGGER'
    else:
        command = 'SET_SELL_TRIGGER'

    while command == 'SET_BUY_TRIGGER':
        if checkIsTrigger(dataList[2], dataList[3], command) == 1:
            buyStockPrice = getTriggerStockPrice(dataList[2], dataList[3], command)

            currFunds =  Decimal(checkAcountFunds(dataList[2]))
            holdMoney = Decimal(dataList[4])
            if holdMoneyFromAcount(dataList[2], dataList[4]) == 1:

                cond.notify()

                # username, transnumber, command, stockname, stockprice, amount, funds, times, cryptokey
                dbLogs((dataList[2], dataList[0], 'BUY-TRIGGER-HOLDER', dataList[3], None, holdMoney, currFunds, getCurrTimestamp(), None))

                while True:
                    dataFromQuote = sendToQuote(dataList[3] + ',' + dataList[2] + '\r').split(',')

                    if Decimal(dataFromQuote[0]) <= buyStockPrice and Decimal(dataFromQuote[0]) <= holdMoney:

                        #currFunds =  Decimal(checkAcountFunds(dataList[2]))

                        userFundsLeft = (holdMoney % Decimal(dataFromQuote[0])) + currFunds
                        stockAmount = int(holdMoney / Decimal(dataFromQuote[0]))

                        addToStocksDB((dataList[2],dataList[3],stockAmount))
                        # username, transnumber, command, stockname, stockprice, amount, funds, times, cryptokey
                        dbLogs((dataList[2], dataList[0], 'BUY', dataList[3], dataFromQuote[0], dataList[4], currFunds, getCurrTimestamp(), dataFromQuote[4]))
                        updateFunds(dataList[2],userFundsLeft)
                        deleteTriggerFromDB(dataList[2],dataList[3],command)

                        break

                    else:
                        print('sleep time')
                        time.sleep(1)
                print('finish exit out of thread!')

                break

            else:
                return "User funds is not enough!"

        else:
            return 'TRIGGER NOT FOUND!'

    while command == 'SET_SELL_TRIGGER':
        if checkIsTrigger(dataList[2], dataList[3], command) == 1:
            sellStockPrice = getTriggerStockPrice(dataList[2],dataList[3],command)

            currFunds = Decimal(checkAcountFunds(dataList[2]))
            numStocks = checkStockAmount(dataList[2], dataList[3])
            holdStockAmount = int(Decimal(dataList[4])/sellStockPrice)
            if holdStockAmountFromAcount(dataList[2], dataList[3], dataList[4]) == 1:

                cond.notify()

                dbLogs((dataList[2], dataList[0], 'SELL-TRIGGER-HOLDER', dataList[3], None, holdStockAmount, currFunds, getCurrTimestamp(), None))

                while True:
                    dataFromQuote = sendToQuote(dataList[3] + ',' + dataList[2] + '\r').split(',')
                    numStocksToSell = int(Decimal(dataList[4]) / Decimal(dataFromQuote[0]))

                    if Decimal(dataFromQuote[0]) >= sellStockPrice and holdStockAmount >= numStocksToSell:


                        moneyCanGet = numStocksToSell * Decimal(dataFromQuote[0])
                        newFunds = currFunds + moneyCanGet

                        updateStockAmount(dataList[2], dataList[3], (numStocks-numStocksToSell))
                        dbLogs((dataList[2], dataList[0], 'SELL', dataList[3], dataFromQuote[0], dataList[4], currFunds, getCurrTimestamp(), dataFromQuote[4]))
                        updateFunds(dataList[2], newFunds)
                        deleteTriggerFromDB(dataList[2],dataList[3],command)

                        break

                    else:
                        print('sleep time')
                        print("current stock price: " + dataFromQuote[0])
                        time.sleep(1)
                print('finish exit out of thread!')

                break

            else:
                return "User stock amount is not enough!"

        else:
            return 'TRIGGER NOT FOUND!'
