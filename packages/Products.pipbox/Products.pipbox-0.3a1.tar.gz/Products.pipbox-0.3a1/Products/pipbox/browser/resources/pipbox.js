/*****************

   PIPbox tools for attaching JQuery Tools bling to CSS with option
   parameter strings.

*****************/


// Name space object for pipbox
pb = {};

// We may be creating multiple targets per page. We need to be able to
// tell them apart. We'll do it by counting.
pb.overlay_counter = 1;
// find our spinner; which isn't in the DOM yet, on page load
jQuery( function () { pb.spinner = jQuery('#kss-spinner'); });


/******
    jQuery.fn.prepOverlay
    JQuery plugin to inject overlay target into DOM
    and annotate it with the data we'll need in order
    to display it.
******/
jQuery.fn.prepOverlay = function(pbo) {
    return this.each( function(){
        var o = jQuery(this);
        // if there's a rel attribute, we've already
        // visited this node.
        if (! o.attr('rel')) {
            // be promiscuous, pick up the url from
            // either href or src attributes
            var src = o.attr('href') || o.attr('src');

            // translate url with config specifications
            if (pbo.urlmatch) {
                src = src.replace(RegExp(pbo.urlmatch), pbo.urlreplace);
            }

            if (pbo.subtype == 'inline') {
                // we're going to let tools' overlay do all the real
                // work. Just get the markers in place.
                src = src.replace(RegExp('^.+#'), '#');
                jQuery("[id='" + src.replace('#','') + "']").addClass('overlay');
                o.removeAttr('href').attr('rel', src);
            } else {
                // this is not inline, so in one fashion or another
                // we'll be loading it via the beforeLoad callback.
                
                // create a unique id for a target element
                var nt = 'pb_' + pb.overlay_counter;
                // create a target element; a div with markers;
                // content will be inserted here by the callback
                var el = jQuery(
                    '<div id="' + nt + '" class="overlay" />'
                    );

                // anything in src after a space is going to be a
                // jQuery filter to use in an ajax load so that
                // we don't get a whole page.
                var parts = src.split(' ');
                src = parts.shift();

                // we'll need the filter in the callback, so let's
                // store it on the target element.
                el.data('target', src).data('filter', parts.join(' '));
                
                // are we being asked to handle forms in an ajax overlay?
                if (pbo.formselector) {
                    // save the form selector on the target element.
                    el.data('formtarget', pbo.formselector);
                }
                
                // add the target element after the source element,
                // and mark the source with a rel attribute
                o.after(el).attr('rel', '#' + nt);

                // Set the preliminary target width and height
                // from the options. These may be just an approximation,
                // but that will get fixed in the overlay callback.
                if (pbo.width) {
                    el.width(pbo.width);
                }
                if (pbo.height) {
                    el.height(pbo.height);
                }

                pb.overlay_counter += 1;
            }

        }
    });
};

/******
    pb.image
    onBeforeLoad handler for image overlays
******/
pb.image = function () {
    pb.spinner.show();

    var content = this.getContent();
    if (content.find('img').length === 0) {
        var src = content.data('target');
        if (src) {
            var el = new Image();
            el.src = src;
            el = jQuery(el);
            content.append( el.addClass('pb-image') );
        }
    }
  return true;
};


/******
    pb.form_handler
    submit event handler for AJAX overlay forms.
    It does an ajax post of the form data, then
    uses the response to load the overlay target
    element.
******/
pb.form_handler = function (event) {
    var form = jQuery(event.target);
    var ajax_parent = jQuery(event.target).parents('.pb-ajax');
    var formtarget = ajax_parent.data('formtarget');
    if (jQuery.inArray(form[0], ajax_parent.find(formtarget)) < 0) {
        // this form wasn't ours; do the default action.
        return true;
    }
    var url = form.attr('action') + ' ' + ajax_parent.data('filter');
    var inputs = form.serializeArray();
    ajax_parent.load(url, inputs);
    return false;
};


/******
    pb.ajax
    onBeforeLoad handler for ajax overlays
******/
pb.ajax = function () {
    // pb.spinner.show();

    // get overlay target in DOM
    var content = this.getContent();
    var src = content.data('target');
    var filter = content.data('filter');
    var formtarget = content.data('formtarget');
    
    if (src) {
        // affix a random query argument to prevent
        // loading from browser cache
        var sep = (src.indexOf('?') >= 0)?'&':'?';
        src += sep + "rand=" + (new Date().getTime());

        // add filter, if any
        if (filter) {
            src += ' ' + filter;
        }

        // see if we already have a container to load
        var el = content.children('div.pb-ajax');
        if (! el.length) {
            // we don't, so create it, annotating it
            // with the information we'll need if it's
            // got an embedded forms.
            el = jQuery('<div class="pb-ajax" />');
            if (filter) {
                el.data('filter', filter);
            }
            if (formtarget) {
                el.data('formtarget', formtarget);
            }
            content.append( el );
        }

        // and load the div
        el.load(src, null, 
            function (responseText, textStatus, XMLHttpRequest) {
                if (formtarget) {
                    // It seems to be much more robust to bind the
                    // submit handler to the wrapper than for forms.
                    el.submit(pb.form_handler, el);
                }
            }
        );
        
    }
  return true;
};



pb.onClose = function () {
    pb.spinner.hide();
}



/******
    pb.iframe
    onBeforeLoad handler for iframe overlays
******/
pb.iframe = function () {
    pb.spinner.show();

    var content = this.getContent();
    if (content.find('iframe').length === 0) {
        var src = content.data('target');
        if (src) {
            var el = jQuery(
            '<iframe src="'+src+'" width="'+content.width()+'" height="'+content.height()+'" />'
            );
            content.append( el );
        }
    }
  return true;
};


/******
    pb.setup
    setup jqt inits
******/
pb.setup = function(p) {
    switch (p.type) {
        case 'overlay' :
            jQuery(function() {
                var config = p.config || {};
                var subtype = p.subtype;
                if (subtype != 'inline') {
                    config.onBeforeLoad = pb[p.subtype];
                    config.onClose = pb.onClose;
                }
                jQuery(p.selector).prepOverlay(p).overlay(config).css('cursor', 'pointer');
            });
            break;
        case 'tabs' :
            jQuery(function() {
                var config = p.config || {};
                config.tabs = p.tabs || config.tabs || 'a';
                jQuery(p.tabcontainer).addClass('pbactive').tabs(p.panes, config);
                jQuery(p.panes).addClass('pbactive');
            });
            break;
    }
};


/******
    pb.doSetup
    parameter: an options object(s)
    options vary by type and subtype of bling.
******/
pb.doSetup = function(s) {
    var plist = s;

    if (! (plist instanceof Array)) {
        plist = [plist];
    }
    for (var i=0;i<plist.length;i++) {
        var p = plist[i];
        pb.setup(p);
    }
};
