from flask import request, Response
from flask_appbuilder.api import BaseApi, expose
from flask_appbuilder.security.decorators import protect
from . import appbuilder, state_controller, klipper_connection

import json
import xml.etree.ElementTree as ET

import src.Widget as W
import src.MovementCommands as MC


def formatWidgetFromContent(contents:dict) -> W.Widget :
    try :
        pos_x = contents['pos_x']
        pos_y = contents['pos_y']
        svg = contents.get('svg')
        if svg != None : svg = ET.fromstring(svg)
        details = contents.get('details')

        if details == None or details['type'] == 'generic' :
            widget = W.Widget(pos_x, pos_y, svg)
        elif details['type'] == 'text' :
            widget = W.TextWidget(pos_x, pos_y, details)
        #elif contents['details']['type'] == '' : # :/ open/closed princliple yada yada
        #    widget = 
        else :
            return Response('type not supported', 400)

        return widget
    except :
        return Response("Must follow proper widget formatting details", 400)

class WidgetApi(BaseApi):

    route_base = ''

    @expose('/widgets', methods=['GET'])
    def getWidgets(self) :
        result = list()

        for key in state_controller.working :
            result.append(key.toJson())

        return result
    
    @expose('/widget', methods=['POST'])
    def addWidget(self) :
        widget = formatWidgetFromContent(request.get_json())
        if isinstance(widget,Response) : return widget

        state_controller.addWidget(widget)
        return widget.toJson()
    
    @expose('/widget', methods=['PUT'])
    def editWidget(self) :
        both:dict = request.get_json()
        if both.get('old') == None or both.get('new') == None : raise Exception("follow editwidget formatting", 400)
        
        old_widget = formatWidgetFromContent(both.get('old'))
        new_widget = formatWidgetFromContent(both.get('new'))

        state_controller.editWidget(old_widget, new_widget)
        return new_widget.toJson()

    @expose('/widget', methods=['DELETE'])
    def deleteWidget(self) :
        widget = formatWidgetFromContent(request.get_json())
        if isinstance(widget,Response) : return widget

        state_controller.deleteWidget(widget)
        return widget.toJson()
        
    @expose('/sync', methods=['GET','POST','PUT','DELETE'])
    def syncWidgets(self) :
        all_movement_commands = state_controller.syncronize()
        str_commands = list()
        for command in all_movement_commands :
            str_commands.append(command.__repr__() + "====" + command.toGcode()[1])
        return {"movement_commands" : str_commands}
    
    @expose('/revert', methods=['GET','POST','PUT','DELETE'])
    def revertWidgets(self) :
        state_controller.revert()
        result = list()
        for key in state_controller.working :
            result.append(key.toJson())

        return result

    



appbuilder.add_api(WidgetApi)