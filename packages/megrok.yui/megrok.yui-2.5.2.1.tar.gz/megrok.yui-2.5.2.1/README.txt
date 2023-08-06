megrok.yui: YUI packaged for Grok
=================================

This is a Grok extension that packages YUI (the Yahoo User Interface
Library) for Grok. Simply include ``megrok.yui`` as a dependency in
your project's ``setup.py`` to make it available.

To construct URLs to YUI javascript libraries, use something like this::

  <script type="text/javascript"
    tal:attributes="src context/@@/YUI/menu/menu.js"></script>

To construct URLs to YUI css libraries, use something like this::

   <link rel="stylesheet" type="text/css" 
      tal:attributes="href context/@@/YUI/reset/reset.css" />
