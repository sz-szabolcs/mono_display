from mono_display import *
from machine import RTC


def test_display(device, t=0):
    # flushframe()
    # show()
    # clear()
    # refresh_epaper()
    # rotate(90)
    device.log("", 'left')
    device.log(device.get_par()[2], 'left')  # name of screen driver chip
    device.log(device.get_par()[1], 'left')  # resolution
    device.log("", 'left')

    sleep_ms(t)

    rtc = RTC()
    now = rtc.datetime()
    device.log_rtc(rtc_datetime=now)

    sleep_ms(t)

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
    device.draw_rssi(10, 10, state=-106, scale=1)
    device.show()
    sleep_ms(t)
    device.flushframe()
    device.draw_rssi(10, 10, state=-35, scale=1)
    device.show()
    sleep_ms(t)
    device.flushframe()
    device.draw_rssi(10, 10, state=-106, scale=2)
    device.show()
    sleep_ms(t)
    device.flushframe()
    device.draw_rssi(10, 10, state=-35, scale=2)
    device.show()
    sleep_ms(t)

    device.flushframe()
    device.draw_battery_state(x=10, y=10, charging=False, state=12, scale=1)
    device.show()
    sleep_ms(t)
    device.flushframe()
    device.draw_battery_state(x=10, y=10, charging=True, state=15, scale=1)
    device.draw_battery_state(x=10, y=10, charging=True, state=15, scale=1)
    sleep_ms(t)
    device.flushframe()
    device.draw_battery_state(x=10, y=10, charging=True, state=55, scale=2)
    device.draw_battery_state(x=10, y=10, charging=True, state=55, scale=2)
    sleep_ms(t)

    for sw in range(32):
        device.flushframe()
        device.draw_switch(8, 4, state=0, scale=0.1 * sw)
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
    device.draw_save_glyph(10, 6)

    sleep_ms(t)

    device.flushframe()
    device.render_gear(x_pos=device.get_res()[0] // 2, y_pos=device.get_res()[1] // 2, len_in_frames=60, obj_r=16,
                       points=8, points_r=4, wait=10)


wait_time = 1000  # ms


#  --------  1.54" e-paper, 200x200  -------
# e_paper = MonoDisplay(sck_freq=4000000,
#                       mosi=12,
#                       miso=2,
#                       sck=13,
#                       cs=34,
#                       dc=21,
#                       rst=36,
#                       busy=35,
#                       inverted=False,
#                       device="1in54_epd",
#                       debug=False,
#                       epd_slow_mode=False)
#
# test_display(e_paper, wait_time)

#  --------  SH1106 OLED, 128x64  --------
# Oled_sh1106 = MonoDisplay(sck_freq=400000,
#                           inverted=False,
#                           device="sh1106_128x64",
#                           scl=1,
#                           sda=2,
#                           debug=False)
#
# Oled_sh1106.set_oled_brightness(255)
# test_display(device=Oled_sh1106, t=wait_time)
# Oled_sh1106.set_oled_brightness(0)

#  --------  SSD1309 OLED, 128x64  --------
# Oled_ssd1309 = MonoDisplay(sck_freq=400000,
#                            inverted=False,
#                            device="ssd1309_128x64",
#                            scl=16,
#                            sda=17,
#                            debug=False)
#
# Oled_ssd1309.rotate(90)
# Oled_ssd1309.set_oled_brightness(255)
# test_display(Oled_ssd1309, wait_time)
# Oled_ssd1309.set_oled_brightness(0)

#  --------  SSD1306 OLED, 128x64  --------
# Oled_ssd1306 = MonoDisplay(sck_freq=400000,
#                            inverted=False,
#                            scl=15,
#                            sda=16,
#                            device="ssd1306_128x64",
#                            debug=False,
#                            scrollable_log=True,
#                            up_button_pin=35,
#                            down_button_pin=36)
#
# Oled_ssd1306.set_oled_brightness(255)
# test_display(Oled_ssd1306, wait_time)
#
# # Show Scrollable:
# for i in range(16):
#     Oled_ssd1306.log("extra line #" + str(i), 'center')
#
# for i in range(1024):
#     Oled_ssd1306.show_scrollable_log(textalign='left')
#
# Oled_ssd1306.set_oled_brightness(0)

#  --------  84x48 LCD (Nokia 5110 like)  --------
Nokia_5110 = MonoDisplay(sck_freq=2000000,
                         backlight=38,
                         mosi=11,
                         miso=0,
                         sck=16,
                         cs=10,
                         dc=47,
                         rst=7,
                         inverted=False,
                         device="nokia_5110",
                         debug=False,
                         scrollable_log=True,
                         up_button_pin=42,
                         down_button_pin=46)

Nokia_5110.pcd8544_contrast(op_voltage=0x3f)

Nokia_5110.lcd_backlight(value=1024, binary=False, inverted=False)

# not using PWM BL:
# Nokia_5110.lcd_backlight(value=1, binary=True, inverted=False)
# sleep_ms(1000)
# Nokia_5110.lcd_backlight(value=0, binary=True, inverted=False)

test_display(Nokia_5110, wait_time)

# Show Scrollable:
for i in range(32):
    Nokia_5110.log("scroll line @" + str(i), 'center')

for i in range(1024):
    Nokia_5110.show_scrollable_log(textalign='left')

Nokia_5110.lcd_backlight(value=0, binary=False, inverted=False)

#  --------  ST7920 LCD, 128x64  --------
# Lcd_st7920 = MonoDisplay(sck_freq=4000000,
#                          backlight=3,
#                          mosi=9,
#                          miso=7,
#                          sck=10,
#                          cs=4,
#                          dc=6,
#                          rst=5,
#                          inverted=False,
#                          device="st7920",
#                          debug=False)
#
# Lcd_st7920.lcd_backlight(value=1024)
# test_display(Lcd_st7920, wait_time)
# Lcd_st7920.lcd_backlight(value=16)

#  --------  ST7735 TFT LCD, 128x128  --------
# Lcd_st7735 = MonoDisplay(sck_freq=4000000,
#                          backlight=3,
#                          mosi=10,
#                          miso=45,
#                          sck=9,
#                          cs=11,
#                          dc=8,
#                          rst=7,
#                          inverted=False,
#                          device="st7735_1in44",
#                          tft_colored=False,
#                          debug=True)
#
# Lcd_st7735.lcd_backlight(value=1024)
# test_display(Lcd_st7735, wait_time)
# Lcd_st7735.lcd_backlight(value=16)
