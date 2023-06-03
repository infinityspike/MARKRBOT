from flask import request, Response
from flask_appbuilder.api import BaseApi, expose
from flask_appbuilder.security.decorators import protect
from . import appbuilder, state_controller, klipper_connection

import json
import xml.etree.ElementTree as ET

import src.Widget as W
import src.MovementCommands as MC


def formatWidgetFromRequest() -> W.Widget :
    try :
        contents:dict = request.get_json()
        
        pos_x = contents['pos_x']
        pos_y = contents['pos_y']
        svg = ET.fromstring(contents.get('svg'))
        details = contents.get('details')

        if details == None :
            widget = W.Widget(pos_x, pos_y, svg, details)
        elif contents['details']['type'] == 'text' :
            widget = W.TextWidget(pos_x, pos_y, details, svg)
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
        widget = formatWidgetFromRequest()
        if isinstance(widget,Response) : return widget

        state_controller.addWidget(widget)
        return widget.toJson()

    @expose('/widget', methods=['DELETE'])
    def deleteWidget(self) :
        widget = formatWidgetFromRequest()
        if isinstance(widget,Response) : return widget

        state_controller.deleteWidget(widget)
        return widget.toJson()
        
    @expose('/sync', methods=['GET','POST','PUT','DELETE'])
    def syncWidgets(self) :
        all_movement_commands = state_controller.syncronize()
        str_commands = list()
        for command in all_movement_commands :
            str_commands.append(command.__repr__())
        return {"movement_commands" : str_commands}

    



appbuilder.add_api(WidgetApi)