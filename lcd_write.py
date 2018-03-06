import Adafruit_CharLCD as LCD

class LCD_writter(object):
    def __init__(self):
        lcd_rs        = 25  # Note this might need to be changed to 21 for older revision Pi's.
        lcd_en        = 24
        lcd_d4        = 23
        lcd_d5        = 17
        lcd_d6        = 18
        lcd_d7        = 22
        lcd_backlight = 4
        lcd_columns = 16
        lcd_rows    = 2

        self.lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,lcd_columns, lcd_rows, lcd_backlight)

    def clear_lcd(self):
        self.lcd.clear()

    def write_lcd(self,msg,line_number=1):
        self.lcd.message(msg)

