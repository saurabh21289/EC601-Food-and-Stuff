app.controller("RegisterCtrl", function ($scope, $http, $rootScope, $location) {
    $scope.register = function(user)
    {
        console.log(user);
        if (user.password != user.password2 || !user.password || !user.password2) {
            alert("Your passwords don't match");
            return;
        }
        //TODO: verify password are teh same and notify user
        else
        {
            $http.post('/register', user)
            .success(function (response) {
                if (response == "user already exists") {
                    alert("user already exists!!");
                }
                if (response != null && response != "user already exists") {
                    $rootScope.currentUser = response;
                    console.log($rootScope.currentUser);
                    $location.url("/profile");

                }
        });
        }
        
    }
});