# mono_display
## This is a primitive class to interface with my favourite monochrome displays with the help of available drivers so with it, I can quickly show stuff on a display in my future projects. [ESP32]

# tested on ESP32S2, ESP32S3R8

## works with:
  - st7920
  - pcd8544
  - 1.54" e-paper
  - ssd1306
  - ssd1309
  - sh1106
  - st7735


## methods:
- draw_rssi(x, y, state=-88, scale=1)
- draw_battery_state(x, y, charging=False, state=50.0, scale=1)
- show_scrollable_log(textalign)
- log_rtc(rtc_datetime)
- render_gear(x_pos, y_pos, len_in_frames, obj_r, points, points_r, wait)
- draw_save_glyph(x, y)
- progressbar(col_pos, row_pos, width, height, state=50, filled=False)
- lcd_backlight(0-1024, in case of PCD8544: 0-1)
- set_oled_brightness(0-255)
- trace(frequency, phase, amplitude, time_ms, colored)
- draw_circle(x, y, r, colored, filled)
- draw_switch(x, y, state, scale)
- log(text, textalign)
- slow mode in log() draws 4 lines of text at a time to save time when an epaper device updates really slowly...

![IMG_2193](https://github.com/sz-szabolcs/mono_display/assets/117392474/47b9efe6-e585-4c18-ba6e-be6ad47b578e)
