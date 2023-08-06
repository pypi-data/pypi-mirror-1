// MCESG ComSat Module
// Author: Jason Alonso (jalonso@manicsages)

// Extend the MCESG Global Object
MCESG.modules.ComSat = function(config) {

// Import MCESG components
var go_json = MCESG.go_json;

// Import YUI components
var JSON = YAHOO.lang.JSON;

// Declare private members
var comsat = null;
var subscriptions = [];

// Declare the default configuration
var _config = {
        // Declare subdomain parameters
        subdomain: 'manicsages.org',
        iframe_suffix: '/media/manicscript/comsat.html',
        comsat_host: 'comsat.manicsages.org',
        protocol: 'http',

        // Declare parameters for url format
        hostname_length: 8

        // Declare parameters for form fields
};

// Load the configuration into _config
if( config == null ) config = {};
for( var k in _config )
        if( k in config )
                _config[k] = config[k];

// Declare routines
function _create_iframe(init) {
        // Set the document domain
        document.domain = _config.subdomain;

        // Create the iframe
        this.subframe = document.createElement('iframe');
        this.subframe.className = 'hidden';
        document.body.appendChild(this.subframe);

        // Create the page load callback 
        var _this = this;
        function comsat_connect() { _this.subframe.contentWindow.comsat_client = _this; if(init) init(); }

        // Choose a comsat hostname
        this.comsat_hostname = _config.comsat_host;

        // Connect to the comsat
        this.subframe.src = _config.protocol + '://' + this.comsat_hostname + _config.iframe_suffix;
        //this.subframe.contentWindow.onload = comsat_connect;
        YAHOO.util.Event.addListener(this.subframe, 'load', comsat_connect);
}

function _register_comsat(new_comsat) { comsat = new_comsat; }

this.set_subscriptions = function(new_subscriptions) {
        if( comsat && comsat.is_connected() )
                comsat.unsubscribe_all();
        subscriptions = new_subscriptions.slice();
        if( comsat && comsat.is_connected() )
                comsat.subscribe_all();
};

this.get_subscriptions = function() { return subscriptions.slice();};

this.send = function(msg, dst, hdr) { comsat.send(JSON.stringify(msg), dst, hdr); };

// Create events
this.event_launch = new YAHOO.util.CustomEvent('launch', this);
this.event_connect = new YAHOO.util.CustomEvent('connect', this);
this.event_data = new YAHOO.util.CustomEvent('data', this);
this.event_disconnect = new YAHOO.util.CustomEvent('disconnect', this);

// Export methods and properties
this._register_comsat = _register_comsat;
this.launch = _create_iframe;
};

// Construct the default comsat object
MCESG.comsat = new MCESG.modules.ComSat();
