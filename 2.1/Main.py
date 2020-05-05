from BitfinexAccount import *
from Transactor import *
from Monitor import *
myBitfinexAccount = BitfinexAccount('4bY5ZpWrrlUuwGo93AZqrkllxS7xPIyi3jMB2bUCmx5','X8Mo3PeahGhMeSiW8Q5VLQZM4t0mvk0lLD5BR7ngNMp')   #read only API
myBitfinexAccount.refresh()
#myBitfinexAccount.showBalances()
#myBitfinexAccount.showOrdersNow()
#print myBitfinexAccount.orderStatus(3235929845)
#print myBitfinexAccount.makeOrder('0.01' , '180' , 'buy', 'exchange limit', 'ethusd')
#myBitfinexAccount.deleteOrder(3235931426)
#myBitfinexAccount.showOrdersNow()
monitor = Monitor( myBitfinexAccount )
monitor.moniting()

