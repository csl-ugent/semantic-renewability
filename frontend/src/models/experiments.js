// Some required imports.
var rethinkdb = require('rethinkdb');
var async = require('async');
var db = require('./database');
var config = require('../config');

// Constructor.
function Experiments() {}

// General functionality.
Experiments.prototype = {

    // Method used to obtain all of the experiments.
    getAllExperiments: function(callback_completed) {

        // Async sequential execution of following tasks.
        async.waterfall([

          // First, we need to be connected to the database.
          function(callback) {

            // We connect to the database.
            var database = new db();
            database.connectToDb(function(err, connection) {
              if(err) {
                  return callback(true, "Error connecting to database");
              }
              callback(null,connection);
            });
          },

          // Secondly, we retrieve all experiments from the database.
          function(connection, callback) {
            rethinkdb.table(config.rethinkdb.table_experiments).run(connection,function(err,cursor) {

              // We close the connection.
              connection.close();
              if(err) {
                return callback(true, "Error fetching experiments from database.");
              }

              // Convert the result to an array.
              cursor.toArray(function(err, result) {
                if(err) {
                  return callback(true,"Error reading cursor");
                }
                callback(null, result)
              });
            });
          }
        ],function(err, data) {

          // Pass the final result as a callback.
          callback_completed(err === null ? false : true, data);
        });
    },

    // Get all information regarding a single experiment.
    getExperiment: function(id, callback_completed) {

        // Async sequential execution of following tasks.
        async.waterfall([

          // First, we need to be connected to the database.
          function(callback) {

            // We connect to the database.
            var database = new db();
            database.connectToDb(function(err, connection) {
              if(err) {
                  return callback(true, "Error connecting to database");
              }
              callback(null,connection);
            });
          },

          // Secondly, we retrieve the specific experiment from the database.
          function(connection, callback) {
            rethinkdb.table(config.rethinkdb.table_experiments).get(id)
                .run(connection,function(err, result) {
              if(err) {
                return callback(true, "Error fetching experiment from database.", null);
              }
              callback(null, connection, result)
            });
          },

          // Next, we retrieve the transformations for this experiment.
          function(connection, currentData, callback) {
            rethinkdb.table(config.rethinkdb.table_transformations)
                .filter(rethinkdb.row('experiment_id').eq(id))
                .run(connection,function(err,cursor) {

              if(err) {
                  console.log(err);
                return callback(true, "Error fetching transformations from database.", null);

              }

              // Convert the result to an array.
              cursor.toArray(function(err, result) {
                if(err) {
                  return callback(true, "Error reading cursor", null);
                }

                // We add the transformations as an extra field to our current data.
                currentData.transformations = result;
                callback(null, connection, currentData);
              });
            });
          },

         // Next, we retrieve the tests for this experiment.
          function(connection, currentData, callback) {
            rethinkdb.table(config.rethinkdb.table_tests)
                .filter(rethinkdb.row('experiment_id').eq(id))
                .run(connection,function(err,cursor) {

              if(err) {
                  console.log(err);
                return callback(true, "Error fetching tests from database.", null);

              }

              // Convert the result to an array.
              cursor.toArray(function(err, result) {
                if(err) {
                  return callback(true, "Error reading cursor", null);
                }

                // We add the tests as an extra field to our current data.
                currentData.tests = result;
                callback(null, connection, currentData);
              });
            });
          },

         // Next, we retrieve the analytics for this experiment.
          function(connection, currentData, callback) {
            rethinkdb.table(config.rethinkdb.table_analytics)
                .filter(rethinkdb.row('experiment_id').eq(id))
                .run(connection,function(err,cursor) {

              // We close the connection.
              connection.close();
              if(err) {
                  console.log(err);
                return callback(true, "Error fetching analytics from database.", null);

              }

              // Convert the result to an array.
              cursor.toArray(function(err, result) {
                if(err) {
                  return callback(true, "Error reading cursor", null);
                }

                // We add the analytics as an extra field to our current data.
                currentData.analytics = result;
                callback(null, currentData);
              });
            });
          },
        ],function(err, data) {

          // Pass the final result as a callback.
          callback_completed(err === null ? false : true, data);
        });
    }
};

// Exporting this object.
module.exports = Experiments
