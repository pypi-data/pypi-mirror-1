/*
 * Zebra Table Plugin for Site Ext
 *
 * Copyright (c) 2007 Rack Lin (racklin.blogsopt.com)
 * Dual licensed under the MIT (MIT-LICENSE.txt)
 * and GPL (GPL-LICENSE.txt) licenses.
 *
 * $Date: 2007-02-18 04:58:04 +0800 $
 * $Rev: 1 $
 */
jQWebExt.ZebraTable = function(opt) {

    for (var tableId in opt) {
        var qStrOdd = '#'+tableId + ' tr:nth-child(odd)';
        var qStrEven = '#'+tableId + ' tr:nth-child(even)'; 
        if(typeof(opt[tableId]['odd']) == 'string' && opt[tableId]['odd'].length>0) jQuery(qStrOdd).addClass(opt[tableId]['odd']);
        if(typeof(opt[tableId]['even']) == 'string' && opt[tableId]['even'].length>0) jQuery(qStrEven).addClass(opt[tableId]['even']);
    }

};

// Register Zebra Table Plugin
jQWebExt.register('ZebraTable' ,  {
        zebra: {even: 'even', odd: 'odd'}
});
