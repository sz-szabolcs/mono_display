from mono_display import *


def test_display(device, t=0):
    # flushframe()
    # show()
    # clear()
    # refresh_epaper()
    # rotate(90)
    device.log("", 'left')
    device.log("", 'left')
    device.log(device.get_par()[2], 'left')  # name of screen driver chip
    device.log(device.get_par()[1], 'left')  # resolution
    sleep_ms(t)
    device.log("", 'left')

    for align in range(16):
        if 0 < align < 5:
            device.log(text="left", textalign='left')
        elif 5 < align < 10:
            device.log(text="right", textalign='right')
        elif 10 < align < 15:
            device.log(text="center", textalign='center')
        else:
            pass
    sleep_ms(t)

    device.flushframe()
    device.draw_switch(2, 4, state=0, scale=0.4)
    device.show()
    device.draw_switch(10, 4, state=1, scale=0.6)
    device.show()
    device.draw_switch(21, 4, state=0, scale=0.8)
    device.show()
    device.draw_switch(35, 4, state=1, scale=1)
    device.show()
    device.draw_switch(53, 4, state=0, scale=1.2)
    device.show()
    device.draw_switch(74, 4, state=1, scale=1.4)
    device.show()
    device.draw_switch(98, 4, state=0, scale=1.6)
    device.show()
    device.draw_switch(125, 4, state=1, scale=2.2)
    device.show()
    sleep_ms(t)

    device.flushframe()

    for trace in range(10):
        device.flushframe()
        device.trace(frequency=trace + 1, phase=trace / 2, amplitude=trace, time_ms=1000, colored=1)
        device.show()

    sleep_ms(t)

    device.flushframe()
    device.progressbar(col_pos=2, row_pos=2, width=40, height=8, state=65, filled=True)
    device.progressbar(col_pos=2, row_pos=4, width=75, height=12, state=95, filled=False)
    sleep_ms(t)

    device.flushframe()
    device.draw_save_glyph(32, 32)
    sleep_ms(t)

    device.flushframe()
    device.render_gear(x_pos=device.get_res()[0] // 2, y_pos=device.get_res()[1] // 2, len_in_frames=30, obj_r=16,
                       points=6, points_r=4, wait=10)


wait_time = 2  # ms

#  --------  1.54" e-paper, 200x200  -------
e_paper = MonoDisplay(sck_freq=1000000,
                      mosi=12,
                      miso=2,
                      sck=13,
                      cs=34,
                      dc=21,
                      rst=36,
                      busy=35,
                      inverted=False,
                      device="1in54_epd",
                      debug=False,
                      epd_slow_mode=False)

test_display(e_paper, wait_time)

#  --------  SH1106 OLED, 128x64  --------
Oled_sh1106 = MonoDisplay(sck_freq=400000,
                          inverted=False,
                          device="sh1106_128x64",
                          scl=1,
                          sda=2,
                          debug=False)

Oled_sh1106.set_oled_brightness(255)
test_display(device=Oled_sh1106, t=wait_time)
Oled_sh1106.set_oled_brightness(0)

#  --------  SSD1309 OLED, 128x64  --------
Oled_ssd1309 = MonoDisplay(sck_freq=400000,
                           inverted=False,
                           device="ssd1309_128x64",
                           scl=16,
                           sda=17,
                           debug=False)

Oled_ssd1309.rotate(90)
Oled_ssd1309.set_oled_brightness(255)
test_display(Oled_ssd1309, wait_time)
Oled_ssd1309.set_oled_brightness(0)

#  --------  SSD1306 OLED, 128x64  --------
Oled_ssd1306 = MonoDisplay(sck_freq=400000,
                           inverted=False,
                           scl=15,
                           sda=18,
                           device="ssd1306_128x64",
                           debug=False)

Oled_ssd1306.set_oled_brightness(255)
test_display(Oled_ssd1306, wait_time)
Oled_ssd1306.set_oled_brightness(0)

#  --------  84x48 LCD (Nokia 5110 like)  --------
Nokia_5110 = MonoDisplay(sck_freq=1000000,
                         backlight=8,  # ->Pin number, backlight turned ON on init
                         mosi=9,
                         miso=7,
                         sck=10,
                         cs=11,
                         dc=6,
                         rst=5,
                         inverted=False,
                         device="nokia_5110",
                         debug=False)

test_display(Nokia_5110, wait_time)
Nokia_5110.lcd_backlight(0)

#  --------  ST7920 LCD, 128x64  --------
Lcd_st7920 = MonoDisplay(sck_freq=1000000,
                         backlight=3,
                         mosi=9,
                         miso=7,
                         sck=10,
                         cs=4,
                         dc=6,
                         rst=5,
                         inverted=False,
                         device="st7920",
                         debug=False)

Lcd_st7920.lcd_backlight(value=1024)
test_display(Lcd_st7920, wait_time)
Lcd_st7920.lcd_backlight(value=16)
