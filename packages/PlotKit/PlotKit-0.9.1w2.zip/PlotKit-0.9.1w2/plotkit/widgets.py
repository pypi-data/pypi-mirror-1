import pkg_resources

from turbogears.widgets import CSSLink, CSSSource, JSLink, JSSource, Widget, WidgetDescription, \
                               register_static_directory, mochikit

js_dir = pkg_resources.resource_filename("plotkit",
                                         "static/javascript")
register_static_directory("plotkit", js_dir)

mochikit_js = mochikit
excanvas_js = JSLink("plotkit", "excanvas.js")
plotkit_packed_js = JSLink("plotkit", "PlotKit_Packed.js")

#related js
Base_js = JSLink("plotkit", "Base.js")
Canvas_js = JSLink("plotkit", "Canvas.js")
EasyPlot_js = JSLink("plotkit", "EasyPlot.js")
Layout_js = JSLink("plotkit", "Layout.js")
PlotKit_js = JSLink("plotkit", "PlotKit.js")
SVG_js = JSLink("plotkit", "SVG.js")
SweetCanvas_js = JSLink("plotkit", "SweetCanvas.js")
SweetSVG_js = JSLink("plotkit", "SweetSVG.js")

class PlotKit(Widget):
    """
    Provides an easy way to use PlotKit in your own packages.
    
    from plotkit import PlotKit,

    then return the PlotKit widget in the output
    
    dictionary from your controller.

    http://www.liquidx.net/plotkit/
    """
    javascript = [mochikit_js,
                  excanvas_js,
                  plotkit_packed_js]

class EasyPlot(PlotKit):
    """
    PlotKit.EasyPlot(style, options, divElement, datasourceArray)
    
    EasyPlot is a wrapper around the various PlotKit classes to allow you
    to get a chart plotted as quick as possible with as little code as possible.
    Using EasyPlot, you will get a chart started with just a single line.
    """
    template = """
    <div>
    <div id="${id}" style="margin: 0 auto 0 auto;" width="${width}" height="${height}"></div>
    <script type="text/javascript">
        var data = ${str(data)};
        var plotter = EasyPlot("${style}", ${str(option)}, $("${id}"), data);
    </script>
    </div>
    """
    
    params = ["id", "style", "width", "height", "data", "option"]
    params_doc = {'id' : 'Element id(string)',
                  'style' : 'style may be "line", "bar" or "pie".(string)',
                  'width' : 'Pic width(int)',
                  'height' : 'Pic height(int)',
                  'data' : 'an array of data sources(two dimensional list)',
                  'option': 'options of both Layout and Renderer(dictionary)'}
    id = 'diag'
    style = 'line'
    width = 400
    height = 400
    option = {}
    
class EasyPlotDesc(WidgetDescription):
    """
    http://www.liquidx.net/plotkit/
    """
    name = "EasyPlot"
    setA = [[0,0], [1,2], [2,3], [3,7], [4,8], [5,6]]
    setB = [[0,0], [1,1], [2,4], [3,8], [4,7], [5,8]]
    setC = [[0,1], [1,3], [2,5], [3,5], [4,3], [5,2]]
    data = [setA, setB, setC]
    
    option = """{"xTicks": [{v:0, label:"zero"},
                            {v:1, label:"one"},
                            {v:2, label:"two"},
                            {v:3, label:"three"},
                            {v:4, label:"four"},
                            {v:5, label:"five"}]}"""
    #EasyPlot(id="diag",style="line", width="300", height="300", data=data)
    #EasyPlot(option= option,data=data)
    for_widget = EasyPlot(data=data)
    
    
