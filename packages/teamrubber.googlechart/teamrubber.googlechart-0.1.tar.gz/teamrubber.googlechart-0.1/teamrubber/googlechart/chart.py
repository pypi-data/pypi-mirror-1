""" Google Chart """

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Globals import DTMLFile
from Acquisition import Implicit, aq_base
from Globals import Persistent
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from OFS.Folder import Folder
from OFS.PropertyManager import PropertyManager
from App.Common import package_home
from AccessControl.Role import RoleManager
from Products.PythonScripts.standard import url_quote
from Products.PythonScripts.standard import url_unquote

import urllib

from pygooglechart import *

def addChart(self, id, title='', cid=997, REQUEST=None):
    """ Add ZGoogleChart Instance """
    ob = ZGoogleChart(id)
    ob.title = str(title)

    new_properties = ob.get_fields()

    #Automagic property addition
    for property in new_properties:
        # Workaround for strange Zope behaviour.
        # And it works! Yey!
        if property[2] == 'selection' or property[2] == "multiple selection":
            ob._properties=ob._properties + ({'id':property[0],'type':property[2],'select_variable':property[1]},)
            if property[2] == 'selection':
                ob._setPropValue(property[0],'')
            else:
                ob._setPropValue(property[0],[])
        else:
            # Normal un-strange property adding behaviour.
            # I'm really not sure why this is needed?
            ob.manage_addProperty(property[0],property[1],property[2])

    ob.manage_changeProperties(background_fill='None')
    ob.manage_changeProperties(chart_fill='None')
    id = self._setObject(id, ob)

    if REQUEST is not None:
        try:
          u=self.DestinationURL()
        except:
          u=REQUEST['URL1']
        REQUEST.RESPONSE.redirect(u+'/manage_main')
        
manage_addChart = DTMLFile('dtml/teamrubber_googlechartAdd', globals())

class ZGoogleChart(SimpleItem,PropertyManager):
    """ ZGoogleChart """

    meta_type = 'GoogleChart'
    security = ClassSecurityInfo()
    manage_options=PropertyManager.manage_options

    def __init__(self, id):
		self.id = id


    def get_fields_list(self):
		""" Get fields as a list of dicts """
		fields = self.get_fields()
		result = []
		for field in fields:
		    next_dict = {'name':field[0],'default_value':field[1],'type':field[2],'nice_name':field[3]}
		    result.append(next_dict)
		return result

    security.declarePrivate('get_fields')
    def get_fields(self):
        """ Get Fields, Titles and other info """
        return [
			# ZGoogleChart specific fields
			("width",300,"int","Width",""),
			("height",300,"int","Height"),
            ("colours",["FFF2CC"],"lines","Colours"),
            ("grid_x",0,"int","Grid X Size"),
            ("grid_y",0,"int","Grid Y Size"),
            ("grid_line",0,"int","Grid Line Size"),
            ("grid_blank",0,"int","Grid Blank Size"),
            ("background_fill","colour_fill_values","selection","Background Fill"),
            ("chart_fill","colour_fill_values","selection","Chart Fill"),
            ("background_solid_fill", "","string","Background Solid Fill"),
            ("chart_solid_fill", "","string","Chart Solid Fill"),
            ("bkgd_linear_gradient_colour", "","lines","Background Linear Gradient Colour"),
            ("bkgd_linear_gradient_angle", "angle_values","selection","Background Linear Gradient Angle"),
            ("bkgd_linear_gradient_offset", [],"lines","Background Linear Gradient Offset"),
            ("chrt_linear_gradient_colour", "","lines","Chart Linear Gradient Colour"),
            ("chrt_linear_gradient_angle", "angle_values","selection","Chart Linear Gradient Angle"),
            ("chrt_linear_gradient_offset", [],"lines","Chart Linear Gradient Offset"),
            ("bar_spacing",0,"int","Bar Chart Spacing"),
            ("bar_width",0,"int","Bar Chart Width"),
            #("colour_fill_values",["None","Solid", "Linear Gradient", "Linear Stripes"],"lines","Colour Fill Values")
			]

    #####################
    # Chart Functions
    #####################

    def angle_values(self):
        """ get angle values """
        return [str(a) for a in range(0,91)]

    def colour_fill_values(self):
        """ get fill values """
        return ["None","Solid", "Linear Gradient", "Linear Stripes"]

    def background_fill_function(self, chart):
        """ set background fill """
            
        if self.background_fill == "Solid":
            chart.fill_solid(Chart.BACKGROUND, self.background_solid_fill)
        elif self.background_fill == "Linear Gradient":
            chart.fill_linear_gradient(Chart.BACKGROUND,int(self.bkgd_linear_gradient_angle), str(self.bkgd_linear_gradient_colour), float(self.bkgd_linear_gradient_offset))
        elif self.background_fill == "Linear Stripes":
            chart.fill_linear_stripes(Chart.BACKGROUND,int(self.bkgd_linear_gradient_angle), str(self.bkgd_linear_gradient_colour), float(self.bkgd_linear_gradient_offset))
        return chart

    def chart_fill_function(self, chart):
        """ set chart fill """
        if self.chart_fill == "Solid":
            chart.fill_solid(Chart.CHART, self.chart_solid_fill)
        elif self.chart_fill == "Linear Gradient":
            chart.fill_linear_gradient(Chart.CHART,int(self.chrt_linear_gradient_angle), str(self.chrt_linear_gradient_colour), float(self.chrt_linear_gradient_offset))
        elif self.chart_fill == "Linear Stripes":
            chart.fill_linear_stripes(Chart.CHART,int(self.chrt_linear_gradient_angle), str(self.chrt_linear_gradient_colour), float(self.chrt_linear_gradient_offset))
        return chart

    def getSimpleLineChart(self,data,x_label='', y_label='', show_legends=True, x_range=None, y_range=None,width=0, height=0, colours=None):
        """ create the link to a simple line chart """
        if width == 0:
            width = self.width
        if height == 0:
            height = self.height
                        
        chart = SimpleLineChart(width=width, height=height)
        
        legends = data.keys()
        
        if legends and show_legends:
            chart.set_legend(map(str, legends))
        if colours:
            chart.set_colours(colours)
        else:
            chart.set_colours(self.colours)
            
        if x_label:
            chart.set_axis_labels(Axis.LEFT,x_label)
        if y_label:
            chart.set_axis_labels(Axis.BOTTOM,y_label)    

        if x_range:
            chart.set_axis_range(Axis.LEFT,x_range[0],x_range[1])
        if y_range:
            chart.set_axis_range(Axis.BOTTOM,y_range[0],y_range[1])
                        
        chart = self.background_fill_function(chart)
        chart = self.chart_fill_function(chart)
        
    
        for key in legends:
            chart.add_data(data[key])
            
        return chart.get_url()

    def getGroupedVerticalBarChart(self,data,x_label='', y_label='', bar_spacing=None, show_legends=True, x_range=None, y_range=None,width=0, height=0, colours=None):
        """ create the link to a grouped vertical bar chart """
        if width == 0:
            width = self.width
        if height == 0:
            height = self.height
                        
        chart = GroupedVerticalBarChart(width=width, height=height)
        
        if bar_spacing:
            chart.set_bar_spacing(bar_spacing)
        else:
            chart.set_bar_spacing(self.bar_spacing)
        
        legends = data.keys()
        
        if legends and show_legends:
            chart.set_legend(legends)
        if colours:
            chart.set_colours(colours)
        else:
            chart.set_colours(self.colours)
            
        if x_label:
            chart.set_axis_labels(Axis.LEFT,x_label)
        if y_label:
            chart.set_axis_labels(Axis.BOTTOM,y_label)    

        if x_range:
            chart.set_axis_range(Axis.LEFT,x_range[0],x_range[1])
        if y_range:
            chart.set_axis_range(Axis.BOTTOM,y_range[0],y_range[1])
                        
        chart = self.background_fill_function(chart)
        chart = self.chart_fill_function(chart)
            
        for key in legends:
            chart.add_data(data[key])
            
        return chart.get_url()

    def getStackedHorizontalBarChart(self,data,x_label='', y_label='', bar_width=None, show_legends=True, x_range=None, y_range=None,width=0, height=0, colours=None):
        """ create the link to a stacked vertical bar chart """
        if width == 0:
            width = self.width
        if height == 0:
            height = self.height
                        
        chart = StackedHorizontalBarChart(width=width, height=height)
        
        if bar_width:
            chart.set_bar_width(bar_width)
        else:
            chart.set_bar_width(self.bar_width)
        
        legends = data.keys()
        
        if legends and show_legends:
            chart.set_legend(legends)
        if colours:
            chart.set_colours(colours)
        else:
            chart.set_colours(self.colours)
            
        if x_label:
            chart.set_axis_labels(Axis.LEFT,x_label)
        if y_label:
            chart.set_axis_labels(Axis.BOTTOM,y_label)    

        if x_range:
            chart.set_axis_range(Axis.LEFT,x_range[0],x_range[1])
        if y_range:
            chart.set_axis_range(Axis.BOTTOM,y_range[0],y_range[1])
                        
        chart = self.background_fill_function(chart)
        chart = self.chart_fill_function(chart)
            
        for key in legends:
            chart.add_data(data[key])
            
        return chart.get_url()

    def getStackedVerticalBarChart(self,data,x_label='', y_label='', bar_width=None, show_legends=True, x_range=None, y_range=None,width=0, height=0, colours=None):
        """ create the link to a stacked vertical bar chart """
        if width == 0:
            width = self.width
        if height == 0:
            height = self.height
                        
        chart = StackedVerticalBarChart(width=width, height=height)
        
        if bar_width:
            chart.set_bar_width(bar_width)
        else:
            chart.set_bar_width(self.bar_width)
        
        legends = data.keys()
        
        if legends and show_legends:
            chart.set_legend(legends)
        if colours:
            chart.set_colours(colours)
        else:
            chart.set_colours(self.colours)
            
        if x_label:
            chart.set_axis_labels(Axis.LEFT,x_label)
        if y_label:
            chart.set_axis_labels(Axis.BOTTOM,y_label)    

        if x_range:
            chart.set_axis_range(Axis.LEFT,x_range[0],x_range[1])
        if y_range:
            chart.set_axis_range(Axis.BOTTOM,y_range[0],y_range[1])
                        
        chart = self.background_fill_function(chart)
        chart = self.chart_fill_function(chart)
            
        for key in legends:
            chart.add_data(data[key])
            
        return chart.get_url()

    def getGroupedHorizontalBarChart(self,data,x_label='', y_label='', bar_spacing=None, show_legends=True, x_range=None, y_range=None,width=0, height=0, colours=None):
        """ create the link to a grouped horizontal bar chart """
        if width == 0:
            width = self.width
        if height == 0:
            height = self.height
                        
        chart = GroupedHorizontalBarChart(width=width, height=height)
        
        if bar_spacing:
            chart.set_bar_spacing(bar_spacing)
        else:
            chart.set_bar_spacing(self.bar_spacing)
        
        legends = data.keys()
        
        if legends and show_legends:
            chart.set_legend(legends)
        if colours:
            chart.set_colours(colours)
        else:
            chart.set_colours(self.colours)
            
        if x_label:
            chart.set_axis_labels(Axis.LEFT,x_label)
        if y_label:
            chart.set_axis_labels(Axis.BOTTOM,y_label)    

        if x_range:
            chart.set_axis_range(Axis.LEFT,x_range[0],x_range[1])
        if y_range:
            chart.set_axis_range(Axis.BOTTOM,y_range[0],y_range[1])
                        
        chart = self.background_fill_function(chart)
        chart = self.chart_fill_function(chart)
        
    
        for key in legends:
            chart.add_data(data[key])
            
        return chart.get_url()

    def getPieChart3D(self,data,show_legends=True, width=0, height=0, colours=None):
        """ create the link to a 3D Pie chart """
        if width == 0:
            width = self.width
        if height == 0:
            height = self.height
        
        chart = PieChart3D(width=width, height=height)

        legends = data.keys()
        
        if legends and show_legends:
            chart.set_pie_labels(legends)
        if colours:
            chart.set_colours(colours)
        else:
            chart.set_colours(self.colours)
            
         
        chart = self.background_fill_function(chart)
        chart = self.chart_fill_function(chart)
    
        for key in legends:
            chart.add_data(data[key])
            
        return chart.get_url()

    def getPieChart2D(self,data,show_legends=True, width=0, height=0, colours=None):
        """ create the link to a 2D Pie chart """
        if width == 0:
            width = self.width
        if height == 0:
            height = self.height
        
        chart = PieChart2D(width=width, height=height)

        legends = data.keys()
        
        if legends and show_legends:
            chart.set_pie_labels(legends)
        if colours:
            chart.set_colours(colours)
        else:
            chart.set_colours(self.colours)
            
         
        chart = self.background_fill_function(chart)
        chart = self.chart_fill_function(chart)
    
        for key in legends:
            chart.add_data(data[key])
            
        return chart.get_url()

    def getVennChart(self,data,show_legends=True, width=0, height=0, colours=None):
        """ create the link to a venn chart """
        if width == 0:
            width = self.width
        if height == 0:
            height = self.height
        
        chart = VennChart(width=width, height=height)

        legends = data.keys()
        
        if legends and show_legends:
            chart.set_legend(legends)
        if colours:
            chart.set_colours(colours)
        else:
            chart.set_colours(self.colours)
            
         
        chart = self.background_fill_function(chart)
        chart = self.chart_fill_function(chart)
    
        for key in legends:
            chart.add_data(data[key])
            
        return chart.get_url()


    def getScatterChart(self,data,x_label='',y_label='',show_legends=True, x_range=None, y_range=None, width=0, height=0, colours=None):
        """ create the link to a scatter graph """
        if width == 0:
            width = self.width
        if height == 0:
            height = self.height
        
        chart = ScatterChart(width=width, height=height)

        legends = data.keys()
        
        if legends and show_legends:
            chart.set_legend(legends)
        if colours:
            chart.set_colours(colours)
        else:
            chart.set_colours(self.colours)
            
        if x_label:
            chart.set_axis_labels(Axis.LEFT,x_label)
        if y_label:
            chart.set_axis_labels(Axis.BOTTOM,y_label)    

        if x_range:
            chart.set_axis_range(Axis.LEFT,x_range[0],x_range[1])
        if y_range:
            chart.set_axis_range(Axis.BOTTOM,y_range[0],y_range[1])
                        
        chart = self.background_fill_function(chart)
        chart = self.chart_fill_function(chart)
    
        for key in legends:
            chart.add_data(data[key])
            
        return chart.get_url()
        

    #Not working yet
    def getXYLineChart(self,data,x_label='', y_label='', show_legends=True, x_range=None, y_range=None,width=0, height=0, colours=None):
        """ create the link to a XY line chart """
        if width == 0:
            width = self.width
        if height == 0:
            height = self.height
                        
        chart = XYLineChart(width=width, height=height)
        
        legends = data.keys()
        
        if legends and show_legends:
            chart.set_legend(legends)
        if colours:
            chart.set_colours(colours)
        else:
            chart.set_colours(self.colours)
            
        if x_label:
            chart.set_axis_labels(Axis.LEFT,x_label)
        if y_label:
            chart.set_axis_labels(Axis.BOTTOM,y_label)    

        if x_range:
            chart.set_axis_range(Axis.LEFT,x_range[0],x_range[1])
        if y_range:
            chart.set_axis_range(Axis.BOTTOM,y_range[0],y_range[1])
                        
        for key in legends:
            chart.add_data(data[key])
            
        return chart.get_url()

InitializeClass(ZGoogleChart)
