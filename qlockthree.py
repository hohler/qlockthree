import os

import RPi.GPIO as GPIO
import datetime
import time
from threading import Thread

from strip import WS2801, WS2812b
from util import hour_ein, hours, minutes, dots, word_es, word_ist
# from util.party import color_generator
from server.api import color_generator, start_api
from util.wifi import check_wifi

light_sensor_pin = 40
GPIO.setmode(GPIO.BOARD)
GPIO.setup(light_sensor_pin, GPIO.IN)


def draw_words(strip):
    for led in word_es + word_ist:
        strip.set_pixel(led)

    now = datetime.datetime.now()

    current_hour = now.hour
    current_minute = now.minute // 5 * 5

    if current_minute > 20:
        if current_hour == 23:
            current_hour = 0
        else:
            current_hour = current_hour + 1

    # show "ein uhr" and not "eins uhr"
    if current_minute == 0 and (current_hour == 1 or current_hour == 13):
        for led in hour_ein:
            strip.set_pixel(led)
    else:
        for led in hours[current_hour]:
            strip.set_pixel(led)

    for led in minutes[current_minute]:
        strip.set_pixel(led)

    dot = datetime.datetime.now().minute - (datetime.datetime.now().minute // 5 * 5)
    if dot > 0:
        for led in dots[dot]:
            strip.set_pixel(led)

    strip.show()


if __name__ == "__main__":
    strip_type = os.environ.get('QLOCKTHREE_STRIP_TYPE')

    if strip_type == 'ws2801':
        strip = WS2801()
    else:
        strip = WS2812b()

    strip.test()

    check_wifi(strip)

    api_thread = Thread(target=start_api, args=(strip,))
    api_thread.setDaemon(True)
    api_thread.start()
    time.sleep(1)

    strip.color_generator = color_generator

    last_timestamp = None
    was_environment_bright = True
    while True:
        is_environment_bright = False if GPIO.input(light_sensor_pin) == GPIO.HIGH else True

        strip.is_environment_bright = is_environment_bright

        current_timestamp = str(datetime.datetime.now().hour) + str(datetime.datetime.now().minute)
        if last_timestamp is None or last_timestamp != current_timestamp or is_environment_bright != was_environment_bright or strip.color_changed:
            draw_words(strip)

        last_timestamp = current_timestamp
        was_environment_bright = is_environment_bright
        strip.color_changed = False
        time.sleep(1)
