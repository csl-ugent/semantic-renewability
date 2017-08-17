var express = require('express');
var router = express.Router();

// Static files serving.
router.use('/',require('./home'));

// API
router.use('/api/experiments', require('./experiments'));

module.exports = router;