// MCESG crypto/sign Module
// Author: Jason Alonso (jalonso@manicsages)

// Extend the MCESG Global Object
MCESG.modules.Sign = function(config) {

// Import JSON
var JSON = YAHOO.lang.JSON;

// Unpack and verify a signed message
function verify(key, signed_msg) {
        method = signed_msg.alg.split('-');
        alg = method[0];
        digest = method[1];
        encoding = method[2];
        json_msg = signed_msg.msg;
        sig = signed_msg.sig;

        if( alg != 'HMAC' ) return [false, null];

        if( digest == 'MD5' ) module = MCESG.crypto.md5;
        else if( digest == 'SHA256' ) module = MCESG.crypto.sha256;
        else if( digest == 'SHA512' ) module = MCESG.crpyto.sha512;
        else return [false, null];

        if( encoding == 'HEX' ) true_sig = module.hex_hmac(key, json_msg);
        else if( encoding == 'BASE64' ) true_sig = module.b64_hmac(key, json_msg);
        else return [false, null];

        msg = JSON.parse(json_msg);

        return [true_sig == sig, msg];
}

function sign(key, msg, alg) {
        if( alg == null ) alg = 'HMAC-SHA256-HEX';

        method = alg.split('-');
        alg2 = method[0];
        digest = method[1];
        encoding = method[2];
        json_msg = JSON.stringify(msg);

        if( alg2 != 'HMAC' ) return null;

        if( digest == 'MD5' ) module = MCESG.crypto.md5;
        else if( digest == 'SHA256' ) module = MCESG.crypto.sha256;
        else if( digest == 'SHA512' ) module = MCESG.crpyto.sha512;
        else return null;

        if( encoding == 'HEX' ) sig = module.hex_hmac(key, json_msg);
        else if( encoding == 'BASE64' ) sig = module.b64_hmac(key, json_msg);
        else return null;

        return {'alg': alg, 'msg': json_msg, 'sig': sig};
}

// Export methods
this.verify = verify;
this.sign = sign;
};

// Construct the default crypto object
if( MCESG.crypto == null ) MCESG.crypto = Object();
MCESG.crypto.sign = new MCESG.modules.Sign();
