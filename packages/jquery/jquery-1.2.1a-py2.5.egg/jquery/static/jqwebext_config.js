// jQWebExt Config
jQWebExt.options.Config = {

  /*
   * Default config will process at any page id.
   */
  'default': {
    /*
     * Require third party's javascript, separate with comma
     */
    'requires': 'plugins/jquery.dimensions.pack.js',

    /*
     * Register global functions
     */
    'functions': {
        test: function() {
            alert('cool! test function in jqwebext_config.js');
        }
    },

    /*
     * Auto Run on DOM Ready.
     * Like jQuery(document).ready( function ...)
     */
    'ready': function () {
      alert('dom ready function in jqwebext_config.js DEFAULT Block');
    }

  },

  /*
   * pageId or Body id="helloworld"
   */
  'helloworld': {
     'ready': function () {
        alert('dom ready function in jqwebext_config.js helloworld Block');
     }
  },

  /*
   * pageId or Body id="tooltip"
   */
  'tooltip': {
    'requires': 'jqwebext.tooltip.js',
    'ready': function () {
        alert('dom ready function in jqwebext_config.js!! \n is Tooltip page?? cool!!!');
     }
  }

};
// callback jQWebExt to process Config.
jQWebExt.Config();