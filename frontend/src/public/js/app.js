// Define the `srApp` module
var srApp = angular.module('srApp', []);

// Socket IO connection for real-time updates.
srApp.factory('socket',function(){
  var socket = io.connect('http://localhost:3000');
  return socket;
});

// Define the `experimentController` controller on the `srApp` module
srApp.controller('experimentController', function ExperimentController($scope, $http, socket) {

    // Initially.
    $scope.experimentData = [];
    $scope.selectedExperiment = undefined;

    // We obtain all the available experiments.
    getExperimentData();
    function getExperimentData() {
        $http.get("/api/experiments").then(function(response){

            // We change the selected experiment.
            $scope.setSelectedExperiment(getMostRecent(response.data.data))

            // Update the experiment data.
            angular.extend($scope.experimentData, response.data.data);
        });
    }

    // Method used to obtain the most recent object.
    function getMostRecent(objects) {
        mostRecent = undefined;
        for (var idx in objects) {
            if (mostRecent == undefined || objects[idx].createdAt > mostRecent.createdAt) {
                mostRecent = objects[idx];
            }
        }
        return mostRecent;
    }

    // Method used to obtain experiment objects by id.
    function getExperimentById(experiment_id) {
        for (var idx in $scope.experimentData) {
            if ($scope.experimentData[idx].id == experiment_id) {
                return $scope.experimentData[idx];
            }
        }
        return undefined;
    }

    // Method used to determine if an experiment is currently active or not.
    $scope.isExperimentActive = function(experiment) {

        // If no experiment was selected, we set it automatically to false.
        if ($scope.selectedExperiment == undefined) {
            return false;
        }
        // We compare the 'experiment' and 'selectedExperiment' id's.
        return $scope.selectedExperiment.id == experiment.id;
    };

    // Method used to determine if a transformation is currently active or not.
    $scope.isTransformationActive = function(transformation) {

        // If no experiment was selected, we set it automatically to false.
        if ($scope.selectedExperiment.selectedTransformation == undefined) {
            return false;
        }
        // We compare the 'transformation' and 'selectedTransformation' id's.
        return $scope.selectedExperiment.selectedTransformation.id == transformation.id;
    };

    // Method used to determine if a test is currently active or not.
    $scope.isTestActive = function(test) {

        // If no experiment was selected, we set it automatically to false.
        if ($scope.selectedExperiment.selectedTest == undefined) {
            return false;
        }
        // We compare the 'transformation' and 'selectedTest' id's.
        return $scope.selectedExperiment.selectedTest.id == test.id;
    };


    // Method used to check if a test is successful or not
    $scope.checkTestSuccessful = function(test) {
        if (test != undefined) {
            for (var idx in test.test_data.results) {
                if (!test.test_data.results[idx].correct) {
                    return false;
                }
            }
        }
        return true;
    };

    // Method to change the currently selected experiment.
    $scope.setSelectedExperiment = function(experiment) {

        // We set the 'transformations' and/or 'tests' and/or 'analytics' fields if needed.
        if (experiment.transformations == undefined || experiment.tests == undefined
            || experiment.analytics == undefined) {

            // We retrieve all data of the specific experiment.
            $http.get("/api/experiments/" + experiment.id).then(function(response){

                // We set the transformations if needed.
                if (experiment.transformations == undefined) {
                    experiment.transformations = response.data.data.transformations;
                }

                // We set the tests if needed.
                if (experiment.tests == undefined) {
                    experiment.tests = response.data.data.tests;
                }

                // We set the analytics if needed.
                if (experiment.analytics == undefined) {
                    if (response.data.data.analytics.length > 0) {
                        experiment.analytics = response.data.data.analytics[0];
                    }
                }

                // We set the selected transformation (of this specific experiment) to the most recent transformation.
                experiment.selectedTransformation = getMostRecent(experiment.transformations);

                // We set the selected test (of this specific experiment) to the most recent test.
                experiment.selectedTest = getMostRecent(experiment.tests);
            });
        }

        // We set the full experiment object.
        $scope.selectedExperiment = experiment;
    };

    // Method used to change the currently selected transformation.
    $scope.setSelectedTransformation = function(transformation) {

        // We set the selected transformation of the currently selected experiment.
        $scope.selectedExperiment.selectedTransformation = transformation;
    };

    // Method used to change the currently selected test.
    $scope.setSelectedTest = function(test) {

        // We set the selected test of the currently selected experiment.
        $scope.selectedExperiment.selectedTest = test;
    };

    // Listen for changes through socket.io
    socket.on('changeFeed', function(data) {

        console.log(JSON.stringify(data));

        // Experiment additions.
        if (data.table == "experiments") {

            // We add the experiment to the list of experiments.
            $scope.experimentData.push(data.value);
            // We set the selected experiment to this experiment.
            $scope.selectedExperiment = data.value;
        }

        // Transformation additions.
        if (data.table == "transformations") {

            // We search for the correct experiment.
            var experiment = getExperimentById(data.value.experiment_id);

            // If the experiments has transformations loaded, we add it to the list of transformations.
            if (experiment.transformations != undefined) {
                experiment.transformations.push(data.value);
            } else {
                experiment.transformations = [data.value];
            }

            // If the experiment is currently selected, we change the selected transformation.
            if ($scope.selectedExperiment.id = experiment.id) {
                $scope.setSelectedTransformation(data.value);
            }
        }

        // Test additions.
        if (data.table == "tests") {

            // We search for the correct experiment.
            var experiment = getExperimentById(data.value.experiment_id);

            // If the experiments has tests loaded, we add it to the list of tests.
            if (experiment.tests != undefined) {
                experiment.tests.push(data.value);
            } else {
                experiment.tests = [data.value];
            }

            // If the experiment is currently selected, we change the selected tests.
            if ($scope.selectedExperiment.id = experiment.id) {
                $scope.setSelectedTest(data.value);
            }
        }

        // Analytic additions.
        if (data.table == "analytics") {

            // We search for the correct experiment.
            var experiment = getExperimentById(data.value.experiment_id);

            // We add the analytics to the correct experiment.
            experiment.analytics = data.value;
        }

        $scope.$apply();
    });
});

