var express = require('express');
var router = express.Router();

// The experiments model.
var experimentsModel = require('../models/experiments');

// General experiments endpoint.
router.route('/')
  .get(function(req, res) {

    // Code to fetch the experiments.
    var experimentsModelObj = new experimentsModel();

    // Calling our model function.
    experimentsModelObj.getAllExperiments(function(err, pollResponse) {
      if(err) {
        return res.json({"responseCode" : 1, "responseDesc" : pollResponse});
      }
      res.json({"responseCode" : 0, "responseDesc" : "Success", "data" : pollResponse});
    });
  });

// Obtain information about a specific experiment.
router.route('/:id').all(function(req, res, next) {

    // We obtain the id from the URL (as a param).
	var id = req.params.id;
	req.idExp = id;
	next();

}).get(function(req, res) {
    // Code to fetch the experiments.
    var experimentsModelObj = new experimentsModel();

    // Calling our model function.
    experimentsModelObj.getExperiment(req.idExp, function(err, pollResponse) {
      if(err) {
        return res.json({"responseCode" : 1, "responseDesc" : pollResponse});
      }
      res.json({"responseCode" : 0, "responseDesc" : "Success", "data" : pollResponse});
    });
});


module.exports = router;