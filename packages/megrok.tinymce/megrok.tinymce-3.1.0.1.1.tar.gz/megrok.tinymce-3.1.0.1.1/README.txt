megrok.tinymce: tinymce packaged for Grok
=========================================

This is a Grok extension that packages TinyMCE_, a Javascript HTML
WYSIWYG editor control.

.. _TinyMCE: http://tinymce.moxiecode.com/

Simply include ``megrok.tinymce`` as a dependency in your project's
``setup.py`` to make it available in your project.

To construct URLs to TinyMCE javascript libraries, use something like this::

  <script type="text/javascript"
    tal:attributes="src context/@@/TinyMCE/tiny_mce.js"></script>

Alternatively you can also declare that your template or Python code
needs the widget somewhere in the code path that's executed during the
display of the page. In a page template this looks like this::

  <tal:block replace="resource_library:TinyMCE"/>

In Python code you can do the following::

  from megrok.tinymce import TinyMCE
  
  def mywidgetcode():
     ...
     TinyMCE.need()
     ...
