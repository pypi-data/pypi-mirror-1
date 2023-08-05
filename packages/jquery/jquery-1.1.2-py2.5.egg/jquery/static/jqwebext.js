/*
 * jQWebExt - jQuery Simple MVC and plugins Components framework
 *
 * Copyright (c) 2007 Rack Lin (racklin.blogsopt.com)
 * Dual licensed under the MIT (MIT-LICENSE.txt)
 * and GPL (GPL-LICENSE.txt) licenses.
 *
 * $Date: 2007-02-18 04:58:04 +0800 $
 * $Rev: 1 $
 */

// Using jQuery with Other Libraries
// try { jQuery.noConflict(); }catch (e) { }

/**
 * Create a new jQWebExt Object
*/
var jQWebExt = {};
jQuery.extend( jQWebExt, {
 
        version: '0.1.1', 

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
            jQWebExt.options[name] =  opts;
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
            var path = '';
            var isIncluded = false;
            jQuery('script').each(function(idx) {
                var s = this;
                if(s.src.match(/jqwebext\.js$/)) path = s.src.replace(/jqwebext\.js$/,'');
                if(s.src.match(jsName)) isIncluded = true;
            });
            if (!isIncluded) {
                document.write('<script type="text/javascript" src="'+path+jsName+'"></script>');
            }
        }
});

try {
    // Run All Register Process
    jQWebExt.process();
}catch (e) {
}
