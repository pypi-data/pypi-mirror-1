// master.js - scanbooker behaviour control


var DEBUG = true;

// Allow debugging code to stick around:
if (!DEBUG || !window.console || !console.firebug) {
    var names = ["log", "debug", "info", "warn", "error", "assert", "dir", "dirxml", "group", 
                 "groupEnd", "time", "timeEnd", "count", "trace", "profile", "profileEnd"];

    window.console = {};
    for (var i = 0; i < names.length; i += 1) { 
        window.console[names[i]] = function () {};
    }
}

var greyed = {
    'loginform-username': '<username>',
    'loginform-password': 'password',
    'project-search-terms': 'Search terms...',
    'user-search-terms': 'Search terms...'
};

window.addEvent('domready', function () {
    $$('.box').addRoundedCorners();

    $each(greyed, function (txt, id) { 
        var elem = $(id);
        // Set up elements as greyed to start with.
        if (elem) { elem.toggleGreyed(greyed); }
    });

//    var desc = $('id_description');
//    if (desc) {
//        desc.checkLen(255, 'desc_charcount');
//        desc.addEvents({
//            // Unfortunately this has to be called on keyup and keydown, as 
//            // keypress always seems to be out-by-one.
//            keyup: desc.checkLen.pass([255, 'desc_charcount'], desc),
//            keydown: desc.checkLen.pass([255, 'desc_charcount'], desc)
//        });
//    }

    $$('input').each(function (elem) {
        elem.addEvents({
            focus: elem.toggleGreyed.pass(greyed, elem),
            blur: elem.toggleGreyed.pass(greyed, elem)
        });
    });

});

