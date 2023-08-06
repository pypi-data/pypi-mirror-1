"""this is a TurboGears widget for using CurvyCorners
easily.
http://www.curvycorners.net
"""
import pkg_resources
import pkg_resources
from turbogears.widgets import JSLink, Widget, WidgetDescription, \
                               register_static_directory

js_dir = pkg_resources.resource_filename(
        "curvycorners",
        'static/javascript')

register_static_directory("curvycorners", js_dir)

curvycorners_js = JSLink("curvycorners", "rounded_corners_lite.inc.js")

class CurvyCorners(Widget):
    """Provides an easy way to use CurvyCorners in your own
    packages.  Exemple:

    from tgcurvycorners import curvycorners
    return dict(jswidget=curvycorners)

    and in your template:

    <span py:strip="True" py:content="jswidget.display()" />

    to get the javascript included. For a detailed usage please
    look at the documentation of the project:

    http://www.curvycorners.net/usage.php

    for a quick and dirty way to use it, insert the following
    code in your html>head:

    ==========================================================
    <script type="text/JavaScript">
      window.onload = function()
      {
        settings = {
          tl: { radius: 20 },
          tr: { radius: 20 },
          bl: { radius: 20 },
          br: { radius: 20 },
          antiAlias: true,
          autoPad: true
        }

        var divObj = document.getElementById("__THEDIVID__");

        var cornersObj = new curvyCorners(settings, divObj);
        cornersObj.applyCornersToAll();
      }
    </script>
    ==========================================================

    make sure you write a real function this is just a dirty
    demo. And make sure you replace "__THEDIVID__" by some real
    div id you want to apply the round corners to.
    """
    javascript = [curvycorners_js]

curvycorners = CurvyCorners()

class CurvyCornersDesc(WidgetDescription):
    for_widget = curvycorners
    template = """
    <div>
    <script type="text/JavaScript">
      function curveit(){
        settings = {
          tl: { radius: 20 },
          tr: { radius: 20 },
          bl: { radius: 20 },
          br: { radius: 20 },
          antiAlias: true,
          autoPad: true
        }

        var divObj = document.getElementById("demodiv");

        var cornersObj = new curvyCorners(settings, divObj);
        cornersObj.applyCornersToAll();
      }
    </script>
    <div id="demodiv" onclick="curveit()" style="border:1px solid #000; min-height: 100px; background-color: #ddddee;">
      <p>
        Click on this box to see it get round corners...
      </p>
      <p>
        The effect may not be pretty but it proves that it works.
      </p>
      <p>
        For some really cool demos of CurvyCorners please look
        <a href="http://www.curvycorners.net/">at their website</a>
      </p>
    </div>
    </div>
    """
    show_separately = True
    
