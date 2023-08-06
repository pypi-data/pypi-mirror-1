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
                    '<div id="' + nt + '" class="overlay overlay-' + pbo.subtype + '" />'
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
                // save the form selector on the target element.
                el.data('formtarget', pbo.formselector);
                el.data('noform', pbo.noform);
                el.data('closeselector', pbo.closeselector);
                
                // add the target element at the end of the portal wrapper 
                // or body.
                var container = jQuery("#visual-portal-wrapper");
                if (! container.length ) {
                    container = jQuery("body");
                }
                el.appendTo(container);

                // mark the source with a rel attribute so jqt will find
                // the overlay
                o.attr('rel', '#' + nt);
                
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
        content.data('oh', content.outerHeight(true));
        content.data('ow', content.outerWidth(true));
        var src = content.data('target');
        if (src) {
            var el = new Image();
            jQuery(el).load( function () {
                var nel = jQuery(this);
                var h = nel.outerHeight(true);
                var w = nel.outerWidth(true);
                var p = nel.parent();
                p.height(p.data('oh')+h);
                p.width(p.data('ow')+w);
            });
            el.src = src;
            el = jQuery(el);
            content.append( el.addClass('pb-image') );
        }
    }
    pb.spinner.hide();
    return true;
};


/******
    pb.close_handler
    when we're in an event, we don't necessarily have
    easy access to the overlay object to use its close
    method.
    This is an alternate.
******/
pb.close_handler = function (event) {
    jQuery(event.target).closest('.overlay').find('.close').click();
    // avoid form submit
    return false;
}


/******
    pb.form_handler
    submit event handler for AJAX overlay forms.
    It does an ajax post of the form data, then
    uses the response to load the overlay target
    element.
******/
pb.form_handler = function (event) {
    var form = jQuery(event.target);
    var ajax_parent = form.closest('.pb-ajax');
    var close_method = ajax_parent.data('close');
    var formtarget = ajax_parent.data('formtarget');

    if (jQuery.inArray(form[0], ajax_parent.find(formtarget)) < 0) {
        // this form wasn't ours; do the default action.
        return true;
    }

    pb.spinner.show();

    var url = form.attr('action') + ' ' + ajax_parent.data('filter');
    var inputs = form.serializeArray();
    ajax_parent.load(url, inputs, function () {
        pb.spinner.hide();

        jQuery(this).wrapInner('<div />');
        
        var myform = ajax_parent.find(formtarget);
        if (! myform.length) {
            switch (ajax_parent.data('noform')) {
                case 'close' :
                    close_method();
                    break;
                case 'reload' :
                    close_method();
                    location.reload();
                    break;
    			
            }
        } else {
            myform.submit(pb.form_handler);
            if (closeselector) {
                el.find(closeselector).click(function (event) {
                    close_method();
                    return false;
                });
            }
        }
    });

    return false;
};


/******
    pb.ajax
    onBeforeLoad handler for ajax overlays
******/
pb.ajax = function () {
    pb.spinner.show();

    // get overlay target in DOM
    var ovl = this;
    var content = this.getContent();
    var src = content.data('target');
    var filter = content.data('filter');
    var formtarget = content.data('formtarget');
    var closeselector = content.data('closeselector');
    
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
            el.data('filter', filter);
            el.data('formtarget', formtarget);
            el.data('noform', content.data('noform'));
            // include a reference to the overlay's close method
            el.data('close', this.close);

            content.append( el );
        }

        // and load the div
        el.load(src, null, function () {
            // a non-semantic div here will make sure we can
            // do enough formatting.
            jQuery(this).wrapInner('<div />');
            
            // add the submit handler if we've a formtarget
            if (formtarget) {
                el.find(formtarget).submit(pb.form_handler);
            }
            // if a closeselector has been specified, tie it to the overlay's
            // close method via closure
            if (closeselector) {
                el.find(closeselector).click( function (event) {
                    ovl.close();
                    return false;
                });
            }
        });
        
        
    }
    pb.spinner.hide();
    return true;
};



/******
    pb.iframe
    onBeforeLoad handler for iframe overlays.

    Note that the spinner is handled a little differently
    so that we can keep it displayed while the iframe's
    content is loading.
******/
pb.iframe = function () {
    pb.spinner.show();

    var content = this.getContent();
    if (content.find('iframe').length === 0) {
        var src = content.data('target');
        if (src) {
            content.append( 
                '<iframe src="'+src+'" width="'+content.width()+'" height="'+content.height()+'" onload="pb.spinner.hide()"/>'
             );
        }
    } else {
        pb.spinner.hide();
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
