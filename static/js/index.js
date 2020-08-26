
// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    app.fields = [];

    // This is the Vue data.
    app.data = {
        locations: [],
        mapsurl: "",
        eloc: null,
        zipcode: null,
        search_happened: false,
        loc_specified: false, // Whether the data comes
    };

    app.enumerate = function (locations) {
        let idx = 0;
        for (let loc of locations) {
            loc._idx = idx++;
        }
        return locations;
    }

    app.goto = function (idx) {
        // Shows the details.
        let loc = app.vue.locations[idx];
        app.vue.eloc = loc;
        // Loads the map.
        app.vue.mapsurl = "https://www.google.com/maps/embed/v1/place?key=" + maps_api_key
                    + "&q=" + loc.lat + "," + loc.lng;
    }

    app.lookup_zip = function (e) {
        if (e.keyCode === 13) {
            app.load_locations(true);
        }
    };

    app.load_locations = function (search_happened) {
        app.vue.eloc = null; // Clears old details.
        axios.get(get_locations_url, {
            params: {zipcode: app.vue.zipcode}
        }).then(function (response) {
            app.vue.search_happened = search_happened;
            app.vue.locations = app.enumerate(response.data.locations);
            app.vue.loc_specified = response.data.loc_specified;
            app.fields = response.data.fields;
        })
    };

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        lookup_zip: app.lookup_zip,
        goto: app.goto,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        app.load_locations(false);
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
