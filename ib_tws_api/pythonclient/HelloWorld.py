from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract


class TestApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def error(self, reqID, errorCode, errorString):
        print("Error: ", reqID, " ", errorCode, " ", errorString)

    def contractDetails(self, reqID, contractDetails):
        print("Contract Details: ", reqID, " ", contractDetails)

def main():
    app = TestApp()
    app.connect("127.0.0.1", 4002, 0)

    contract = Contract()
    contract.symbol = "AAPL"
    contract.secType = "STK"
    contract.exchange = "SMART"
    contract.currency = "USD"
    contract.primaryExchange = "NASDAQ"

    app.reqContractDetails(1, contract)
    app.run()

if __name__ == "__main__":
    main()