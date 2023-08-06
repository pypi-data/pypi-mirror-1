if (!window.webflash) {
    webflash = (function() {
        var doc = document; // Alias to aid name-mangling
        var allCookies = doc.cookie;
        var cookie_name = null;
        var flash_shown = false;
        var container_id = null;
        var isIE = doc.attachEvent !== undefined;

        var get_payload = function() {
            var pos = allCookies.indexOf(cookie_name + '=');
            if (pos<0) {
                return null
            }
            var start = pos + cookie_name.length + 1;
            var end = allCookies.indexOf(';', start);
            if (end == -1) {
                end = allCookies.length;
            }
            var cookie = allCookies.substring(start, end);
            // remove cookie
            doc.cookie = cookie_name + '=; expires=Fri, 02-Jan-1970 00:00:00 GMT; path=/';
            return webflash.lj(unescape(cookie));
        }

        var display_flash = function() {
            if (flash_shown) return;
            flash_shown = true;
            var payload = get_payload()
            if (payload !== null) {
                var container = doc.getElementById(container_id);
                var flash_div = doc.createElement('div');
                flash_div.setAttribute(isIE?'className':'class', payload.status);
                var text = doc.createTextNode(payload.message);
                flash_div.appendChild(text);
                container.style.display = 'block';
                if (payload.delay) {
                    setTimeout(function() {
                        container.style.display = 'none';
                    }, payload.delay);
                }
                container.appendChild(flash_div);
            }
        }

        // Adds a display_flash for when the DOM is ready. It also adds a
        // callback for the window "onload" event since the domready event does
        // not always work.
        // This code is heavily inspired by jquery's ready() function.
        var attachLoadEvent = function() {
            if (!isIE) {
                // DOM 2 Event model
                var domloaded = "DOMContentLoaded";
                doc.addEventListener(domloaded, function() {
                    doc.removeEventListener(domloaded, arguments.callee, false);
                    display_flash();
                }, false);
                // A fallback to window.onload that will always work
                window.addEventListener("load", display_flash, false);
            } else if (isIE) {
                // IE event model
                var domloaded = "onreadystatechange";
                // ensure firing before onload,
                // maybe late but safe also for iframes
                doc.attachEvent(domloaded, function() {
                    doc.detachEvent(domloaded, arguments.callee);
                    display_flash();
                });
                // If IE and not an iframe
                // continually check to see if the document is ready
                if (doc.documentElement.doScroll && !frameElement ) (function(){
                    if (flash_shown) return;
                    try {
                        // If IE is used, use the trick by Diego Perini
                        // http://javascript.nwbox.com/IEContentLoaded/
                        doc.documentElement.doScroll("left");
                    } catch( error ) {
                        setTimeout( arguments.callee, 0 );
                        return;
                    }
                    display_flash()
                })();
                // A fallback to window.onload that will always work
                window.attachEvent("load", display_flash);
            }
        }

        return function(opts) {
            cookie_name = opts.name;
            container_id = opts.id;
            return {
                payload: get_payload,
                render: attachLoadEvent
            }
        }
    })();

    // This function needs to live outside the anonymous function's closure for
    // YUICompressor to be able to mangle the private symbols because it uses
    // eval
    webflash.lj = function(s) {
        // Loads a JSON string
        var r;
        eval("r="+s);
        return r;
    };
};
