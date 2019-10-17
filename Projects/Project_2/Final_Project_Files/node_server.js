/* EID Project-2 Node.JS Server Script (supports websocket interface with the HTML client)
* @AUTHORS: Rushi James Macwan and Poorn Mehta
*
* @BRIEF: This is the main Node.JS server script that establishes connection with the localhost
* server and allows remote access while handling the MySQL database queries. The script also 
* uses websockets to communicate with the HTML client to service the client requests pertaining
* to the data available in the MySQL database. The basic flow of this program is as under:
*
* MySQL Databse <--> Node.JS Server <--> HTML Client (via websockets)
*
* @REFERENCES: The list of references that were used to create this script have been provided
* in the References folder of the project repository. Please, refer to the file named,
* "References_P2" to access all major reference resources that were used to create this document.
* Furthermore, some of the common resources have been added to the list below for direct 
* reference. Thanks.
*
* LIST OF REFERENCES:
*
* @COURTESY:
*
* The following list of webpages (references) were heavily used to develop this project codebase. 
* In many cases, the code was first copied from these webpages, and then was modified to fit the 
* project requirements. We, the authors of this work, duly credit these external resources for
* their resourcefulness and we clarify that this work is of our own, but these external references
* were used on several instances to leverage our work.
*
* INSTRUCTIONS TO RUN THIS SCRIPT:
*
* To run this script, please run the below command on the terminal:
*
* node node_server.js
*
* INSTALLATION INSTRUCTIONS:
*
* https://stackoverflow.com/questions/26409480/assign-result-from-mysql-query-to-string
* https://stackoverflow.com/questions/19084570/how-to-add-items-to-array-in-nodejs
* https://stackoverflow.com/questions/22381998/how-to-parse-the-data-from-rows-object-in-node-js-express-js-mysql2
* https://stackoverflow.com/questions/15462122/assign-console-log-value-to-a-variable
* https://www.w3schools.com/js/js_json_stringify.asp
* https://stackoverflow.com/questions/11151632/passing-an-object-to-client-in-node-express-ejs
* https://stackoverflow.com/questions/34264800/node-js-function-return-object-object-instead-of-a-string-value
* https://www.w3schools.com/js/js_json_stringify.asp
* https://dzone.com/articles/how-to-parse-json-data-from-a-rest-api-using-simpl
* https://www.fmsinc.com/MicrosoftAccess/query/snytax/append-query.html
* https://nodejs.org/api/dgram.html
* https://nodejs.org/api/http.html
* https://blog.abelotech.com/posts/measure-execution-time-nodejs-javascript/
* https://stackoverflow.com/questions/10617070/how-to-measure-execution-time-of-javascript-code-with-callbacks
* https://www.npmjs.com/package/execution-time
* https://www.geeksforgeeks.org/javascript-json-stringify-with-examples/
* https://www.codediesel.com/nodejs/mysql-transactions-in-nodejs/
* https://linuxize.com/post/how-to-install-node-js-on-raspberry-pi/
* https://www.npmjs.com/package/websocket
*
* For general instructions on installation of the tools required to run this script have been provided in the main
* directory inside the ReadMe.md file. Please, refer to that for detailed explanation.
*/
 
/* ******************************************************************************************
 * CODE BEGINS
 * ******************************************************************************************/

// Global Variables for the Node.JS script
var mydata;				// Logging variable
var lastJSON;			// Object for the last data entry acquired from the MySQL database
var myJSON_out = []; 	// JSON object file converted to string that will be fed to the HTML client
var myTIME;				// Time variable
var len;				// Number of elements available in the MySQL

// Null object created to append null data (i.e. zero humidity value) if number of database samples
// are below 10.
my2obj = new Object();
my2obj.Readings = 1000;
my2obj.Temperature = 0;
my2obj.Humidity = 0;
my2obj.Updated = 0;

// Conversion to string for the above created object
var myobj = JSON.stringify(my2obj);

// HTML client request modes that would allow this script to load either the last database entry or
// a set of the last 10 entries.

var mode1 = "LAST_ENTRY"; //mode1 for sending data to the client
var mode2 = "NET_TEST"; //mode2 for sending 10 data to the client

// Establishing Node.js server connection with the MySQL database

var mysql      = require('mysql');

var connection = mysql.createConnection({
  host     : 'localhost',
  user     : 'poorn',
  password : 'root',
  database : 'EID_Project1_DB'
});
 
connection.connect(function(err) {
  if (err) 
  {
    console.error('error connecting: ' + err.stack);
    return;
  } 
  console.log('connected as id ' + connection.threadId);
});
 
// Variable to fetch database entries from the associated table of DHT22 sensor;
var queryString = 'SELECT * FROM DHT22_Table';

// Initialization the execution time measurement function
const perf = require('execution-time')();

// Function that repeats itself at certain intervals to referesh the Node.JS server
// image of the MySQL database by updating the connection between the two and udpating
// the MySQL image on the Server side.

function Poll_DB() 
{
	connection.query(queryString, function(err, rows, fields) 
	{
      
		if (err) throw err;

		// Beginning to calculate the execution timing for database fetching time
		var begin = new Date();
		perf.start('apiCall');

		// Local variables
		var i, j;

		// Storing number of database entries available into len
		len = rows.length;
		// If there is not a single entry available, set the lastJSON object to a predefined one
		if(len < 1)
		{
			lastJSON = myobj;
		}
		else
		{
			mydata = rows[len - 1];
			// Converting acquired object to strings
			lastJSON = JSON.stringify(mydata);
		}

		// Setting the database server side entries to null if associated actual database entries do not exist
		if(len < 10) 
		{
			for(i = 0; i < len; i ++)
			{
				mydata = rows[i];
				myJSON_out[i] = JSON.stringify(mydata);
			}
		
			for(j = i; j < 10; j ++) 
			{
				myJSON_out[j] = myobj;
			}
		}
		
		else 
		{
			for(i = (len - 10), j = 0; i < len; i ++, j ++) 
			{
				mydata = rows[i];
				myJSON_out[j] = JSON.stringify(mydata);
			}
		}


		// Calculating the execution timing for database fetching time
		const results = perf.stop('apiCall');
		var end = new Date();
		var exec = results.time;
		
		// Converting objects to strings and parsing data as per need to acquire the start, end and exec times
		var t_flt = parseFloat(exec);
		t_flt = t_flt * 1000;
		exec = t_flt.toFixed(3);
		var d = {begin, end, exec};
		myTIME = JSON.stringify(d);
		         
	});
}

// Interval duration is approximately 4 seconds
setInterval(Poll_DB, 4000);
 
// Establishing connection to websocket for HTML Client interaction

var WebSocketServer = require('websocket').server;
var http = require('http');

var server = http.createServer(function(request, response) {
  // process HTTP request. Since we're writing just WebSockets
  // server we don't have to implement anything.
});

server.listen(9898, function() { });

// creating the server
wsServer = new WebSocketServer({
  httpServer: server
});

// WebSocket server
wsServer.on('request', function(request) 
{
	// Websocket requests to be accepted from the HTML client
	var connection = request.accept(null, request.origin);

	// This is the most important callback for us, we'll handle
	// all messages from users here.
	connection.on('message', function(message) 
	{
		// Server checks if the acquired user data is in UTF-8 format
		if (message.type === 'utf8') 
		{
			console.log(message.utf8Data);

			// If the acquired request from the HTML client is about sending the
			// last database entry, the server sends only the lastJSON object
			// after it is converted to string
			if(message.utf8Data == "LAST_ENTRY")
			{
				connection.sendUTF(lastJSON);
			}
			
			// If the acquired request from the HTML client is about sending the
			// last 10 database entries, the server sends a bundle of entries
			// that are converted to string from objects
			else if(message.utf8Data == "NET_TEST")
			{
				connection.sendUTF(myTIME);
				for(var i = 0; i < 10; i ++)
				{
				  connection.sendUTF(myJSON_out[i]);
				}
			}
			
			// If the server acquires an unanticipated request, an error is logged on
			// the server side console and no other actions are taken by the server script
			else
			{
			  console.log("UNDEFINED CLIENT REQUEST");
			}
		}
	});

	connection.on('close', function(connection) 
	{
		// close user connection
	});
});
