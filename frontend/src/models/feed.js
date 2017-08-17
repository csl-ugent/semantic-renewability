// Required imports
var rethinkdb = require('rethinkdb');
var db = require('./database');
var database = new db();
var config = require('../config');

// What will be exported from this module.
module.exports = function(socket) {

  // Function used to emit data to the client.
  function emitData(cursor, table) {

      // Emit the changes.
      cursor.each(function(err, row) {

          // Debug information of changes.
          console.log(JSON.stringify(row));
          if(Object.keys(row).length > 0) {
            socket.emit("changeFeed", {"table" : table,
                                       "value" : row.new_val});
          }
      });
  }

  // We connect to the database.
  database.connectToDb(function(err,connection) {

      // Check if the connection to the database succeeded.
      if(err) {
        return callback(true,"Error connecting to database");
      }

      // We poll for changes to the experiment table.
      rethinkdb.db(config.rethinkdb.db)
          .table(config.rethinkdb.table_experiments)
          .changes().run(connection,function(err, cursor) {

              // Check for errors.
              if(err) {
                  console.log("Error while listening for changefeed for experiments: " + err);
                  return;
              }

              // We emit the data to the client.
              emitData(cursor, config.rethinkdb.table_experiments);
      });

      // We poll for changes to the transformations table.
      rethinkdb.db(config.rethinkdb.db)
          .table(config.rethinkdb.table_transformations)
          .changes().run(connection,function(err, cursor) {

              // Check for errors.
              if(err) {
                  console.log("Error while listening for changefeed for transformations: " + err);
                  return;
              }

              // We emit the data to the client.
              emitData(cursor, config.rethinkdb.table_transformations);
      });

      // We poll for changes to the tests table.
      rethinkdb.db(config.rethinkdb.db)
          .table(config.rethinkdb.table_tests)
          .changes().run(connection,function(err, cursor) {

              // Check for errors.
              if(err) {
                  console.log("Error while listening for changefeed for tests: " + err);
                  return;
              }

              // We emit the data to the client.
              emitData(cursor, config.rethinkdb.table_tests);
      });


      // We poll for changes to the analytics table.
      rethinkdb.db(config.rethinkdb.db)
          .table(config.rethinkdb.table_analytics)
          .changes().run(connection,function(err, cursor) {

              // Check for errors.
              if(err) {
                  console.log("Error while listening for changefeed for analytics: " + err);
                  return;
              }

              // We emit the data to the client.
              emitData(cursor, config.rethinkdb.table_analytics);
      });
  });
};
