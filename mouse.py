#!/usr/bin/python3
import glob
import json
import os
import struct
import time

from datetime import date, datetime, time
from urllib.request import urlopen, Request

# This script requires open-razer drivers. For more information, see https://openrazer.github.io.
# It is suggested that this script be run as a cron job.

def run():
    # Mouse is off late night/morning.
    # Mouse is green/red depending on Coinbase BTC-USD price during the day, Monday through Friday.
    # Otherwise show full color spectrum pattern.

    current_time = datetime.now().time()
    mouse_dir = get_mouse_dir()

    if time(1, 0, 0) <= current_time < time(9, 0, 0):
        filepath = os.path.join(mouse_dir, "logo_matrix_effect_none")
        with open(filepath, 'wb') as mouse_effect_file:
            mouse_effect_file.write(struct.pack(">B", 0x01))

    #elif (time(9, 0, 0) <= current_time <= time(21, 0, 0)) and date.today().weekday() == 0:
    elif 1 == 1:
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'}
        url = "https://api.pro.coinbase.com/products/btc-usd/stats"
        request = Request(url=url, headers=headers) 
        data = json.loads(urlopen(request).read().decode("utf-8"))
        percent_change = (float(data['last']) - float(data['open'])) / float(data['open']) * 100

        # Numbers are scaled such that +-10% are maximum brightness.
        red_value = cutoff_min_max(percent_change * -255.0 / 20 + 127.5, 0, 255)
        green_value = cutoff_min_max(percent_change * 255.0 / 20 + 127.5, 0, 255)
        blue_value = cutoff_min_max(-abs(percent_change * 70 / 10) + 70, 0, 100) # blue is scaled differently so that colors for percent changes close to zero are more white-ish instead of yellow.
        values = [round(red_value), round(green_value), round(blue_value)]

        byte_string = struct.pack(">BBB", *values)
        static_mode_filepath = os.path.join(mouse_dir, "logo_matrix_effect_static")
        with open(static_mode_filepath, 'wb') as static_mode_file:
            static_mode_file.write(byte_string)
    else:
        filepath = os.path.join(mouse_dir, "logo_matrix_effect_spectrum")
        with open(filepath, 'wb') as mouse_effect_file:
            mouse_effect_file.write(struct.pack(">B", 0x01))

def cutoff_min_max(value, min, max):
    if value > max:
        value = max
    elif value < min:
        value = min
    return value

def get_mouse_dir():
    # The open-razer drivers inexplicably show three Razer devices when a single mouse is plugged in.
    # The directory corresponding to the real mouse contains many files/folders. We check for the device_type file to determine the correct device.
    # It is assumed that only a single mouse is plugged in to the computer.
    mouse_dir = ""
    for file_path in glob.glob(os.path.join("/sys/bus/hid/drivers/razermouse/", "*:*:*.*", "device_type")):
        with open(file_path, 'r') as device_type_file:
            if "Razer Viper Mini" in device_type_file.read():
                mouse_dir = file_path.replace('/device_type', '')
    return mouse_dir

if __name__ == '__main__':
    run()

