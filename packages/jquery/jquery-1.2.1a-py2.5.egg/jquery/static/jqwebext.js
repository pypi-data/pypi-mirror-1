/**
 * jQWebExt - jQuery Simple MVC and plugins Components framework
 *
 * Copyright (c) 2007 Rack Lin (racklin.blogsopt.com)
 * Dual licensed under the MIT (MIT-LICENSE.txt)
 * and GPL (GPL-LICENSE.txt) licenses.
 *
 * $Date: 2007-05-18 04:58:04 +0800 $
 * $Rev: 2 $
 */

// Using jQuery with Other Libraries
// try { jQuery.noConflict(); }catch (e) { }

/**
 * Create a new jQWebExt Object
*/
var jQWebExt = {};
jQuery.extend( jQWebExt, {

        version: '0.2.1',

        /**
         * The registed extension  elements
         */
        extensions: [],

        /**
         * The registed extension options elements
         */
        options: {},

        /**
         * Register extension to jQWebExt framework
         *
         * name = extension name
         * opts = extension default options
         */
        register: function(name, opts) {
            if (typeof (opts) == 'undefined') opts ={};
            jQWebExt.extensions.push(name);
            if (typeof (jQWebExt.options[name]) == 'undefined') jQWebExt.options[name] = opts;
            else jQuery.extend( jQWebExt.options[name], opts );
        },

        /**
         * When DOM ready run extensions and call extension's register function.
         */
        process: function() {
            jQuery(document).ready( function(){
                jQuery(jQWebExt.extensions).each( function() {
                    var name = this;
                    if ( typeof(jQWebExt[name]) == 'function') {
                        try { jQWebExt[name](jQWebExt.options[name]); }catch(e){}
                    }
                });
            });
        },

        /**
         * Include third-party Javascript source
         *
         * jsName = javascript src file
         */
        require: function(jsName) {
            var path = jQWebExtConfig.path;
            var isIncluded = false;
            jQuery('script').each(function(idx) {
                var s = this;
                if(s.src.match(/jqwebext[\.pack]*\.js$/)) {
                  if(path.length == 0) path = s.src.replace(/jqwebext[\.pack]*\.js$/,'');
                }
                if(s.src.match(jsName)) isIncluded = true;
            });
            if (!isIncluded) {
              if(jQuery.isReady) {
                // DOM is already ready
                var s=document.createElement('script');
                s.src = path+jsName;
                s.type = 'text/javascript';
                jQuery('head',document).append( s );
              }else {
                document.write('<scr'+'ipt type="text/javascript" src="'+path+jsName+'"></scr'+'ipt>');
              }
            }
        },

        /**
         * create Remote JSON with callback
         */
         createJSON: function (url, callback) {

            var id = (new Date).getTime();
            var name = 'json_' + id;

            if(typeof(callback) != 'undefined') {
                var cb = function( json ) {
                    eval( 'delete ' + name );
                    // remove script element , ie6 will crash.
                    if(!jQuery.browser.msie) jQuery('script#'+id).remove();
                    callback.call(this, json);
                };
                url = url.replace(/{callback}/, name);
                eval( name + ' = cb' );
            }
            if(jQuery.isReady) {
              // DOM is already ready
              var s=document.createElement('script');
              s.src = url;
              s.type = 'text/javascript';
              s.id = id;
              jQuery('head',document).append( s );
            }else {
              document.write('<scr'+'ipt type="text/javascript" src="'+url+'" id="'+id+'"></scr'+'ipt>');
            }
         }
});

if (typeof(jQWebExtConfig) == 'undefined') {
		var jQWebExtConfig = {config: 'jqwebext_config.js', path: '', pageId: ''};
}

// jQWebExt MVC Config
jQWebExt.options.Config = {};
jQuery.extend( jQWebExt, {

  Config: function () {

    var options = jQWebExt.options.Config;

    var pageId = '';

    // use body id
    if(typeof jQuery('body').attr('id') != 'undefined') pageId = jQuery('body').attr('id');
    // use script options
    if(typeof jQWebExtConfig.pageId != 'undefined' && jQWebExtConfig.pageId != '') pageId = jQWebExtConfig.pageId;

    var pageIds =  (pageId + ',default').split(',');

    for (var i in pageIds) {

      var pid = pageIds[i];
      if(pid.length ==0) continue;

      // initial config and register ready function
      if(typeof options[pid] != 'undefined' ) {
        var config  = options[pid];

        // require javascripts
        if(typeof config['requires'] != 'undefined') {
          jQuery(config['requires'].split(',')).each(function() {
            var js = jQuery.trim(this);
            if(js.length > 0) jQWebExt.require(js);
          });
        }

        // register functions to window
        if(typeof config['functions'] != 'undefined') {
            jQuery.extend(window,  config['functions']);
        }

        // register ready function
        if (typeof config['ready'] != 'undefined' && typeof config['ready'] == 'function' ) {
          jQuery(document).ready(config['ready']);
        }
      }

    }

  }
});

try {
    // try require jQWebExtConfig first if exists
    jQWebExt.require(jQWebExtConfig.config);

    // Run All Register Process
    jQWebExt.process();
}catch (e) {
}