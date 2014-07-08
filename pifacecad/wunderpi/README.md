Get your weather from a weather station just blocks from your home.
Go to http://www.wunderground.com/wundermap/ to find a station near you!

Based on weather.py from the pifacecad examples, expanded into a
fully-customizable program by Zach White <zwhite@darkstar.frop.org>.

Why Use This?
=============

You may be wondering why you should use this when weather.py from the
examples seems to do the same thing. The answer is that they achieve
seperate goals. If you just want to build the weather gadget and have
it to use, wunderpi probably does everything you need and you can have 
it running in minutes.

However, all that flexibility comes at a cost. If you want to understand
how it works it's easier to understand weather.py since there are fewer
hooks for customization.

Getting Started
===============

To get started you'll need to create a config file. By default this
program looks in /etc/flexible_weather.conf, but you can specify a 
different filename on the command line. You should have received an 
example configuration with this program- it is heavily commented and is
your best reference.

At a minimum you need to set the following values for your environment:

    DisplayFormat
        This is the default format to display on startup. The default
        config file has two options, "US" and "Metric" but it can be any
        of the formats from the [DisplayFormats] section.

    RefreshInterval
        How long since last fetching data from wunderground before we
        attempt to refresh our data. Please be kind to wunderground, who
        is providing a free service to you, and don't set this to less
        than 300 seconds.

    [DisplayFormats]
        This is an entire section which defines which display formats are
        available to cycle through. You can use this to swap between
        US and Metric units (the default configuration) or to cycle
        through many datapoints. See the configuration file for more
        information.

    [WeatherStations]
        This section of the config defines the weather stations to
        include.  The key is the name of the weather station (Usually
        the city or neighborhood the station is located in) and the
        value is the station's ID. You can find your local station's
        ID here:

            http://www.wunderground.com/wundermap/

Packaging
=========

If you would like to package this software you will also need to package the
pyfacecad package, which is not available on pypi at this time. Cloning the
repository and running "setup.py sdist" is pretty straightforward, and should
not require extraordinary effort. You can clone the pifacecad repository at
this URL:

    https://github.com/piface/pifacecad.git
