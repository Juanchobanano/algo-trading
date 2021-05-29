/* ###################################################################

Example socket server.
Code can be used as both MQ4 and MQ5 (on both 32-bit and 64-bit MT5)

Receives messages from the example client and simply writes them
to the Experts log.

In addition, you can telnet into the server's port. Any CRLF-terminated
message you type is similarly printed to the Experts log. You
can also type in the commands "quote", to which the server reponds
with the current price of its chart, or "close", which causes the
server to shut down the connection.

As well as demonstrating server functionality, the use of Receive()
and the event-driven handling are also applicable to a client
which needs to receive data from the server as well as just sending it.

################################################################### */


#property strict

// --------------------------------------------------------------------
// Include socket library, asking for event handling
// --------------------------------------------------------------------

#define SOCKET_LIBRARY_USE_EVENTS
#include <socket-library-mt4-mt5.mqh>


// --------------------------------------------------------------------
// EA user inputs
// --------------------------------------------------------------------

input ushort   ServerPort = 23456;  // Server port


// --------------------------------------------------------------------
// Global variables and constants
// --------------------------------------------------------------------

// Frequency for EventSetMillisecondTimer(). Doesn't need to 
// be very frequent, because it is just a back-up for the 
// event-driven handling in OnChartEvent()
#define TIMER_FREQUENCY_MS    1000

// Server socket
ServerSocket * glbServerSocket;

// Array of current clients
ClientSocket * glbClients[];


// Watch for need to create timer;
bool glbCreatedTimer = false;


// --------------------------------------------------------------------
// Initialisation - set up server socket
// --------------------------------------------------------------------

void OnInit()
{
   // Create the server socket
   glbServerSocket = new ServerSocket(ServerPort, false);
   if (glbServerSocket.Created()) {
      Print("Server socket created");

      // Note: this can fail if MT4/5 starts up
      // with the EA already attached to a chart. Therefore,
      // we repeat in OnTick()
      glbCreatedTimer = EventSetMillisecondTimer(TIMER_FREQUENCY_MS);
   } else {
      Print("Server socket FAILED - is the port already in use?");
   }
   
   //Print(GetDateTime());
   //Print(AccountInfoMessage());
}


// --------------------------------------------------------------------
// Termination - free server socket and any clients
// --------------------------------------------------------------------

void OnDeinit(const int reason)
{
   glbCreatedTimer = false;
   
   // Delete all clients currently connected
   for (int i = 0; i < ArraySize(glbClients); i++) {
      delete glbClients[i];
   }

   // Free the server socket. *VERY* important, or else
   // the port number remains in use and un-reusable until
   // MT4/5 is shut down
   delete glbServerSocket;
   Print("Server socket terminated");
}


// --------------------------------------------------------------------
// Timer - accept new connections, and handle incoming data from clients.
// Secondary to the event-driven handling via OnChartEvent(). Most
// socket events should be picked up faster through OnChartEvent()
// rather than being first detected in OnTimer()
// --------------------------------------------------------------------

void OnTimer()
{
   // Accept any new pending connections
   AcceptNewConnections();
   
   // Process any incoming data on each client socket,
   // bearing in mind that HandleSocketIncomingData()
   // can delete sockets and reduce the size of the array
   // if a socket has been closed

   for (int i = ArraySize(glbClients) - 1; i >= 0; i--) {
      HandleSocketIncomingData(i);
   }
}


// --------------------------------------------------------------------
// Accepts new connections on the server socket, creating new
// entries in the glbClients[] array
// --------------------------------------------------------------------

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


// --------------------------------------------------------------------
// Handles any new incoming data on a client socket, identified
// by its index within the glbClients[] array. This function
// deletes the ClientSocket object, and restructures the array,
// if the socket has been closed by the client
// --------------------------------------------------------------------

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
               allocateLots(result);
               
            }else if(command == "ON_EXPERT"){
               onExpert(result);
               
            }else if(command == "ON_ORDER"){    
               onOrder(result);      
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


// --------------------------------------------------------------------
// Use OnTick() to watch for failure to create the timer in OnInit()
// --------------------------------------------------------------------

void OnTick()
{
   if (!glbCreatedTimer) glbCreatedTimer = EventSetMillisecondTimer(TIMER_FREQUENCY_MS);

   
}

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


// Example message: "ALLOCATION|4562:0.02|4321:0.05|5376:0.5"
void allocateLots(string &result[]){
   string allocations[];
   ArrayCopy(allocations, result, 0, 1, WHOLE_ARRAY);
   int size = ArraySize(allocations);
   
   for(int i = 0; i < size; i++){
      string alloc = allocations[i];
      
      string res[];
      string sep = ":";
      ushort u_sep = StringGetCharacter(sep, 0);
      int k = StringSplit(alloc, u_sep, res);
      
      string expert_id = res[0];
      double lots_to_trade = (double) res[1];
      
      Print(expert_id, " trade => ", lots_to_trade);
   }
}

//"ON_EXPERT|4562|TRUE|FALSE|Hello from Python"
void onExpert(string &result[]){

   string expert_id = result[1];
   bool turn_on = checkBoolean(result[2]);
   bool close_position = checkBoolean(result[3]);
   string comment = result[4];
   
   Print(expert_id, " => ", turn_on);
   Print("Close position: ", close_position);
   Print(comment);
   
}

// "ON_ORDER|4562|19|MODIFY|0|1.2685|1.1246|Hello from Python"
void onOrder(string &result[]){
   Print(result[0]);
   
   string expert_id = result[1];
   string order_id = result[2];
   ENUM_TRADE_REQUEST_ACTIONS action = checkAction(result[3]);
   
   // In case we want to open a position, otherwise should be 0.
   double openPrice = (double) result[4];
   double take_profit = (double) result[5];
   double stop_loss = (double) result[6];
   string comment = result[7];
   
   Print(openPrice, " => ", take_profit, " => ", stop_loss);
   Print(comment);
   
}

bool checkBoolean(string value){
   if(value == "TRUE"){
      return true;
   }else if(value == "FALSE"){
      return false;
   }
   return false;
}

ENUM_TRADE_REQUEST_ACTIONS checkAction(string value){
   ENUM_TRADE_REQUEST_ACTIONS action;
   if(value == "TRADE_ACTION_DEAL"){
      action = TRADE_ACTION_DEAL;
   }else if(value == "TRADE_ACTION_PENDING"){
      action = TRADE_ACTION_PENDING;
   }else if(value == "TRADE_ACTION_SLTP"){
      action = TRADE_ACTION_SLTP;
   }else if(value == "TRADE_ACTION_REMOVE"){
      action = TRADE_ACTION_REMOVE;
   }else if(value == "TRADE_ACTION_CLOSE_BY"){
      action = TRADE_ACTION_CLOSE_BY;        
   }else{
      action = TRADE_ACTION_DEAL;
   }
   return action;
}