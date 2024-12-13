'user-strict';
let ccxt = require ('ccxt');
let ccxtpro = ccxt.pro;
console.log(ccxtpro);
(async() => {
    const streams = {
        'binance': 'BTC/USDT',
        'bittrex': 'BTC/USDT',
        'bitfinex': 'BTC/USDT',
        'hitbtc': 'BTC/USDT',
        'upbit': 'BTC/USDT',
        'coinbasepro': 'BTC/USDT',
        'okex': 'BTC/USDT',
        'gateio': 'BTC/USDT'
    }
    await Promise.all(Object.keys(streams).map(exchangeId => 
        (async () => {
            //console.log(exchangeId)
            const exchange = new ccxtpro[exchangeId]({ enabledRateLimit: true })
            //console.log(exchange)
            //const exchange = new ccxtpro[exchangeId]({ enabledRateLimit: true })
            const symbol = streams[exchangeId];
            while(true) {
                try{
                    const orderbook = await exchange.watchOrderBook(symbol)
                    console.log(new Date(), exchange.id, symbol, orderbook['asks'][0], orderbook['bids'][0])
                    //HERE AJAX REQUEST
                } catch(e) {
                    console.log(symbol, e);
                }
            }
        })()
    ))
})()


$.ajax({
    type: "POST",
    url: "~/pythoncode.py",
    data: { param: text}
  }).done(function( o ) {
     // do something
  })