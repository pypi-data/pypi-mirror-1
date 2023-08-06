collective.kss.inlinejs
=======================

If you want to use external js libraries with kss you may have to write a kss plugin (for example create a jQuery porting of some features).
When it makes sense you can also use this package and put simple inline javascript code that will be executed.

You can call javascript code from the inlinejs kss command set or configure properly a kss configuration file.


Example usage
-------------

From python code:

element = ksscore.getHtmlIdSelector('selector')
inline = self.getCommandSet("inlinejs")
inline.execJs(element, "alert('TEST'); alert(node.id); jQuery(...)")

From a kss configuration file:

img:click {
    action-client: inlinejs-effect;
    inlinejs-effect-code: 'alert(node.id); alert("done"); jQuery(...)';
    inlinejs-effect-debug: '1';
    }

TODO
----

* Tests coverage


Author
======

- Davide Moro <davide.moro@redomino.com>

