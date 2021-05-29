//|                              Copyright 2018, Intelligent Capital |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2018, MetaQuotes Software Corp."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict

input int MagicNumber = 4562;
input double Lots = 0.01;

// Temporality filters.
input bool TradeOnMonday = true;
input bool TradeOnTuesday = true;
input bool TradeOnWednesday = true;
input bool TradeOnThursday = true;
input bool TradeOnFriday = true;

input int StartHour = 0;
input int EndHour = 24;
input int StartMinute = 0;
input int EndMinute = 60;

#include <Trade\Trade.mqh>
CTrade ExtTrade;

// ----------------      Socket library variables ----------------.
#include <socket-library-mt4-mt5.mqh>

// ----- Client variables. -----
#include <Trade\PositionInfo.mqh>
input string Hostname = "127.0.0.1";
input ushort pythonServerPort = 9500;

int MAX_TRIES = 5;
ClientSocket * glbClientSocket = NULL;
CPositionInfo posInfo;
datetime LastTime;

// ----- Server variables. -----
#define SOCKET_LIBRARY_USE_EVENTS
#define TIMER_FREQUENCY_MS   1000

input ushort mqlServerPort = 23456;

ServerSocket * glbServerSocket;
ClientSocket * glbClients[];

bool glbCreatedTimer = false; 
bool canOperate = true;
// --------------------------------------------------------------------. 

 
 
 
//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
      Print("Expert initialized");
      
      // Create server socket.
      glbServerSocket = new ServerSocket(mqlServerPort, false);
      if(glbServerSocket.Created()){
          Print("Server socket created");
          glbCreatedTimer = EventSetMillisecondTimer(TIMER_FREQUENCY_MS);
      }else{
          Print("Server socket FAILED - is the port already in use?");
      }
  
      Print("Expert ID: ", posInfo.Magic());
      sendMessageToPython("", false, "HELLO FROM MQL5");
      return(INIT_SUCCEEDED);
      
      
  }
  
  
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
  
    // If expert is connected with Python, close the socket.
    if(glbClientSocket){
        delete glbClientSocket;
        glbClientSocket = NULL;
    }
    
    // Turn off MQL5 Expert Server.
    glbCreatedTimer = false;
    for(int i = 0; i < ArraySize(glbClients); i++){
        delete glbClients[i];
    }
    delete glbServerSocket;
    Print("Server socket terminated");


  }
  
//+------------------------------------------------------------------+
//| OnTimer()                                                        |
//+------------------------------------------------------------------+
void OnTimer()
{
    // Accept any new pending connections.
    AcceptNewConnections();
    
    // Proccess incoming data from clients.
    for(int i = ArraySize(glbClients) - 1; i >= 0; i--){
        HandleSocketIncomingData(i);
    }
    
}
  
//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
  {
  
      // Server configuration.
      if(!glbCreatedTimer) glbCreatedTimer = EventSetMillisecondTimer(TIMER_FREQUENCY_MS);
     
      if(canOperate == true){
         if(CheckNewBar()){
             if(tradeTime()){
                // Open, Close, Modify logic here...
                // Once the operation has been performed, use sendMessageToPython(dir)
             }
         }
      }else{
         // Robot deactivated.
         return;
      }
  }
  
  
//+------------------------------------------------------------------+
//| ChartEvent function                                              |
//+------------------------------------------------------------------+

// --------------------------------------------------------------------
// Event-driven functionality, turned on by #defining SOCKET_LIBRARY_USE_EVENTS
// before including the socket library. This generates dummy key-down
// messages when socket activity occurs, with lparam being the 
// .GetSocketHandle()
// --------------------------------------------------------------------

void OnChartEvent(const int id, const long& lparam, const double& dparam, const string& sparam)
{
   if (id == CHARTEVENT_KEYDOWN) {
      // If the lparam matches a .GetSocketHandle(), then it's a dummy
      // key press indicating that there's socket activity. Otherwise,
      // it's a real key press
         
      if (lparam == glbServerSocket.GetSocketHandle()) {
         // Activity on server socket. Accept new connections
         Print("New server socket event - incoming connection");
         AcceptNewConnections();

      } else {
         // Compare lparam to each client socket handle
         for (int i = 0; i < ArraySize(glbClients); i++) {
            if (lparam == glbClients[i].GetSocketHandle()) {
               HandleSocketIncomingData(i);
               return; // Early exit
            }
         }
         
         // If we get here, then the key press does not seem
         // to match any socket, and appears to be a real
         // key press event...
      }
   }
}

  
//+------------------------------------------------------------------+
//| Server functions.                                                |
//+------------------------------------------------------------------+

void AcceptNewConnections()
{
   // Keep accepting any pending connections until Accept() returns NULL
   ClientSocket * pNewClient = NULL;
   do {
      pNewClient = glbServerSocket.Accept();
      if (pNewClient != NULL) {
         int sz = ArraySize(glbClients);
         ArrayResize(glbClients, sz + 1);
         glbClients[sz] = pNewClient;
         Print("New client connection");
         
         pNewClient.Send("Welcome to MQL5 Server!");
      }
      
   } while (pNewClient != NULL);
}

void HandleSocketIncomingData(int idxClient)
{
   ClientSocket * pClient = glbClients[idxClient];

   // Keep reading CRLF-terminated lines of input from the client
   // until we run out of new data
   bool bForceClose = false; // Client has sent a "close" message
   string strCommand;
   do {
      // \r\n
      strCommand = pClient.Receive("");

      if (strCommand == "quote") {
         pClient.Send(Symbol() + "," + DoubleToString(SymbolInfoDouble(Symbol(), SYMBOL_BID), 6) + "," + DoubleToString(SymbolInfoDouble(Symbol(), SYMBOL_ASK), 6) + "\r\n");

      } else if (strCommand == "close") {
         bForceClose = true;
         
      } else if (strCommand != "") {
         // Potentially handle other commands etc here.
         // For example purposes, we'll simply print messages to the Experts log
         
         string result[];
         string sep = "|";
         ushort u_sep;
         
         u_sep = StringGetCharacter(sep, 0);
         int k = StringSplit(strCommand, u_sep, result);

         if(k > 0){
            string command = result[0];
            if(command == "ALLOCATION"){
               setLots(result, pClient);
               
            }else if(command == "ON_EXPERT"){
               onExpert(result, pClient);
               
            }else if(command == "ON_ORDER"){    
               onOrder(result, pClient);      
            }
         }
         
         /*if(k > 0){
            for(int i = 0; i < k; i++){
               Print(result[i], " ");
            }
         }*/
         
         //Print(strCommand);
      }
   } while (strCommand != "");

   // If the socket has been closed, or the client has sent a close message,
   // release the socket and shuffle the glbClients[] array
   if (!pClient.IsSocketConnected() || bForceClose) {
      Print("Client has disconnected");

      // Client is dead. Destroy the object
      delete pClient;
      
      // And remove from the array
      int ctClients = ArraySize(glbClients);
      for (int i = idxClient + 1; i < ctClients; i++) {
         glbClients[i - 1] = glbClients[i];
      }
      ctClients--;
      ArrayResize(glbClients, ctClients);
   }
}

// Example message: "ALLOCATION|4562:0.02"
void setLots(string &result[], ClientSocket * client){

   string allocations[];
   ArrayCopy(allocations, result, 0, 1, WHOLE_ARRAY);
   int size = ArraySize(allocations);
   
   bool res = false;
   
   for(int i = 0; i < size; i++){
      string alloc = allocations[i];
      
      string rest[];
      string sep = ":";
      ushort u_sep = StringGetCharacter(sep, 0);
      int k = StringSplit(alloc, u_sep, rest);
      
      int expert_id = int(rest[0]);
      double lots_to_trade = (double) rest[1];
      
      if(expert_id == MagicNumber){
         // Change Lots here.
         Print("Trading lots changed to: ", lots_to_trade);
         
         // Send message.
         res = client.Send("lots:DONE");
      }else{
         // Send error message.
         res = client.Send("magicNum:ERROR");
      }
      
      // Info coulnt be sent.
      if(res == false){
      
      }
   }
}

//"ON_EXPERT|4562|TRUE|FALSE|Hello from Python"
void onExpert(string &result[], ClientSocket * client){

   int expert_id = (int) result[1];
   bool turn_on = checkBoolean(result[2]);
   bool close_positions = checkBoolean(result[3]);
   string comment = result[4];
   
   bool res = false;
   
   if(expert_id == MagicNumber){   
      Print("canOperate: ", turn_on);
      canOperate = turn_on;
      
      string msg = "canOperate:DONE|";
      
      if(close_positions){
         Print("close positions: ", close_positions);
         bool success = ExtTrade.PositionClose(_Symbol, 3);
         if(!success){
            string error = ExtTrade.ResultRetcodeDescription();
            msg += "close_positions:error." + error;
         }else{
            msg += "close_positions:DONE";
            Print("All positions closed");
         }
      }
    
      // Send response to Python.
      res = client.Send(msg);
      
   }else{
      
      // Send error message.
      res = client.Send("magicNum:ERROR");
   }
   
   // Info could not been sent.
   if(res == false){
      
   }
   
}

// "ON_ORDER|4562|19|MODIFY|0|1.2685|1.1246|Hello from Python"
void onOrder(string &result[], ClientSocket * client){
   //Print(result[0]);
   
   int expert_id = (int) result[1];
   ENUM_ORDER_TYPE order_type = checkOrderType(result[2]);
   string order_id = result[3]; // Should be -1 in case we want to open a new order.
   
   // In case we want to open a position, otherwise should be 0.
   double openPrice = (double) result[4];
   double take_profit = (double) result[5];
   double stop_loss = (double) result[6];
   string comment = result[7];
   
   // Check valid magic number.
   if(expert_id == MagicNumber){
      if(order_type == ORDER_TYPE_BUY || order_type == ORDER_TYPE_SELL){
         ExtTrade.PositionOpen(_Symbol, order_type, Lots, openPrice, stop_loss, take_profit, comment);
      }else if(order_type == ORDER_TYPE_BUY_LIMIT){
         ExtTrade.BuyLimit(Lots, openPrice, _Symbol, stop_loss, take_profit);
      }else if(order_type == ORDER_TYPE_SELL_LIMIT){
         ExtTrade.SellLimit(Lots, openPrice, _Symbol, stop_loss, take_profit);
      }else if(order_type == ORDER_TYPE_BUY_STOP_LIMIT){
         ExtTrade.BuyStop(Lots, openPrice, _Symbol, stop_loss, take_profit);
      }else if(order_type == ORDER_TYPE_SELL_STOP_LIMIT){
         ExtTrade.SellStop(Lots, openPrice, _Symbol, stop_loss, take_profit);
      }else if(order_type == ORDER_TYPE_CLOSE_BY){
         ExtTrade.PositionClose(_Symbol, 3);
         
      }else if(order_type == WRONG_VALUE){
         client.Send("Order type not provided.");
      }
      
      // BuyLimitStop & SellLimitStop not implemented yet.
   }
}

bool checkBoolean(string value){
   if(value == "TRUE"){
      return true;
   }else if(value == "FALSE"){
      return false;
   }
   return false;
}

ENUM_ORDER_TYPE checkOrderType(string value){
   ENUM_ORDER_TYPE order_type;
   if(value == "ORDER_TYPE_BUY"){
      order_type = ORDER_TYPE_BUY;
      
   }else if(value == "ORDER_TYPE_SELL"){
      order_type = ORDER_TYPE_SELL;
      
   }else if(value == "ORDER_TYPE_BUY_LIMIT"){
      order_type = ORDER_TYPE_BUY_LIMIT;
      
   }else if(value == "ORDER_TYPE_BUY"){
      order_type = ORDER_TYPE_SELL_LIMIT;
      
   }else if(value == "ORDER_TYPE_BUY_STOP"){
      order_type = ORDER_TYPE_BUY_STOP;     
      
   }else if(value == "ORDER_TYPE_SELL_STOP"){
      order_type = ORDER_TYPE_SELL_STOP;  
   
   }else if(value == "ORDER_TYPE_SELL_STOP"){
      order_type = ORDER_TYPE_BUY_STOP_LIMIT;  
         
   }else if(value == "ORDER_TYPE_SELL_STOP"){
      order_type = ORDER_TYPE_SELL_STOP_LIMIT;   
        
   }else if(value == "ORDER_TYPE_CLOSE_BY"){
      order_type = ORDER_TYPE_CLOSE_BY;
      
   }else{
      order_type = WRONG_VALUE;
   }
   
   return order_type;
}

//+------------------------------------------------------------------+
//| Client functions.                                                |
//+------------------------------------------------------------------+
void sendMessageToPython(string dir, bool tradeInfo = true, string message = "")
  {
  
     int count = 0;
     do{
         if (!glbClientSocket) {
         
             // Connect with Python.
             glbClientSocket = new ClientSocket(Hostname, pythonServerPort);
             
             // Check connection.
             if(glbClientSocket.IsSocketConnected()){
             
                // Send the information.
                string strMsg = "";
                if(tradeInfo) strMsg = generateMessage(dir);
                else{ strMsg = message;  }
                
                Sleep(5000);
                glbClientSocket.Send(strMsg);
                
                // Close socket.
                delete glbClientSocket;
                glbClientSocket = NULL;
                
                Print("Message sent!");
                break;
                
             }else{
                count += 1;
             }
         }else{
             count += 1;
         }
     }while(count < MAX_TRIES);
     
     // Generate csv file.
     if(count >= MAX_TRIES){
         Print("ERROR. MAX TRIES reached. Trade information not sent.");
         
         Print("Generating a csv file...");
         int fileHandle = FileOpen("trades_" + string(MagicNumber) + "_MQL5.csv", FILE_READ|FILE_WRITE|FILE_CSV, "|");
         FileSeek(fileHandle, 0, SEEK_END);
         
         string info = "";
         FileWrite(fileHandle, StringConcatenate(info, generateMessage(dir), "\n"));
         FileClose(fileHandle);
         
         // Send email.
         //SendMail("Error sending trade info. Check expert " + string(MagicNumber) + ".", "Trade info saved as CSV in MQL Files.");
         
     }
  
  }

string generateMessage(string dir){

   string pythonMessage = "";
   
   string info_type = "TRADE_INFO";
   string magic_num = (string) 4376; //(string) posInfo.Magic();
   string date_time = TimeToString(posInfo.Time());
   string deal = (string) posInfo.Identifier();
   string symbol = (string) posInfo.Symbol();
   string type = (string) posInfo.TypeDescription();
   string direction = dir;
   string volume = (string) posInfo.Volume();
   string price = (string) posInfo.PriceOpen();
   string take_profit = (string) posInfo.TakeProfit();
   string stop_loss = (string) posInfo.StopLoss();
   string order_num = (string) posInfo.Ticket();
   string commission = (string) posInfo.Commission();
   string swap = (string) posInfo.Swap();
   string profit = (string) posInfo.Profit();
   string balance = (string) AccountInfoDouble(ACCOUNT_BALANCE);  
   string comment = "GREETINGS FROM MQL5"; //(string) posInfo.Comment();
   
   pythonMessage = info_type + "|" + magic_num + "|" + date_time + "|" + deal + "|" + symbol + "|" + type + "|" + direction + "|" + volume + "|" + price + "|" + take_profit + "|" + stop_loss + "|" + order_num + "|" + commission + "|" + swap + "|" + profit + "|" + balance + "|" + comment + "|";
   return (string) pythonMessage;
}


bool tradeTime(){

   datetime Time[];
   ArraySetAsSeries(Time, true);
   CopyTime(_Symbol, PERIOD_M1, 0, 2, Time);
  
   MqlDateTime timeStruct;
   TimeToStruct(Time[0], timeStruct);
   
   int hour = timeStruct.hour;
   int minute = timeStruct.min;
   int day_of_week = timeStruct.day_of_week;
   
   bool filter = (day_of_week == 1 && TradeOnMonday) || (day_of_week == 2 && TradeOnTuesday)
   || (day_of_week == 3 && TradeOnWednesday) || (day_of_week == 4 && TradeOnThursday)
   || (day_of_week == 5 && TradeOnFriday);
   
   if(filter){
      if(hour >= StartHour && hour <= EndHour){
         if(minute >= StartMinute && minute <= EndMinute){
            return true;
         }
      }
   }
   
   return false;
}


/*bool CheckNewBar(){

   bool firstRun = false, newBar = false;
   datetime Time[];   
   ArraySetAsSeries(Time, true);
   
   CopyTime(_Symbol, PERIOD_M1, 0, 2, Time);
   if (LastTime == 0) firstRun = true;
   if(Time[0] > LastTime){
      if(firstRun == false) newBar = true;
      LastTime = Time[0];
   }
   return newBar;
}*/


