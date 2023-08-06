Introduction
============
KSS does not provide comforting error messages when a timeout occurs. collective.kssmessages displays an overlayed div when an error occurs. The possible causes are explained in non-technical terms.

Usage
=====
Run the collective.kssmessages profile in portal_setup. 

To make use of the error handler you will need to specify an error action in your KSS rule sheet, eg.

form#myform input[type="submit"]:click {
    evt-click-preventdefault: True;
    action-server: aMethod;
    aMethod-error: kssmessages-error;
}
