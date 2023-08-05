/*
 * jQuery tooltip plugins Plugin for jQWeb Ext
 *
 * Copyright (c) 2007 Rack Lin (racklin.blogsopt.com)
 * Dual licensed under the MIT (MIT-LICENSE.txt)
 * and GPL (GPL-LICENSE.txt) licenses.
 *
 * $Date: 2007-02-18 04:58:04 +0800 $
 * $Rev: 1 $
 */
// include jQuery tooltip js
jQWebExt.require('plugins/jquery.tooltip.pack.js');

jQWebExt.Tooltip = function(opt) {
    for (var selector in opt) {
        jQuery(selector).Tooltip(opt[selector]);
    }
};

// Register Tooltip Plugin
jQWebExt.register('Tooltip' ,  {'*[@title]':''});
