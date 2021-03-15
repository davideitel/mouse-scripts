#!/usr/bin/python3
import json
import os
import struct
import time

from datetime import date, datetime, time
from urllib.request import urlopen, Request

# This script requires open-razer drivers. For more information, see https://openrazer.github.io.
# It is suggested that this script be run as a cron job.

MOUSE_DIR = "/sys/bus/hid/drivers/razermouse/0003:1532:008A.0003"

def run():
    # Mouse is off late night/morning.
    # Mouse is green/red depending on Coinbase BTC-USD price during the day, Monday through Friday.
    # Otherwise show full color spectrum pattern.

    current_time = datetime.now().time()

    if time(1, 33, 0) <= current_time < time(9, 0, 0):
        filepath = os.path.join(MOUSE_DIR, "logo_matrix_effect_none")
        with open(filepath, 'wb') as mouse_effect_file:
            mouse_effect_file.write(struct.pack(">B", 0x01))

    elif (time(9, 0, 0) <= current_time <= time(16, 0, 0)) and date.today().weekday() == 0:
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'}
        url = "https://api.pro.coinbase.com/products/btc-usd/stats"
        request = Request(url=url, headers=headers) 
        data = json.loads(urlopen(request).read().decode("utf-8"))
        percent_change = (float(data['last']) - float(data['open'])) / float(data['open']) * 100

        # Numbers are scaled such that +-10% are maximum brightness.
        red_value = cutoff_min_max(percent_change * -255.0 / 20 + 127.5, 0, 255)
        green_value = cutoff_min_max(percent_change * 255.0 / 20 + 127.5, 0, 255)
        blue_value = cutoff_min_max(-abs(percent_change * 100 / 10) + 100, 0, 100) # blue is scaled differently so that colors for percent changes close to zero are more white-ish instead of yellow.
        values = [round(red_value), round(green_value), round(blue_value)]

        byte_string = struct.pack(">BBB", *values)
        static_mode_filepath = os.path.join(MOUSE_DIR, "logo_matrix_effect_static")
        with open(static_mode_filepath, 'wb') as static_mode_file:
            static_mode_file.write(byte_string)
    else:
        filepath = os.path.join(MOUSE_DIR, "logo_matrix_effect_spectrum")
        with open(filepath, 'wb') as mouse_effect_file:
            mouse_effect_file.write(struct.pack(">B", 0x01))

def cutoff_min_max(value, min, max):
    if value > max:
        value = max
    elif value < min:
        value = min
    return value

if __name__ == '__main__':
    run()

