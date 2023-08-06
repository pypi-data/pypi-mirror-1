//  MCESG Global Object and small utilities
//  Author: Jason Alonso <jalonso@manicsages>

function $(x) { return document.getElementById(x); }

function McesgGlobalObject(status_tag) {

// Import YUI features
var YUC = YAHOO.util.Connect;
var JSON = YAHOO.lang.JSON;

// Declare routines
function go_json( url, form, handler, fields, error_handler ) {
        var callbacks = {
                success: function(o) {
                        // Attempt to parse JSON
                        try {
                                response = JSON.parse(o.responseText);
                        } catch (x) {
                                _show_status( 'JSON parse error while parsing "' + o.responseText + '".');
                        }

                        // Render response
                        _show_status( response['text'] );

                        // Handle it
                        if( response['result'] == 'ok' ) handler(response);
                        else if( typeof(error_handler) != 'undefined' ) error_handler(response);
                },
                
                failure: function (o) {
                        try {
                                // Try parsing the error as JSON.
                                error_handler(JSON.parse(o.responseText).text);
                        } catch (x) {
                                if (o.responseText) error_handler(o.responseText);
                                else error_handler(o.statusText);
                        }
                }
        };

       // Prepare fields
       var fields_str = '';
       for( var k in fields )
               fields_str += k.toString() + '=' + escape(fields[k].toString()) + '&';
       
        // Submit request
        if( form != null ) {
                var post = $(form);
                YUC.setForm(post);
        }
        YUC.asyncRequest('POST', url, callbacks, fields_str);
}

function _show_status(status_text) {
        // Render response
        if( status_tag != null )
                $(status_tag).innerHTML = status_text;
}

// Declare sub-objects
this.widgets = new Object();
this.modules = new Object();

// Export methods and properties
this.go_json = go_json;

};

// Construct the MCESG Global Object
MCESG = new McesgGlobalObject();
