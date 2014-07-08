from sys import version_info
if version_info[0] < 3:
    print('Weather only works with python3.')
    exit(1)

import logging
from pifacecad import LCDBitmap
from time import strftime, time
from urllib.request import urlopen
from xml.etree.ElementTree import XML


CUSTOM_BITMAPS = [
    LCDBitmap([0x0c, 0x12, 0x12, 0x0c, 0x00, 0x00, 0x00, 0x00]),  # Degrees
    LCDBitmap([0x00, 0x0e, 0x15, 0x17, 0x11, 0x0e, 0x00, 0x00]),  # Clock
    LCDBitmap([0x04, 0x04, 0x04, 0x04, 0x0e, 0x0e, 0x0e, 0x00]),  # Thermometer
    LCDBitmap([0x00, 0x0f, 0x03, 0x05, 0x09, 0x10, 0x00, 0x00]),  # Wind
    LCDBitmap([0x0c, 0x1f, 0x0f, 0x00, 0x02, 0x08, 0x04, 0x00]),  # Rain cloud
    LCDBitmap([0x00, 0x15, 0x0e, 0x1f, 0x0e, 0x15, 0x00, 0x00]),  # Sun
]

logger = logging.getLogger('wunderpi')
logger.setLevel(logging.DEBUG)


class WeatherStation(object):
    """Representation of a weatherstation from wunderground."""
    def __init__(self, verbose, location, weather_id, refresh_interval, url_prefix):
        logger.debug('Instantating WeatherStation("%s")' % '", "'.join(map(repr, (verbose, location, weather_id, url_prefix))))
        self.location = location
        self.refresh_interval = refresh_interval
        self.weather_id = weather_id
        self.url_prefix = url_prefix
        self._xmltree_updated = 0
        self._xmltree = None

    def _get_data(self):
        """Returns the XML data from wunderground"""
        url = self.url_prefix + self.weather_id
        logger.info('Updating weather data for %s' % self.location)
        logger.debug('Fetching XML data from %s', url)
        return urlopen(url).read()

    def _find_datatype(self, data):
        """Returns data coerced to float() or int() if it can."""
        if hasattr(data, 'isnumeric') and data.isnumeric():
            return int(data)

        try:
            return float(data)

        except ValueError:
            return data

        except TypeError:
            return data

    def update(self, weatherdisplay, retry=0):
        if (time() - self._xmltree_updated) > self.refresh_interval:
            logger.info('Updating weather data...')
            weatherdisplay.clear()
            weatherdisplay.write('Updating\n' + self.location + ' %1')

            self._xmltree_updated = time()
            self._xmltree = XML(self._get_data())

            # Populate the weather station values
            nodes = self._xmltree.findall('current_observation')

            if not nodes:
                if retry > 2:
                    logger.error('Could not fetch station data!')
                    exit(1)

                self.update(weatherdisplay, retry + 1)

            # Walk the first two levels to populate our observations. Some day
            # in the future we should walk this recursively.
            for node in nodes[-1]:
                if node.tag not in self.__dict__:
                    self.__dict__[node.tag] = self._find_datatype(node.text)

                for child in node:
                    key = '_'.join((node.tag, child.tag))
                    self.__dict__[key] = self._find_datatype(child.text)

            # Populate a few other keys that are nice to have
            self.__dict__['date'] = strftime('%Y-%m-%d')
            self.__dict__['date_year'] = strftime('%Y')
            self.__dict__['date_month'] = strftime('%m')
            self.__dict__['date_day'] = strftime('%d')
            self.__dict__['time'] = strftime('%H:%M')
            self.__dict__['time_hour'] = strftime('%H')
            self.__dict__['time_minute'] = strftime('%M')

        else:
            left = self.refresh_interval - (time() - self._xmltree_updated)
            logger.debug('Refresh not yet expired, %s seconds left...', left)


class WeatherDisplay(object):
    """Class responsible for actually displaying the weather data on the cad"""
    def __init__(self, cad, display_format, display_formats, stations,
                 station_index=0, verbose=False):
        arglist = map(repr, (cad, display_format, display_formats, stations,
                             station_index, verbose))
        logger.debug('Instaniating WeatherDisplay("%s")', '", "'.join(arglist))

        # Map arguments to attributes
        self.cad = cad
        self.display_format = display_format
        self.display_formats = display_formats
        self.stations = stations
        self.station_index = station_index
        self.verbose = verbose

        # Prepare the LCD
        self.cad.lcd.backlight_on()
        self.cad.lcd.blink_off()
        self.cad.lcd.cursor_off()

        # Store our custom bitmaps
        for i, bitmap in enumerate(CUSTOM_BITMAPS):
            self.cad.lcd.store_custom_bitmap(i, bitmap)

    def _send_data(self, data):
        """Sends data to the LCD."""
        self.cad.lcd.send_data(data)
        self.cad.lcd._cursor_position[0] += 1

    @property
    def current_station(self):
        """Returns the current station dict."""
        return self.stations[self.station_index]

    def change_format(self, event=None):
        """Change to the next available format."""
        formats = sorted(self.display_formats)
        format = formats.index(self.display_format)
        self.display_format = formats[(format + 1) % len(formats)]
        self.update()

    def next_station(self, event=None):
        """Display the next weather station's data."""
        self.station_index = (self.station_index + 1) % len(self.stations)
        self.update()

    def previous_station(self, event=None):
        """Display the previous weather station's data."""
        self.station_index = (self.station_index - 1) % len(self.stations)
        self.update()

    def clear(self):
        """Clear the display"""
        self.cad.lcd.clear()

        # Print out (and log, if enabled) a message that's exactly as wide
        # as the screen so that when we write what has been output to the
        # screen we can see what overflows.
        logger.info('Display cleared.')
        logger.info(16 * '-')

    def write(self, string):
        """
            Writes a string to the LCD.

            This function will write the specified string to the LCD. If it
            encounters the special character % followed by one of the numerals
            0-7 it will print the custom bitmap stored at that location instead.

            Use %% to print a literal percent sign on the LCD.

            Example::

                self.write('It is 15%0F outside')
        """
        self.cad.lcd.set_ddram_address()

        is_bitmap = False
        for char in string:
            if is_bitmap and char in '01234567':
                is_bitmap = False
                self._send_data(int(char))

            elif not is_bitmap and char == '%':
                is_bitmap = True

            elif char == '\n':
                self.cad.lcd.set_cursor(0, 1)

            else:
                self._send_data(ord(char))

    def update(self, event=None):
        """Update the current station and refresh the display"""
        self.current_station.update(self)
        self.clear()

        # Write the lines to the LCD
        for line in self.display_formats[self.display_format].split('\\n'):
            line = line.format(**self.current_station.__dict__)
            self.write(line + '\n')
            logger.info(line.replace('%%', '%'))

    def close(self):
        """Clear the LCD and turn off the backlight."""
        self.clear()
        self.cad.lcd.backlight_off()
