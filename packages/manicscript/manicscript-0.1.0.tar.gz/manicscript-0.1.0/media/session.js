// MCESG Session Module
// Author: Jason Alonso (jalonso@manicsages)

// Extend the MCESG Global Object
MCESG.modules.Session = function(config) {

// Import MCESG components
var go_json = MCESG.go_json;

// Declare the default configuration
var _config = {
        // Declare parameters for url format
        url_profile: '/json/profile/',
        url_login: '/json/login/',
        url_logout: '/json/logout/',

        // Declare parameters for form fields
        form_login: 'login_form'
};

// Load the configuration into _config
if( config == null ) config = {};
for( var k in _config )
        if( k in config )
                _config[k] = config[k];

// Declare routines
function fetch_profile() {
        var _this = this;
        var handler = function(response) {
                // Determine if the user is logged-in
                if( response.logged_in ) 
                        _this.user = {
                                username:       response['username'],
                                last_name:      response['last_name'],
                                first_name:     response['first_name']
                        };
                else _this.user = null;

                // Fire profile event
                _this.event_profile.fire();
        };

        // Submit request
        go_json(_config.url_profile, null, handler);

        // Operation Complete!
}

function do_login() {
        var _this = this;
        var handler = function(response) {
                _this.fetch_profile();
                _this.event_login.fire();
        };
        go_json(_config.url_login, _config.form_login, handler);
}

function do_logout() {
        var _this = this;
        var handler = function(response) {
                _this.user = null;
                _this.event_logout.fire();
        };
        go_json(_config.url_logout, null, handler);
}

// Create events
this.event_profile = new YAHOO.util.CustomEvent('profile', this);
this.event_login = new YAHOO.util.CustomEvent('login', this);
this.event_logout = new YAHOO.util.CustomEvent('logout', this);

// Export methods and properties
this.user = null;
this.fetch_profile = fetch_profile;
this.do_login = do_login;
this.do_logout = do_logout;
};

// Construct the default session object
MCESG.session = new MCESG.modules.Session();
