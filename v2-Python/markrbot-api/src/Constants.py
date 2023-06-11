DRAW_SPEED = 600
MOVE_SPEED = 1000
ERASE_SPEED = 400

MARKER_ERASER_DIST_X = 0 #distance from the marker to eraser on the Y-carrige; plane offset
MARKER_ERASER_DIST_Y = 10 #in mm

BOARD_SIZE_X = 1125
BOARD_SIZE_Y = 735

MAX_X = BOARD_SIZE_X - MARKER_ERASER_DIST_X #furthest point BOTH eraser and marker can reach
MAX_Y = BOARD_SIZE_Y - MARKER_ERASER_DIST_Y
MIN_X = MARKER_ERASER_DIST_X #closest point BOTH marker and eraser can reach
MIN_Y = MARKER_ERASER_DIST_Y


#these angles will determine how hard the zero presses the marker/eraser into the board
SERVO_ANGLE_DRAW = -80 
SERVO_ANGLE_ERASE = 80

SERVO_ANGLE_MOVE = 0
SERVO_ANGLE_MIN = -90
SERVO_ANGLE_MAX = 90

SERVO_GPIO_PIN = 12 #pin must be PWM capable

KLIPPY_SOCKET_ADDRESS = '/tmp/klippy_uds'
