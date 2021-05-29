/* ###################################################################

Example socket client.
Code can be used as both MQ4 and MQ5 (on both 32-bit and 64-bit MT5)

Simply sends each new tick to the server, as a CRLF-terminated 
message. The example server then writes these to its Experts log.

################################################################### */


#property strict

// --------------------------------------------------------------------
// Include socket library
// --------------------------------------------------------------------

#include <socket-library-mt4-mt5.mqh>
#include <Trade\AccountInfo.mqh>

// --------------------------------------------------------------------
// EA user inputs
// --------------------------------------------------------------------

input string   Hostname = "127.0.0.1";    // Server hostname or IP address
input ushort   ServerPort = 8888;        // Server port


// --------------------------------------------------------------------
// Global variables and constants
// --------------------------------------------------------------------

ClientSocket * glbClientSocket = NULL;


// Account info instance.
CAccountInfo accountInfo;
datetime LastTime;

// --------------------------------------------------------------------
// Initialisation (no action required)
// --------------------------------------------------------------------

void OnInit() {
   Print("Robot initialized");
}


// --------------------------------------------------------------------
// Termination - free the client socket, if created
// --------------------------------------------------------------------

void OnDeinit(const int reason)
{
   if (glbClientSocket) {
      delete glbClientSocket;
      glbClientSocket = NULL;
   }
}


// --------------------------------------------------------------------
// Tick handling - set up a connection, if none already active,
// and send the current price quote
// --------------------------------------------------------------------

void OnTick()
{

   if (!glbClientSocket) {
      glbClientSocket = new ClientSocket(Hostname, ServerPort);
      /*if (glbClientSocket.IsSocketConnected()) {
         Print("Client connection succeeded");   
      } else {
         Print("Client connection failed");
      }*/
   }
   


   Print("glbClientSocket isocket connected value: ");
   Print(glbClientSocket.IsSocketConnected());
   
   /*if (glbClientSocket.IsSocketConnected()) {
      // Send the current price as a CRLF-terminated message
      string strMsg = Symbol() + "," + DoubleToString(SymbolInfoDouble(Symbol(), SYMBOL_BID), 6) + "," + DoubleToString(SymbolInfoDouble(Symbol(), SYMBOL_ASK), 6) + "\r\n";
      //Print(StringToShortArray(strMsg));
      glbClientSocket.Send(strMsg);
      
   } else {
      // Either the connection above failed, or the socket has been closed since an earlier
      // connection. We handle this in the next block of code...
      Print("Error has occurred");
   }*/
   
   // If the socket is closed, destroy it, and attempt a new connection
   // on the next call to OnTick()
   if (!glbClientSocket.IsSocketConnected()) {
      // Destroy the server socket. A new connection
      // will be attempted on the next tick
      Print("Client disconnected. Will retry.");
      delete glbClientSocket;
      glbClientSocket = NULL;
   }
   
   if(CheckNewBar()){
      if(checkTimeMessage()){
         if (glbClientSocket.IsSocketConnected()) {
            Print("Account info sent...");
            string strMsg = accountInfoMessage();
            glbClientSocket.Send(strMsg);
         } else {
            Print("Error has occurred");
         }     
      }
   }
   
}


bool checkTimeMessage(){

   datetime Time[];
   ArraySetAsSeries(Time, true);
   CopyTime(_Symbol, PERIOD_D1, 0, 2, Time);
   
   MqlDateTime timeStruct;
   TimeToStruct(Time[0], timeStruct);
   
   int hour = timeStruct.hour;
   int minute = timeStruct.min;
   int second = timeStruct.sec;
   
   /*Print("hour: ", hour);
   Print("minute: ", minute);
   Print("second: ", second);
   Print(typename(hour)); */

   if((hour == 0) && (minute == 0) && (second == 0)){
      return true;
   }
   
   return false;
}


string accountInfoMessage(){

   datetime Time[];
   ArraySetAsSeries(Time, true);
   CopyTime(_Symbol, PERIOD_D1, 0, 2, Time);

   string date_time = (string) Time[0];
   string balance = (string) accountInfo.Balance();
   string credit = (string) accountInfo.Credit();
   string account_profit = (string) accountInfo.Profit();
   string equity = (string) accountInfo.Equity();
   string margin = (string) accountInfo.Margin();
   string margin_free = (string) accountInfo.FreeMargin();
   string margin_level = (string) accountInfo.MarginLevel();
   string margin_so_call = (string) accountInfo.MarginCall();
   string margin_so_so = (string) accountInfo.MarginStopOut();
   
   string pythonMsg = "ACCOUNT_INFO" + "|" + date_time + "|" + balance + "|" + credit + "|" + account_profit + "|" + equity + "|" + margin + "|" + margin_free 
   + "|" + margin_level + "|" + margin_so_call + "|" + margin_so_so + "|";
   return pythonMsg;
}

bool CheckNewBar(){

   bool firstRun = false, newBar = false;
   
   datetime Time[];   
   ArraySetAsSeries(Time, true);
   
   CopyTime(_Symbol, PERIOD_D1, 0, 2, Time);
   if (LastTime == 0) firstRun = true;
   if(Time[0] > LastTime){
      if(firstRun == false) newBar = true;
      LastTime = Time[0];
   }
   
   return newBar;
}