// Required imports.
var express = require('express');
var app = express();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var db = require('./models/database');

// Provide changefeed to clients that connected through socket io.
io.on('connection', function(socket) {
  require('./models/feed')(socket);
});

// Configuration.
var config = require(__dirname + '/config.js');

// Used for serving static files, controllers, 404 and errors.
app.use(express.static(__dirname + '/public'));
app.use(require(__dirname + '/controllers'));
app.use(handle404);
app.use(handleError);

// Middleware used to handle invalid requests.
function handle404(req, res, next) {
  res.status(404).end('Not found, please check the URL.');
}

// Middleware used to handle errors (only used in dev mode).
function handleError(err, req, res, next) {
  console.error(err.stack);
  res.status(500).json({err: err.message});
}

// We create a new database model and make sure the database
// structure has been initialized correctly.
var databaseModel = new db()
databaseModel.setup(function() {
  http.listen(config.express.port, function(){
    console.log('Listening on port ' + config.express.port);
  });
});
