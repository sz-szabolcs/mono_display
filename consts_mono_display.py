from pcd8544 import PCD8544_WIDTH, PCD8544_HEIGHT
from st7920 import ST7920_WIDTH, ST7920_HEIGHT
from epaper1in54_mod import EPD_WIDTH, EPD_HEIGHT
from ST7735_128x128 import ScreenSize as st7735_ScreenSize


display_properties = {"st7920": [[ST7920_WIDTH, ST7920_HEIGHT], 'Generic ST7920'],
                      "nokia_5110": [[PCD8544_WIDTH, PCD8544_HEIGHT], 'PCD8544'],
                      "sh1106_128x64": [[0x80, 0x40], 'Generic SH1106'],
                      "ssd1309_128x64": [[0x80, 0x40], '2.42 OLED V1.1'],
                      "ssd1306_128x64": [[0x80, 0x40], 'Generic SSD1306'],
                      "1in54_epd": [[EPD_WIDTH, EPD_HEIGHT], "1.54 inch e-ink device, GDEH0154D27"],
                      "st7735_1in44": [st7735_ScreenSize, "1in44 TFT ST7735"],
                      "gc9a01": [[0xF0, 0xF0], '1.28"TFT VER1.0, GC9A01']
                      }

save_glyph = bytearray(b'\xff\xff\xff\xff\xff\xff\xff\xff\x01\x01\x01\x01\x01\x01\x01\x3d'
                       b'\x3d\x3d\x3d\x3d\x3d\x3d\x3d\x01\xff\xff\xfe\xfc\xf8\xf0\xe0\xc0'
                       b'\xff\xff\xff\xff\x0f\x0f\x0f\x4f\x4f\x4f\x4f\x4f\x4f\x4f\x4f\x4f'
                       b'\x4f\x4f\x4f\x4f\x4f\x4f\x4f\x4f\x4f\x0f\x0f\x0f\xff\xff\xff\xff'
                       b'\xff\xff\xff\xff\x00\x00\x00\x92\x92\x92\x92\x92\x92\x92\x92\x92'
                       b'\x92\x92\x92\x92\x92\x92\x92\x92\x92\x00\x00\x00\xff\xff\xff\xff'
                       b'\xff\xff\xef\xff\xc0\xc0\xc0\xcd\xcd\xcd\xcd\xcd\xcd\xcd\xcd\xcd'
                       b'\xcd\xcd\xcd\xcd\xcd\xcd\xcd\xcd\xcd\xc0\xc0\xc0\xff\xef\xff\xff')  # 32x32 px

tft_color_theme = {'black': 0x0000,
                   'white': 0xffff,
                   'trace_color': 0xFBC0,
                   'circle_color': 0xED86,
                   'circle_fill_color': 0xFBBF,
                   'sw_body_color': 0x9d13,
                   'sw_toggle_bg_color': 0x1082,
                   'sw_toggle_color': 0x6dee,
                   'text_color': 0x249F,
                   'progbar_border_color': 0xA00D,
                   'progbar_fill_color': 0x9FE7,
                   'wifi_rssi_color': 0x39b4,
                   'battery_border_color': 0xc604,
                   'battery_fill_color': 0x1705}
