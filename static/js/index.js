
// Map and its initialization.
function initMap() {
    var map = new google.maps.Map(
        document.getElementById('map'), {
          center: {lat: 37, lng: -120},
          zoom: 6
        });
    var infoWindow = new google.maps.InfoWindow();
    geolocate(infoWindow, map);
}

function geolocate(infoWindow, map) {
// Try HTML5 geolocation.
    if (navigator.geolocation) {
        console.log("Getting location");
        navigator.geolocation.getCurrentPosition(function (position) {
            console.log("Gotten position:", position.coords)
            var pos = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };

            infoWindow.setPosition(pos);
            infoWindow.setContent('Location found.');
            console.log("Found position:", pos)
            infoWindow.open(map);
            map.setCenter(pos);
        }, function () {
            console.log("some error");
            handleLocationError(true, infoWindow, map.getCenter());
        },
            {timeout: 2000});
    } else {
        // Browser doesn't support Geolocation
        console.log("nope");
        handleLocationError(false, infoWindow, map.getCenter());
    }
}

function handleLocationError(browserHasGeolocation, infoWindow, pos) {
    infoWindow.setPosition(pos);
    infoWindow.setContent(browserHasGeolocation ?
        'Error: The Geolocation service failed.' :
        'Error: Your browser doesn\'t support geolocation.');
    infoWindow.open(map);
}



// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
    };

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
