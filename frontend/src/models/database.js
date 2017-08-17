// Required imports.
var rethinkdb = require('rethinkdb');
var async = require('async');
var config = require('../config');

// Constructor.
function Database() {}

// General functionality.
Database.prototype = {

    // Function that is used for the database setup.
    setup: function(callback_completed) {

        // Reference to object itself.
        var self = this;

        // Async sequential execution of following tasks.
        async.waterfall([

          // First step is to connect to the rethinkdb server.
          function(callback) {
            self.connectToRethinkDbServer(function(err,connection) {
              if(err) {
                return callback(true,"Error in connecting to the RethinkDB server.");
              }
              callback(null,connection);
            });
          },

          // Create the database if needed.
          function(connection, callback) {
            rethinkdb.dbList().contains(config.rethinkdb.db).do(function(containsDb) {
              return rethinkdb.branch(
                containsDb,
                {created: 0},
                rethinkdb.dbCreate(config.rethinkdb.db)
              );
            }).run(connection, function(err) {
              callback(err, connection);
            });
          },

          // Create experiments table if needed.
          function(connection, callback) {
            rethinkdb.db(config.rethinkdb.db).tableList().contains(config.rethinkdb.table_experiments).do(function(containsTable) {
              return rethinkdb.branch(
                containsTable,
                {created: 0},
                rethinkdb.db(config.rethinkdb.db).tableCreate(config.rethinkdb.table_experiments)
              );
            }).run(connection, function(err) {
              callback(err, connection);
            });
          },

          // Create transformations table if needed.
          function(connection, callback) {
            rethinkdb.db(config.rethinkdb.db).tableList().contains(config.rethinkdb.table_transformations).do(function(containsTable) {
              return rethinkdb.branch(
                containsTable,
                {created: 0},
                rethinkdb.db(config.rethinkdb.db).tableCreate(config.rethinkdb.table_transformations)
              );
            }).run(connection, function(err) {
              callback(err, connection);
            });
          },

          // Create tests table if needed.
          function(connection, callback) {
            rethinkdb.db(config.rethinkdb.db).tableList().contains(config.rethinkdb.table_tests).do(function(containsTable) {
              return rethinkdb.branch(
                containsTable,
                {created: 0},
                rethinkdb.db(config.rethinkdb.db).tableCreate(config.rethinkdb.table_tests)
              );
            }).run(connection, function(err) {
              callback(err, connection);
            });
          },

          // Create analytics table if needed.
          function(connection, callback) {
            rethinkdb.db(config.rethinkdb.db).tableList().contains(config.rethinkdb.table_analytics).do(function(containsTable) {
              return rethinkdb.branch(
                containsTable,
                {created: 0},
                rethinkdb.db(config.rethinkdb.db).tableCreate(config.rethinkdb.table_analytics)
              );
            }).run(connection, function(err) {
              callback(err, connection);
            });
          }

        ],function(err, connection) {
          if(err) {
            console.error(err);
            process.exit(1);
            return;
          }

          // We execute the completed callback
          callback_completed();
        });
    },

    // Function used to connect to the rethinkdb server.
    connectToRethinkDbServer: function(callback) {

        // Connect to the rethinkdb server and catch any errors.
        rethinkdb.connect({
                host: config.rethinkdb.host,
                port: config.rethinkdb.port
            },
            function(err,connection) {
                callback(err,connection);
            });
    },

    // Function used to connect to a specific database.
    connectToDb: function(callback) {

        // Connect to the rethinkdb database and catch any errors.
        rethinkdb.connect({
                host: config.rethinkdb.host,
                port: config.rethinkdb.port,
                db: config.rethinkdb.db
        }, function(err,connection) {
          callback(err,connection);
        });
    }
};

// Exporting this object.
module.exports = Database