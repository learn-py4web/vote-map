var places = [
    {_idx: 0, name: 'Great Blue Heron', lat: 37.462910, lng: -121.997299},
    {_idx: 1, name: "Nuttal's Woodpecker", lat: 37.785023, lng: -122.472527},
    {_idx: 2, name: "Napoletana Pizzeria", loc: "1910 W El Camino Real, Mountain View, CA 94040"}
];


// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        places: [],
        mapsurl: ""
    };

    app.goto = function (idx) {
        p = app.vue.places[idx];
        app.vue.mapsurl = p.url;
    }

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        goto: app.goto
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        for (var p of places) {
            if (p.lat !== undefined) {
                p.url = "https://www.google.com/maps/embed/v1/place?key=" + maps_api_key
                    + "&q=" + p.lat + "," + p.lng;
                p.exturl = "https://www.google.com/maps/search/?api=1&query=" + p.lat + "," + p.lng;
            } else if (p.loc !== undefined) {
                eq = encodeURIComponent(p.loc);
                p.url = "https://www.google.com/maps/embed/v1/place?key=" + maps_api_key + "&q=" + eq;
                p.exturl = "https://www.google.com/maps/search/?api=1&query=" + eq;
            }
        }
        app.vue.places = places;
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
