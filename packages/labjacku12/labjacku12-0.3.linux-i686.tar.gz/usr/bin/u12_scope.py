#!/usr/bin/python
"""
U12 scope

Based on:
https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/advanced/spectrum.py

Based on spectrum.py
Based on updating_plot.py
"""

# Major library imports
from labjack_u12 import LabjackU12
from enthought.chaco2.default_colormaps import gray, jet

import wx
from numpy import fabs, zeros, linspace, short, fromstring, hstack, transpose, array
from scipy import fft

# Enthought library imports
from enthought.enable2.api import Window
from enthought.enable2.example_support import DemoFrame, demo_main

# Chaco imports
from enthought.chaco2.api import Plot, ArrayPlotData, HPlotContainer
from enthought.chaco2.tools.api import PanTool, SimpleZoom

NUM_SAMPLES = 4096
SAMPLING_RATE = 8096
SPECTROGRAM_LENGTH = 10

l = LabjackU12.find_all().next()

class PlotFrame(DemoFrame):
    
    def _create_window(self):
        # Setup the spectrum plot
        frequencies = linspace(0., float(SAMPLING_RATE)/2, num=NUM_SAMPLES/2)
        self.spectrum_data = ArrayPlotData(frequency=frequencies)
        empty_amplitude = zeros(NUM_SAMPLES/2)
        self.spectrum_data.set_data('amplitude', empty_amplitude)

        self.spectrum_plot = Plot(self.spectrum_data)
        self.spectrum_plot.plot(("frequency", "amplitude"), name="Spectrum", color="red")
        self.spectrum_plot.padding = 50
        self.spectrum_plot.title = "Spectrum"
        spec_range = self.spectrum_plot.plots.values()[0][0].value_mapper.range
        spec_range.low = 0.0
        spec_range.high = 5.0
        self.spectrum_plot.index_axis.title = 'Frequency (hz)'
        self.spectrum_plot.value_axis.title = 'Amplitude'
        


        # Time Series plot
        times = linspace(0., float(NUM_SAMPLES)/SAMPLING_RATE, num=NUM_SAMPLES)
        self.time_data = ArrayPlotData(time=times)
        empty_amplitude = y_values = zeros(NUM_SAMPLES)
        self.time_data.set_data('amplitude', empty_amplitude)

        self.time_plot = Plot(self.time_data)
        self.time_plot.plot(("time", "amplitude"), name="Time", color="blue")
        self.time_plot.padding = 50
        self.time_plot.title = "Time"
        self.time_plot.index_axis.title = 'Time (seconds)'
        self.time_plot.value_axis.title = 'Amplitude'
        time_range = self.time_plot.plots.values()[0][0].value_mapper.range
        time_range.low = -0.2
        time_range.high = 0.2
        
        # Spectrogram plot
        spectrogram_data = zeros(( NUM_SAMPLES/2, SPECTROGRAM_LENGTH))
        self.spectrogram_plotdata = ArrayPlotData()
        self.spectrogram_plotdata.set_data('imagedata', spectrogram_data)
        spectrogram_plot = Plot(self.spectrogram_plotdata)
        spectrogram_time = linspace(0., float(SPECTROGRAM_LENGTH*NUM_SAMPLES)/float(SAMPLING_RATE), num=SPECTROGRAM_LENGTH)
        spectrogram_freq = linspace(0., float(SAMPLING_RATE/2), num=NUM_SAMPLES/2)
        spectrogram_plot.img_plot('imagedata',
                                  name='Spectrogram',
                                  xbounds=spectrogram_time,
                                  ybounds=spectrogram_freq,
                                  colormap=jet,
                                  )
        range_obj = spectrogram_plot.plots['Spectrogram'][0].value_mapper.range
        range_obj.high = 5
        range_obj.low = 0.0
        spectrogram_plot.title = 'Spectrogram'
        self.spectrogram_plot = spectrogram_plot
        
        container = HPlotContainer()
        container.add(self.spectrum_plot)
        container.add(self.time_plot)
        container.add(spectrogram_plot)
        
        # Set the timer to generate events to us
        timerId = wx.NewId()
        self.timer = wx.Timer(self, timerId)
        self.Bind(wx.EVT_TIMER, self.onTimer, id=timerId)
        self.timer.Start(2500.0, wx.TIMER_CONTINUOUS)
        return Window(self, -1, component=container)

    def onTimer(self, event):
        spectrum, time = get_audio_data()
        self.spectrum_data.set_data('amplitude', spectrum)
        self.time_data.set_data('amplitude', time)
        spectrogram_data = self.spectrogram_plotdata.get_data('imagedata')
        spectrogram_data = hstack((spectrogram_data[:,1:], transpose([spectrum])))

        
        self.spectrogram_plotdata.set_data('imagedata', spectrogram_data)
        self.spectrum_plot.request_redraw()
        return


def get_audio_data():
        chans=(8,8,8,8)
        gains=(5,5,5,5)
        l.burst(channels=chans, gains=gains,
                num_scans=NUM_SAMPLES/4, rate=SAMPLING_RATE/4)
        d = []
        for i in range(NUM_SAMPLES/4/16):
            for v in l.bulk_read(chans, gains):
                d.append(v[0])
        l.bulk_stop()
        dat = array(d).reshape((NUM_SAMPLES))
        #dat /= max(abs(dat))
        return abs(fft(dat))[:NUM_SAMPLES/2], dat
        

if __name__ == "__main__":
    demo_main(PlotFrame, size=(900,500), title="Audio Spectrum")

# EOF
