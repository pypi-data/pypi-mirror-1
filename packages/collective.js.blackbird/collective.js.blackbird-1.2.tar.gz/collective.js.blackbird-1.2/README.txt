Introduction
============

Blackbird is an open source javascript logging facility written by G Scott
Olson and released under the MIT License.

Please read Scott's website for instructions on how to use the logging
functionality.

Web: http://blackbirdjs.googlecode.com/
     http://www.gscottolson.com/blackbirdjs/

This Plone compatibility egg provides the following functionality:
    
*   Registers the JS file Blackbird.js in portal_javascripts. This file will only
    be loaded if your portal_javascripts tool is in debug mode.

*   Additionally I've added another file Blackbird_disabled.js that is loaded when
    portal_javascripts is *not* in debug mode and which overrides Blackbird's 'log'
    namespace with empty functions. This allows you to safely leave log statements 
    in your javascript even though Blackbird.js is not being loaded.

*   Registers Blackbird.css to style the logging prompt.

*   Registers a viewlet for IBelowContent that enables you to toggle the logging prompt's visibility and position.
