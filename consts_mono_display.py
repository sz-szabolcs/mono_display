from pcd8544 import PCD8544_WIDTH, PCD8544_HEIGHT
from st7920 import ST7920_WIDTH, ST7920_HEIGHT
from epaper1in54_mod import EPD_WIDTH, EPD_HEIGHT


display_properties = {"st7920": [[ST7920_WIDTH, ST7920_HEIGHT], 'Generic ST7920'],
                      "nokia_5110": [[PCD8544_WIDTH, PCD8544_HEIGHT], 'PCD8544'],
                      "sh1106_128x64": [[0x80, 0x40], 'Generic SH1106'],
                      "ssd1309_128x64": [[0x80, 0x40], '2.42 OLED V1.1'],
                      "ssd1306_128x64": [[0x80, 0x40], 'Generic SSD1306'],
                      "1in54_epd": [[EPD_WIDTH, EPD_HEIGHT], "GDEH0154D27 1.54 inch e-ink device"]
                      }

save_glyph = bytearray(b'\xff\xff\xff\xff\xff\xff\xff\xff\x01\x01\x01\x01\x01\x01\x01\x3d'
                       b'\x3d\x3d\x3d\x3d\x3d\x3d\x3d\x01\xff\xff\xfe\xfc\xf8\xf0\xe0\xc0'
                       b'\xff\xff\xff\xff\x0f\x0f\x0f\x4f\x4f\x4f\x4f\x4f\x4f\x4f\x4f\x4f'
                       b'\x4f\x4f\x4f\x4f\x4f\x4f\x4f\x4f\x4f\x0f\x0f\x0f\xff\xff\xff\xff'
                       b'\xff\xff\xff\xff\x00\x00\x00\x92\x92\x92\x92\x92\x92\x92\x92\x92'
                       b'\x92\x92\x92\x92\x92\x92\x92\x92\x92\x00\x00\x00\xff\xff\xff\xff'
                       b'\xff\xff\xef\xff\xc0\xc0\xc0\xcd\xcd\xcd\xcd\xcd\xcd\xcd\xcd\xcd'
                       b'\xcd\xcd\xcd\xcd\xcd\xcd\xcd\xcd\xcd\xc0\xc0\xc0\xff\xef\xff\xff')  # 32x32 px
