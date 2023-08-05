# Release information about jquery

version = "1.1.2"

description = "Jquery javascript library for TurboGears"
long_description = """

Feature
===============

jquery is a jquery javascript library wrapper to minimize the duty of 
TurboGears web designer.

It contains 2 extra ajax widgets based on jquery.

  * link_to_remote(target ,update, href)
        
  * periodically_call_remote(update, href, interval)

Which are inspired from Ruby on Rails.

And it contains 2 extra widgets based on jqwebext.

  * zebra table

  * tabs

which are based on jqwebext, a jQuery simple MVC and plugins 
Components framework respected by Racklin
http://jqwebext.googlecode.com/ 


Available widgets
====================
* Jquery

  basic jquery libray wrapper for Turbogears

* link_to_remote()

* periodically_call_remote

* jqzebratable

  alternative line color 
  
* jqtabs

  head tabber

Install
==============
Use setuptools to install::
    
    $easy_install jquery


Usage
==============

jquery
~~~~~~~~~

include in config/app.cfg::

    tg.include_widgets = ['jquery.jquery']

jquery ajax
~~~~~~~~~~~~~

import in controllers.py::

    from jquery import link_to_remote
    from jquery import periodically_call_remote

    ....
    return dict(link_to_remote = link_to_remote(), periodically_call_remote = periodically_call_remote())


in template::
    
    <div id="timelink"><a href = "#">get time</a></div>
    <div id="timediv"></div>
    ${link_to_remote(target="timelink" ,update="timediv", href="/time")}
    
    or 

    <div id="timediv"></div>
    ${periodically_call_remote(update="timediv", href="/time", interval="3000")}

The link_to_remote/periodically_call_remote could be placed anywhere in your template.
Check http://docs.turbogears.org/1.0/RemoteLink for detail.


jqzebratable/jqtabs
~~~~~~~~~~~~~~~~~~~~~~

Take jqzebratable for example

1. include proper extension in config/app.cfg::

    tg.include_widgets = ['jquery.jqtabs']

    The proper javascripts will be included in all your templates
    
2. open the template to edit. check
    http://code.google.com/p/jqwebext/wiki/ZebraTableExtension 
    for detail

Reference
============
- jquery http://jquery.com
- jqwebext http://jqwebext.googlecode.com/


"""
author = "Fred Lin"
email = "gasolin+tg@gmail.com"
copyright = "Fred Lin 2007"

# if it's open source, you might want to specify these
# url = "http://yourcool.site/"
# download_url = "http://yourcool.site/download"
license = "MIT"
