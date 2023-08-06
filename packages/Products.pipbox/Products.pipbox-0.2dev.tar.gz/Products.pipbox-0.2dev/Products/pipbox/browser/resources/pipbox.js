/*****************

   PIPbox tools for attaching JQuery Tools bling to CSS with option
   parameter strings.

*****************/


// Name space object for pipbox
pb = {};
// We may be creating multiple targets per page. We need to be able to 
// tell them apart. We'll do it by counting.
pb.overlay_counter = 1;


/******
    jQuery.fn.prepOverlay
    JQuery plugin to inject overlay target into DOM
******/
jQuery.fn.prepOverlay = function(pbo) {
    return this.each( function(){
        var o = jQuery(this);
        // if there's an rel attribute, we've already
        // visited this node.
        if (! o.attr('rel')) {
            var nt = 'pb_' + pb.overlay_counter;
            var src = o.attr('href') || o.attr('src');
            var el = jQuery(
                '<div id="' + nt + '" class="overlay pb-'+pbo.subtype+'" />'
                );

            if (pbo.urlmatch) {
                src = src.replace(RegExp(pbo.urlmatch), pbo.urlreplace);
            }

            el.append('<a href="'+src+'" />');
            o.after(el).attr('rel', '#' + nt);
            o.addClass('pboverlay');

            if (pbo.width) {
                el.width(pbo.width);
            }
            if (pbo.height) {
                el.height(pbo.height);
            }

            pb.overlay_counter += 1;
        }
    });
};

/******
    pb.image
    onBeforeLoad handler for image overlays
******/
pb.image = function () {
      var content = this.getContent();
      var wrap = content.find("a"); 
      if (wrap.length) {
          src = wrap.attr('href');
          var el = jQuery('<img src="'+src+'" />');
          wrap.replaceWith( el );
          // Should work in next version of JQT.
          // content.width(el[0].width);
          // content.height(el[0].height);
      }
  return true;
}


/******
    pb.ajax
    onBeforeLoad handler for ajax overlays
******/
pb.ajax = function () {
      var content = this.getContent();
      var wrap = content.find("a"); 
      if (wrap.length) {
          src = wrap.attr('href');
          var el = jQuery('<div class="pbajax" />').load(src);
          wrap.replaceWith( el );
      }
  return true;
}


/******
    pb.iframes
    onBeforeLoad handler for iframe overlays
******/
pb.iframe = function () {
      var content = this.getContent();
      var wrap = content.find("a"); 
      if (wrap.length) {
          src = wrap.attr('href');
          var el = jQuery(
              '<iframe src="'+src+'" width="'+content.width()+'" height="'+content.height()+'" />'
              );
          wrap.replaceWith( el );
      }
  return true;
}


/******
    pb.setup
    setup jqt inits
******/
pb.setup = function(p) {
    switch (p.type) {
        case 'overlay' :
            jQuery(function() {
                var config = p.config || {};
                config.onBeforeLoad = pb[p.subtype];
                jQuery(p.selector).prepOverlay(p)
                jQuery('.pboverlay').removeClass('pboverlay').overlay(config).css('cursor', 'pointer');
            });
            break;
    }
}


/******
    pb.doSetup
    parameter: an options object(s)
    options vary by type and subtype of bling.
******/
pb.doSetup = function(s) {
    var plist = s;
    // var plist = eval ('("'+s+'")');
    
    if (! (plist instanceof Array)) {
        plist = [plist];
    }
    for (var i=0;i<plist.length;i++) {
        var p = plist[i];
        pb.setup(p);
    }
    
}
