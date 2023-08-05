# Release information about jquery

version = "1.1.2w2"

description = "Jquery javascript library for TurboGears"
long_description = """

Feature
===============

jquery is a jquery javascript library wrapper and ajax helper for happy
TurboGears web designers.

It contains 3 extra ajax widgets based on jquery.

  * addCallback / link_to_remote(target ,update, href, callback)
        
  * addPeriodBack / periodically_call_remote(update, href, interval)

  * addFormback / form_remote_tag(target, update, href)

Which are inspired from Ruby on Rails/pquery and give them the twisted syntax.


Available widgets
====================

    * Jquery (basic jquery libray wrapper for Turbogears)

    * addCallback/link_to_remote

    * addPeriodBack/periodically_call_remote

    * addFormback/form_remote_tag
    
    * jqzebratable (alternative line color)
      
    * jqtabs (head tabber)

.. note:: 
    Update notice form 1.1.2 jquery widget: you need return dict(link = link_to_remote) instead of 
    return dict(link = link_to_remote()) in the following versions


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

    from jquery import addCallback
    from jquery import addPeriodback
    from jquery import addFormback
    ....
    return dict(addCallback = addCallback, 
            addPeriodback = addPeriodback)


in template::
    
    <div id="timelink"><a href = "#">get time</a></div>
    <div id="timediv"></div>
    ${addCallback(target="timelink" ,update="timediv", href="/time")}
    
or::

    <div id="timediv"></div>
    ${addPeriodback(update="timediv", href="/time", interval="3000")}

or 

    <form class="timelink" action="ajax"  method="get" >
       Field : <input type="text" name="field" /><br />
       <input type="submit" /> 
    </form>
    <div id="timediv"></div>
    ${addFormback(target="timelink", update="timediv", href="ajax")}

The addCallback/addPeriodback(link_to_remote/periodically_call_remote) could be placed anywhere in your template.
Check http://docs.turbogears.org/1.0/RemoteLink for detail.


jqzebratable/jqtabs
~~~~~~~~~~~~~~~~~~~~~~

This extension also contains 2 extra fancy widgets:

  * zebra table

  * tabs

which are based on jqwebext, a jQuery simple MVC and plugins 
Components framework respected by Racklin.

Take jqzebratable for example

1. include proper extension in config/app.cfg::

    tg.include_widgets = ['jquery.jqtabs']

    The proper javascripts will be included in all your templates
    
2. open the template to edit. check
   http://code.google.com/p/jqwebext/wiki/ZebraTableExtension for detail

Reference
============

    - jquery 1.1.2 http://jquery.com
    - jqwebext 0.2.1 http://jqwebext.googlecode.com/
    - pquery http://www.ngcoders.com/pquery/

History
=============
1.1.2w2: 

* new twisted style ajax call
* new addFormback/form_remote_tag call
* passing ajax function no need extra '()' at all.


"""
author = "Fred Lin"
email = "gasolin+tg@gmail.com"
copyright = "Fred Lin 2007"

# if it's open source, you might want to specify these
# url = "http://yourcool.site/"
# download_url = "http://yourcool.site/download"
license = "MIT"
