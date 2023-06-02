from flask import request, Response
from flask_appbuilder.api import BaseApi, expose
from flask_appbuilder.security.decorators import protect
from . import appbuilder, state_controller, klipper_connection,

import json
import xml.etree.ElementTree as ET
import src.Widget as W


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
        try :
            contents = request.get_json()
            
            pos_x = contents['pos_x']
            pos_y = contents['pos_y']

            if contents['details']['type'] == 'text' :
                widget = W.TextWidget(pos_x, pos_y, ET.fromstring(contents['details']), contents['svg'])
            #elif contents['details']['type'] == '' : open/closed princliple yada yada
            else :
                widget = W.Widget(pos_x, pos_y, ET.fromstring(contents['svg']), contents['details'])


            state_controller.addWidget(widget)

            return widget.toJson()
        except :
            return Response("Must follow proper widget formatting details", 400)
        
    @expose('/sync', methods=['GET','POST','PUT','DELETE'])
    def syncWidgets(self) :
        state_controller.syncronize()


        
        

    
    



appbuilder.add_api(WidgetApi)