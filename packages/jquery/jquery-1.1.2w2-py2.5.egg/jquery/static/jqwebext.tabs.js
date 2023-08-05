/*
 * jQuery tabs plugins Plugin for Site Ext
 *
 * Copyright (c) 2007 Rack Lin (racklin.blogsopt.com)
 * Dual licensed under the MIT (MIT-LICENSE.txt)
 * and GPL (GPL-LICENSE.txt) licenses.
 *
 * $Date: 2007-02-18 04:58:04 +0800 $
 * $Rev: 1 $
 */
// include jQuery tabs js
//jQWebExt.require('plugins/jquery.tabs.pack.js');

jQWebExt.Tabs = function(opt) {
    for (var tabsId in opt) {    
        var qStr = '#'+tabsId;
        jQuery(qStr).tabs(opt[tabsId]);
    }
};

// Register Zebra Table Plugin
jQWebExt.register('Tabs' ,  {
        'tabs-container': 1
});
