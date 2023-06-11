import logging
import gpiozero

from flask import Flask
from flask_appbuilder import AppBuilder, SQLA

"""
 Logging configuration
"""

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_object("config")
db = SQLA(app)
appbuilder = AppBuilder(app, db.session)


from src.StateController import StateController
from src.KlipperSocket import KlipperSocket
from src.CommandQueue import CommandQueue
from src.Widget import Widget

import src.Constants as Constants

from xml.etree import ElementTree as ET

klipper_connection = KlipperSocket(Constants.KLIPPY_SOCKET_ADDRESS)
klipper_connection.sendMessage({ "id" : 420, "method" : "gcode/script", "params" : {"script" : f"G28 X0 Y{Constants.BOARD_SIZE_Y}"} })
klipper_connection.sendMessage({ "id" : 421, "method" : "gcode/script", "params" : {"script" : f"G90"} })
klipper_connection.sendMessage({ "id" : 420, "method" : "gcode/script", "params" : {"script" : f"G0 X0 Y0"} })


toolhead_servo = gpiozero.AngularServo(Constants.SERVO_GPIO_PIN)
command_queue = CommandQueue(klipper_connection, toolhead_servo)
state_controller = StateController(command_queue)

state_controller.addWidget(Widget(0,0,ET.fromstring('<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><path d="M 10 10 H 90 V 90 H 10 L 10 10"/></svg>')))
state_controller.addWidget(Widget(20,20,ET.fromstring('<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><path d="M 10 10 H 90 V 90 H 10 L 10 10"/></svg>')))

"""
from sqlalchemy.engine import Engine
from sqlalchemy import event

#Only include this for SQLLite constraints
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    # Will force sqllite contraint foreign keys
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
"""

from . import views
from . import WidgetAPI
appbuilder.security_cleanup()