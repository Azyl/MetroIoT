import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008


class ADC_reader:
    def __init__(self):

        # Software SPI configuration:
        #CLK  = 18
        #MISO = 23
        #MOSI = 24
        #CS   = 25
        #mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

        # Hardware SPI configuration:
        self.SPI_PORT   = 0
        self.SPI_DEVICE = 0
        self.mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(self.SPI_PORT, self.SPI_DEVICE))

        self.ADC_moisture = 7
        self.ADC_temperature = 1
        self.ADC_humidity = 0
        self.ADC_ligth = 2
        self.Reference_mV = 3.3

    def read_ADC_channel(self, channel_number):
        return self.mcp.read_adc(channel_number)

    def get_soil_moisture(self, channel_number = self.ADC_moisture):
        return read_ADC_channel(channel_number)

    def get_air_humidity(self,channel_number = self.ADC_humidity):
        return read_ADC_channel(channel_number)

    def get_ambient_ligth(self,channel_number = self.ADC_ligth):
        return read_ADC_channel(channel_number)

    def get_ambient_temperature(self,channel_number = self.ADC_temperature):
        return read_ADC_channel(channel_number)
