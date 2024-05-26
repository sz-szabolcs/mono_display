from machine import Pin, SoftSPI, SoftI2C, PWM
import consts_mono_display
import framebuf
from utime import sleep_ms
from math import sin, cos, pi


# 2024-05-25: slow mode in log() draws 4 lines of text at a time to save time when
# an epaper device updates really slowly...
# 2024-05-03: ->draw_save_glyph(x, y), ->render_gear(x_pos, y_pos, len_in_frames, obj_r, points, points_r, wait)
# 2024-04-27: ->progressbar(col_pos, row_pos, width, height, state=50, filled=False),
# 2024-04-26: ->set_oled_brightness(0-255), ->lcd_backlight(0-1024, in case of PCD8544 0-1)
# 2024-04-25: optimization, clean up
# 2024-04-24: *works with SSD1309 ->*sort-of supported with SH1106 driver
# 2024-02-09: works with SSD1306, SH1106
# 2024-02-02: works with ST7920, PCD8544, 1.54" e-paper
# 2024-01-28: A simple class for monochrome displays. ->log(text, textalign),
#                                                     ->draw_switch(x, y, state),
#                                                     ->draw_circle(x, y, r, colored, filled),
#                                                     ->trace(frequency, phase, amplitude, time_ms, colored),


# ST7920:
# --------  ST7920 128X64B V2.X PIN  --------  BUS Pin  --------
#                   GND                  |        GND
#                   VCC                  |        5V
#                   V0                   |        ADJ. CONTRAST
#                   RS                   |        CS
#                   R/W                  |        MOSI
#                   E (En)               |        SCK
#                   RST                  |        RESET
#                   BL A                 |        LED VCC
#                   BL K                 |        LED VSS
# connect LCD PSB with LCD GND
# connect LCD RS with LCD RST


class MonoDisplay:
    def __init__(self,
                 device="st7920",
                 sck_freq=100000,
                 inverted=False,
                 debug=True,
                 backlight=3,
                 mosi=9,
                 miso=7,
                 sck=10,
                 cs=4,
                 dc=6,
                 rst=5,
                 busy=20,
                 scl=19,
                 sda=20,
                 epd_slow_mode=False):

        # --------  CONTROL VARS  --------
        self.DEBUG = debug
        self._inverted = inverted
        self._sck_freq = sck_freq
        self._device = device.lower()
        self._epd_mem_clear = [0x00, 0xff] * 2  # used only with e-ink device
        self._last_oled_brightness = 0
        self.spcr = "\t-> "
        # --------  CONTROL VARS END  --------

        # -> init the right driver by given key:
        self._devices_dict = consts_mono_display.display_properties

        # --------  INIT BUS  --------

        if self._device == "sh1106_128x64" or self._device == "ssd1306_128x64" or self._device == "ssd1309_128x64":
            self._i2c_scl = Pin(scl)
            self._i2c_sda = Pin(sda)

            self._i2c = SoftI2C(scl=self._i2c_scl, sda=self._i2c_sda, freq=self._sck_freq)
            if self.DEBUG:
                i2c_scan_result = self._i2c.scan()
                if len(i2c_scan_result) > 0:
                    i2c_scan_result = hex(i2c_scan_result[0])
                    print(self.spcr + "I2C OK, scan(): {scan_res}".format(scan_res=i2c_scan_result))

        elif self._device == "nokia_5110" or self._device == "st7920" or self._device == "1in54_epd":
            self._backlightpin = Pin(backlight, Pin.OUT)
            self._mosi = Pin(mosi)
            self._miso = Pin(miso)
            self._sck = Pin(sck)
            self._cs = Pin(cs)
            self._dc = Pin(dc)
            self._rst = Pin(rst)
            self._busy = Pin(busy)
            self._epd_slow_mode = epd_slow_mode

            self._SPI = SoftSPI(baudrate=self._sck_freq,
                                polarity=0,
                                phase=0,
                                sck=self._sck,
                                mosi=self._mosi,
                                miso=self._miso)
            if self.DEBUG:
                print(self.spcr + "init SPI OK")

        # --------  INIT BUS END  --------

        # --------  INIT DISPLAY & CONSTRUCT SCREEN  --------
        if isinstance(self._device, str):
            self._oled_brightness = 0
            self._lcd_brightness = 0
            if self._device in self._devices_dict:
                self.W, self.H = self.get_res()[0], self.get_res()[1]

                if self._device == "st7920":
                    from st7920 import ST7920
                    self._display = ST7920(self._SPI, self._rst)
                    # this array will be manipulated by framebuf object and gets rendered to screen:
                    self._framedata = bytearray(self.W * self.H // 8)
                    self._frame = framebuf.FrameBuffer(self._framedata, self.W, self.H, framebuf.MONO_HLSB)
                    self._lcd_backlight_pwm = PWM(self._backlightpin, freq=2000)
                    self.lcd_backlight(value=511)

                elif self._device == "nokia_5110":
                    from pcd8544 import PCD8544
                    self._display = PCD8544(self._SPI, self._cs, self._dc, self._rst)
                    self._framedata = bytearray((self.H // 8) * self.W)
                    self._frame = framebuf.FrameBuffer(self._framedata, self.W, self.H, framebuf.MONO_VLSB)
                    self.lcd_backlight(value=1)  # turn ON on init, only 1 or 0 because positive gnd

                elif self._device == "sh1106_128x64":
                    import sh1106
                    self._display = sh1106.SH1106_I2C(self.W, self.H, self._i2c, rotate=0, delay=0)
                    self._framedata = bytearray(self.W * self.H // 8)
                    self._frame = self._display  # note this is inherited from framebuf

                elif self._device == "ssd1309_128x64":
                    import sh1106
                    self._display = sh1106.SH1106_I2C(self.W + 2, self.H, self._i2c, rotate=0, delay=0)
                    self._framedata = bytearray(self.W * self.H // 8)
                    self._frame = self._display  # note this is inherited from framebuf

                elif self._device == "ssd1306_128x64":
                    import ssd1306
                    self._display = ssd1306.SSD1306_I2C(self.W, self.H, self._i2c)
                    self._framedata = bytearray(self.W * self.H // 8)
                    self._frame = self._display  # note this is inherited from framebuf
                    self._display.invert(0)

                elif self._device == "1in54_epd":
                    import epaper1in54_mod
                    self._display = epaper1in54_mod.EPD(self._SPI, self._cs, self._dc, self._rst, self._busy)
                    self._display.init()
                    self._framedata = bytearray(self.W * self.H // 8)
                    self._frame = framebuf.FrameBuffer(self._framedata, self.W, self.H, framebuf.MONO_HLSB)
                    self.refresh_epaper()
                else:
                    pass

                if self.DEBUG:
                    print(self.spcr + "Device: {logdevice} Init OK".format(logdevice=self._device))
                    print(self.spcr + "Driver Chip: {chip}".format(chip=self._devices_dict[self._device][1]))
                    print(self.spcr + "Created Buffer size: {logbufsize}".format(logbufsize=len(self._framedata)))

            else:
                print(self.spcr + "Device: {logusrdevice} is not a valid chip or a chip which is not supported yet..."
                      .format(logusrdevice=self._device))
        else:
            print(self.spcr + "device must be a string")
            pass

        if self._device == "1in54_epd":
            if self._inverted:
                self.COLORED, self.UNCOLORED = 1, 0
            else:
                self.COLORED, self.UNCOLORED = 0, 1
        else:
            if self._inverted:
                self.COLORED, self.UNCOLORED = 0, 1
            else:
                self.COLORED, self.UNCOLORED = 1, 0

        self._text_size = 8  # currently, we cannot change font size, which is 8 by 8 in mpy framebuf
        self._max_line_width = self.W // self._text_size   # chars, font size is fixed 8x8
        self._max_line_number = self.H // self._text_size
        self._page = []
        self._counter_log_slow_mode = 0

        if self.DEBUG:
            print(self.spcr + "Resolution: {logres}".format(logres=str(self.get_res()[0]) + "x" + str(self.get_res()[1])))
            print(self.spcr + "Line width: {loglinew}".format(loglinew=self._max_line_width))
            print(self.spcr + "Max Lines: {logmaxlines}".format(logmaxlines=self._max_line_number))
            print(self.spcr + "[OK]")

    def get_res(self):
        res = self._devices_dict[self._device][0]
        return res

    def get_par(self):
        self_parameters = [self._device,                                           # display name
                           str(self.get_res()[0]) + "x" + str(self.get_res()[1]),  # res
                           self._devices_dict[self._device][1],                    # chip
                           len(self._framedata)]                                   # buf size

        return self_parameters

    def lcd_backlight(self, value):
        if value > 1023:
            value = 1023

        if self._device == "st7920":
            if value < self._lcd_brightness:
                while value != self._lcd_brightness:
                    self._lcd_brightness -= 1
                    if not self._lcd_brightness % 4:
                        self._lcd_backlight_pwm.duty(self._lcd_brightness)
                        sleep_ms(8)
                if self.DEBUG:
                    print(self.spcr + "ST7920 brightness decreased to: " + str(self._lcd_brightness))
            elif value > self._lcd_brightness:
                while value != self._lcd_brightness:
                    self._lcd_brightness += 1
                    if not self._lcd_brightness % 4:
                        self._lcd_backlight_pwm.duty(self._lcd_brightness)
                        sleep_ms(8)
                if self.DEBUG:
                    print(self.spcr + "ST7920 brightness increased to: " + str(self._lcd_brightness))
            else:
                return -1

        elif self._device == "nokia_5110":
            if value:
                self._backlightpin.value(0)
            else:
                self._backlightpin.value(1)

        else:
            return -1

    def set_oled_brightness(self, amount):
        if self._device == "sh1106_128x64" or self._device == "ssd1306_128x64" or self._device == "ssd1309_128x64":
            if amount <= self._last_oled_brightness:
                for dec in range(self._last_oled_brightness, amount, -1):
                    self._display.contrast(dec)
                    self._last_oled_brightness = dec
                    sleep_ms(4)

                if self.DEBUG:
                    print(self.spcr + "oled bl set: {brightness}".format(brightness=self._last_oled_brightness))

            elif amount >= self._last_oled_brightness:
                for inc in range(self._last_oled_brightness, amount):
                    self._display.contrast(inc)
                    self._last_oled_brightness = inc
                    sleep_ms(4)

                if self.DEBUG:
                    print(self.spcr + "oled bl set : {brightness}".format(brightness=self._last_oled_brightness))

            else:
                print("brightness out of range")

        else:
            pass

    def flushframe(self):
        """ Fill frame data array without render on the screen """
        self._frame.fill(self.UNCOLORED)

    def rotate(self, deg):
        self._frame.rotate(deg)

    def clear(self):
        """ Clear framebuf and display a blank screen """
        if self._device == "1in54_epd":
            self._display.clear_frame_memory(0xff)  # empty display's internal frb
            self._frame.fill(self.UNCOLORED)  # empty framebuffer
            self._display.display_frame()
        else:
            self._frame.fill(self.UNCOLORED)
            self.show()

    def show(self):
        """ Sets frame memory with composed framebuffer and show on screen """
        if self._device == "st7920":
            self._display.show(data=self._framedata)
        elif self._device == "nokia_5110":
            self._display.data(data=self._framedata)
        elif self._device == "sh1106_128x64" or self._device == "ssd1309_128x64":
            self._display.show()  # full_update=True
        elif self._device == "ssd1306_128x64":
            self._display.show()
        elif self._device == "1in54_epd":
            self._display.set_frame_memory(self._framedata, 0, 0, self.W, self.H)
            self._display.display_frame()
        else:
            return -1

    def refresh_epaper(self):
        """ Run a full display erase routine (slow) """
        for i in self._epd_mem_clear:
            self._display.clear_frame_memory(i)
            self._display.display_frame()

    def trace(self, frequency=1, phase=0, amplitude=10, time_ms=1000, colored=1):
        scale_offset = 20
        curve = []  # storing coords
        step = (self.W - scale_offset) / time_ms  # scale x represents n secs
        for t in range(0, time_ms + 1, 1):
            diversion = amplitude * sin(2 * pi * frequency * t / time_ms - phase)  # e = A sin(2 pi f t + phase)
            x = 10 + t * step
            y = self.H / 2 + diversion * self.H / scale_offset
            curve.append((x, y))
        color = colored
        if self._device == "1in54_epd":
            color ^= 1

        for pixel in curve:
            self._frame.pixel(int(pixel[0]), int(pixel[1]), color)

    def draw_circle(self, x, y, radius, colored, filled):
        # Bresenham algorithm
        x_pos = - radius
        y_pos = 0
        err = 2 - 2 * radius
        if x >= self.W or y >= self.H:
            return
        while True:
            if colored:
                self._frame.pixel(x - x_pos, y + y_pos, self.COLORED)
                self._frame.pixel(x + x_pos, y + y_pos, self.COLORED)
                self._frame.pixel(x + x_pos, y - y_pos, self.COLORED)
                self._frame.pixel(x - x_pos, y - y_pos, self.COLORED)
            else:
                self._frame.pixel(x - x_pos, y + y_pos, self.UNCOLORED)
                self._frame.pixel(x + x_pos, y + y_pos, self.UNCOLORED)
                self._frame.pixel(x + x_pos, y - y_pos, self.UNCOLORED)
                self._frame.pixel(x - x_pos, y - y_pos, self.UNCOLORED)

            if filled:
                self._frame.hline(x + x_pos, y + y_pos, 2 * (-x_pos) + 1, self.COLORED)
                self._frame.hline(x + x_pos, y - y_pos, 2 * (-x_pos) + 1, self.COLORED)

            e2 = err
            if e2 <= y_pos:
                y_pos += 1
                err += y_pos * 2 + 1
                if -x_pos == y_pos and e2 <= x_pos:
                    e2 = 0
            if e2 > x_pos:
                x_pos += 1
                err += x_pos * 2 + 1
            if x_pos > 0:
                break

    def draw_switch(self, x, y, state=0, scale=1):
        default_width = 16
        default_height = default_width * 2
        default_gap = 6
        sw_body_width = int(default_width * scale)
        sw_body_height = int(default_height * scale)
        gap = int(default_gap * scale)
        sw_state_bg_width = sw_body_width - gap
        sw_state_bg_height = sw_state_bg_width
        sw_state_bg_x = (x + int(sw_body_width / 2)) - int(sw_state_bg_width / 2)
        sw_state_bg_y = y + gap // 2
        sw_dot_x = x + sw_body_width // 2
        sw_dot_y = sw_state_bg_y + sw_state_bg_height // 2

        if self._device == "1in54_epd":
            if state:
                self._frame.fill_rect(x, y, sw_body_width, sw_body_height, self.COLORED)
                self._frame.fill_rect(sw_state_bg_x, sw_state_bg_y, sw_state_bg_width, sw_state_bg_height,
                                      self.UNCOLORED)
                if scale <= 0.8:
                    self._frame.pixel(sw_dot_x - 1, sw_dot_y - 1, self.COLORED)
                    self._frame.pixel(sw_dot_x, sw_dot_y - 1, self.COLORED)
                else:
                    self._frame.text("I", sw_dot_x - self._text_size // 2, sw_dot_y - self._text_size // 2, self.COLORED)

            else:
                bottom_pos = (y + sw_body_height - sw_state_bg_height) - gap // 2
                self._frame.fill_rect(x, y, sw_body_width, sw_body_height, self.COLORED)
                self._frame.fill_rect(sw_state_bg_x, bottom_pos, sw_state_bg_width, sw_state_bg_height, self.UNCOLORED)

                if scale <= 0.8:
                    self._frame.pixel(sw_dot_x - 1, bottom_pos + sw_state_bg_height // 2, self.COLORED)
                    self._frame.pixel(sw_dot_x, bottom_pos + sw_state_bg_height // 2, self.COLORED)
                else:
                    self._frame.text("0", sw_dot_x - self._text_size // 2,
                                     bottom_pos + sw_state_bg_height // 2 - self._text_size // 2, self.COLORED)

        else:
            if state:
                self._frame.fill_rect(x, y, sw_body_width, sw_body_height, self.COLORED)
                self._frame.fill_rect(sw_state_bg_x, sw_state_bg_y, sw_state_bg_width, sw_state_bg_height, self.UNCOLORED)
                if scale <= 0.8:
                    self._frame.pixel(sw_dot_x - 1, sw_dot_y - 1, 1)
                    self._frame.pixel(sw_dot_x, sw_dot_y - 1, 1)
                else:
                    self._frame.text("I", sw_dot_x - self._text_size // 2, sw_dot_y - self._text_size // 2)

            else:
                bottom_pos = (y + sw_body_height - sw_state_bg_height) - gap // 2
                self._frame.fill_rect(x, y, sw_body_width, sw_body_height, self.COLORED)
                self._frame.fill_rect(sw_state_bg_x, bottom_pos, sw_state_bg_width, sw_state_bg_height, self.UNCOLORED)

                if scale <= 0.8:
                    self._frame.pixel(sw_dot_x - 1, bottom_pos + sw_state_bg_height // 2, 1)
                    self._frame.pixel(sw_dot_x, bottom_pos + sw_state_bg_height // 2, 1)
                else:
                    self._frame.text("0", sw_dot_x - self._text_size // 2, bottom_pos + sw_state_bg_height // 2 - self._text_size // 2)

    def log(self, text, textalign="left"):
        x_pos = 0

        if textalign == "left":
            x_pos = 0

        if isinstance(text, str):
            if self._device == "1in54_epd" and self._epd_slow_mode:
                if len(text) <= self._max_line_width:
                    if len(self._page) >= self._max_line_number:
                        self._page.pop(0)
                        self._page.append(text)
                    else:
                        self._page.append(text)
                else:
                    text_a, text_b = text[0:self._max_line_width], text[self._max_line_width::]
                    if len(self._page) >= self._max_line_number:
                        self._page.pop(0)
                        self._page.pop(0)
                        self._page.append(text_a)
                        self._page.append(text_b)
                    else:
                        self._page.append(text_a)
                        self._page.append(text_b)

                # render page:
                self.flushframe()  # clear frame

                for line_s in range(len(self._page)):
                    if textalign == "center":
                        x_pos = (self.W // 2) - ((len(self._page[line_s]) * self._text_size) // 2)
                    elif textalign == "right":
                        x_pos = self.W - len(self._page[line_s]) * self._text_size
                    y_pos = line_s * self._text_size
                    self._frame.text(self._page[line_s], x_pos, y_pos, self.COLORED)

                if len(self._page) < self._max_line_number:
                    if not len(self._page) % 4:
                        self.show()  # show framebuf
                else:
                    self._counter_log_slow_mode += 1
                    if not self._counter_log_slow_mode % 8:
                        self.show()  # show framebuf

            else:
                if len(text) <= self._max_line_width:
                    if len(self._page) >= self._max_line_number:
                        self._page.pop(0)
                        self._page.append(text)
                    else:
                        self._page.append(text)
                else:
                    text_a, text_b = text[0:self._max_line_width], text[self._max_line_width::]
                    if len(self._page) >= self._max_line_number:
                        self._page.pop(0)
                        self._page.pop(0)
                        self._page.append(text_a)
                        self._page.append(text_b)
                    else:
                        self._page.append(text_a)
                        self._page.append(text_b)

                # render page:
                self.flushframe()  # clear frame

                for line in range(len(self._page)):
                    if textalign == "center":
                        x_pos = (self.W // 2) - ((len(self._page[line]) * self._text_size) // 2)
                    elif textalign == "right":
                        x_pos = self.W - len(self._page[line]) * self._text_size
                    y_pos = line * self._text_size
                    self._frame.text(self._page[line], x_pos, y_pos, self.COLORED)

                self.show()  # show framebuf line by line

    def progressbar(self, col_pos, row_pos, width, height, state=50, filled=False):
        width = width
        height = height
        columns, rows = [], []
        border = 2
        total_columns = self.get_res()[0] // self._text_size
        total_rows = self.get_res()[1] // self._text_size

        if self._device == "1in54_epd":
            colored = 0
        else:
            colored = 1

        for i in range(self.get_res()[0]):
            if not i % self._text_size:
                columns.append(i)

        for j in range(self.get_res()[1]):
            if not j % self._text_size:
                rows.append(j)

        if col_pos > total_columns - 1:
            index_columns = total_columns - 1
        else:
            index_columns = col_pos

        if row_pos > total_rows - 1:
            index_rows = total_rows - 1
        else:
            index_rows = row_pos

        x_0 = columns[index_columns]
        y_0 = rows[index_rows]

        self._frame.rect(x_0, y_0, width, height, colored)

        if state > 100:
            state = 100

        if state < 0:
            state = 0

        # draw progress according to state:
        if filled:
            for k in range(state):
                if not k % 8:
                    width_progress = int((width / 100) * k)
                    self._frame.fill_rect(x_0 + border, y_0 + border, width_progress - border, height - border * 2, colored)
                    self.show()

        else:
            for m in range(state):
                if not m % 8:
                    x_1 = (x_0 + border) + m
                    y_1 = y_0 + border
                    x_2 = (x_0 + border + width // 8) + m
                    y_2 = y_0 + height - (border + 1)

                    if x_2 < width:
                        self._frame.line(x_1 - 1, y_1, x_2 - 1, y_2, colored)
                        self._frame.line(x_1, y_1, x_2, y_2, colored)
                        self._frame.line(x_1 + 1, y_1, x_2 + 1, y_2, colored)
                        self.show()

    @staticmethod
    def calculate_gear_coordinates(radius, angles):
        coordinates = []
        for i in range(angles):
            angle = 2 * pi * i / angles
            x = radius * cos(angle)
            y = radius * sin(angle)
            coordinates.append((x, y))
        return coordinates

    def draw_gear(self, x_pos, y_pos, coordinates, rad):
        frame_x_pos = x_pos
        frame_y_pos = y_pos

        for x, y in coordinates:
            self.draw_circle(x=frame_x_pos + int(x), y=frame_y_pos + int(y), radius=rad, colored=self.COLORED, filled=1)

    def render_gear(self, x_pos, y_pos, len_in_frames, obj_r, points, points_r, wait):
        rad_shift = 0
        rad_moving = 0
        frames_coordinates = []
        radius = obj_r
        points = points

        # Generate gear coordinates for each frame:
        for i_frame in range(len_in_frames):
            self.flushframe()
            rotation_angle = 2 * pi * i_frame / len_in_frames
            rotated_coordinates = [(x * cos(rotation_angle) - y * sin(rotation_angle),
                                    x * sin(rotation_angle) + y * cos(rotation_angle))
                                   for x, y in self.calculate_gear_coordinates(radius, points)]  # obj size
            frames_coordinates.append(rotated_coordinates)

            if not i_frame % points_r:
                rad_shift = 1

            if rad_moving >= points_r:
                rad_shift = -1

            # Draw each frame:
            rad_moving += rad_shift
            self.draw_gear(x_pos, y_pos, rotated_coordinates, rad_moving)
            self.show()
            sleep_ms(wait)

    def draw_save_glyph(self, x, y):
        save_glyph = consts_mono_display.save_glyph  # save glyph 32x32
        img_fbuf_save_glyph = framebuf.FrameBuffer(save_glyph, 32, 32, framebuf.MONO_VLSB)
        if self._device == "1in54_epd":
            self._frame.fill(0)
            self._frame.blit(img_fbuf_save_glyph, x, y, self.COLORED)
        else:
            self._frame.blit(img_fbuf_save_glyph, x, y, self.UNCOLORED)
        self.show()
