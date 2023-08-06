"""
Video file handler, using GStreamer.

Requires PyGST.
"""

# Vodoo import dance.
import pygtk
pygtk.require("2.0")
import gobject
gobject.threads_init()
import pygst
pygst.require("0.10")
import gst
import gtk

from presenter.handlers.base import FileHandler

class VideoFileHandler(FileHandler):
    """
    A file handler for video files
    """

    mime_types = [
        'application/mxf', 'application/ogg', 'application/ram',
        'application/sdp', 'application/smil', 'application/smil+xml',
        'application/vnd.ms-wpl', 'application/vnd.rn-realmedia',
        'application/x-extension-m4a', 'application/x-extension-mp4',
        'application/x-flac', 'application/x-flash-video',
        'application/x-matroska', 'application/x-netshow-channel',
        'application/x-ogg', 'application/x-quicktime-media-link',
        'application/x-quicktimeplayer', 'application/x-shorten',
        'application/x-smil', 'application/xspf+xml', 'audio/3gpp', 'audio/ac3',
        'audio/AMR', 'audio/AMR-WB', 'audio/basic', 'audio/midi', 'audio/mp4',
        'audio/mpeg', 'audio/mpegurl', 'audio/ogg', 'audio/prs.sid',
        'audio/vnd.rn-realaudio', 'audio/x-ape', 'audio/x-flac', 'audio/x-gsm',
        'audio/x-it', 'audio/x-m4a', 'audio/x-matroska', 'audio/x-mod',
        'audio/x-mp3', 'audio/x-mpeg', 'audio/x-mpegurl', 'audio/x-ms-asf',
        'audio/x-ms-asx', 'audio/x-ms-wax', 'audio/x-ms-wma',
        'audio/x-musepack', 'audio/x-pn-aiff', 'audio/x-pn-au',
        'audio/x-pn-realaudio', 'audio/x-pn-realaudio-plugin', 'audio/x-pn-wav',
        'audio/x-pn-windows-acm', 'audio/x-realaudio', 'audio/x-real-audio',
        'audio/x-sbc', 'audio/x-scpls', 'audio/x-speex', 'audio/x-tta',
        'audio/x-wav', 'audio/x-wavpack', 'audio/x-vorbis',
        'audio/x-vorbis+ogg', 'audio/x-xm', 'image/vnd.rn-realpix',
        'image/x-pict', 'misc/ultravox', 'text/google-video-pointer',
        'text/x-google-video-pointer', 'video/3gpp', 'video/dv', 'video/fli',
        'video/flv', 'video/mp4', 'video/mp4v-es', 'video/mpeg',
        'video/msvideo', 'video/ogg', 'video/quicktime', 'video/vivo',
        'video/vnd.divx', 'video/vnd.rn-realvideo', 'video/vnd.vivo',
        'video/x-anim', 'video/x-avi', 'video/x-flc', 'video/x-fli',
        'video/x-flic', 'video/x-flv', 'video/x-m4v', 'video/x-matroska',
        'video/x-mpeg', 'video/x-ms-asf', 'video/x-ms-asx', 'video/x-msvideo',
        'video/x-ms-wm', 'video/x-ms-wmv', 'video/x-ms-wmx', 'video/x-ms-wvx',
        'video/x-nsv', 'video/x-ogm+ogg', 'video/x-theora+ogg',
        'video/x-totem-stream', 'x-content/video-dvd', 'x-content/video-vcd',
        'x-content/video-svcd',
    ]

    def __init__(self, uri):
        super(VideoFileHandler, self).__init__(uri)

        self.widgets_queue = []
        self.widgets_sinks = {}
        self.sinks_widgets = {}

        self.last_state = gst.STATE_NULL

        # Setup GStreamer pipeline.
        self.pipeline = gst.Pipeline()

        playbin = gst.element_factory_make("playbin", "player")
        playbin.set_property("uri", uri)
        self.pipeline.add(playbin)

        self.sink_tee = gst.element_factory_make("tee")

        self.sink_bin = gst.Bin()
        self.sink_bin.add(self.sink_tee)

        self.sink_bin.add_pad(gst.GhostPad("sink", self.sink_tee.get_pad("sink")))

        playbin.set_property("video-sink", self.sink_bin)

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        bus.connect("sync-message::element", self.on_sync_message)

    def add_video_sink(self, widget):
        queue = gst.element_factory_make("queue")
        sink = gst.element_factory_make("autovideosink")

        self.sinks_widgets[widget] = (queue, sink)

        current_state = self.sink_bin.get_state()[1]

        pad = self.sink_tee.get_pad("sink")
        if current_state == gst.STATE_PLAYING:
            pad.set_blocked(True)

        self.sink_bin.add(queue, sink)
        gst.element_link_many(self.sink_tee, queue, sink)

        if current_state == gst.STATE_PLAYING:
            self.sink_bin.set_state(gst.STATE_PLAYING)
            pad.set_blocked(False)

    def add_video_control(self, widget):
        # Add the widget to the queue for connection with a videosink.
        self.widgets_queue.append(widget)

        self.add_video_sink(widget)

    def remove_video_control(self, widget):
        if widget in self.widgets_queue:
            self.widgets_queue.remove(widget)
        else:
            queue, sink = self.sinks_widgets[widget]
            gst.element_unlink_many(self.sink_tee, queue, sink)

            self.sink_bin.remove(queue, sink)
            del queue, sink

    def make_video_control(self):
        widget = gtk.DrawingArea()
        widget.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("black"))
        widget.connect('realize', self.add_video_control)
        widget.connect('unrealize', self.remove_video_control)
        return widget

    def get_editor_control(self):
        editor = gtk.VBox()

        video_widget = self.make_video_control()
        editor.pack_start(video_widget, True)

        buttons = gtk.HBox()
        editor.pack_end(buttons, False)

        play_button = gtk.Button(stock=gtk.STOCK_MEDIA_PLAY)
        play_button.connect('clicked', self.on_play)
        buttons.add(play_button)

        stop_button = gtk.Button(stock=gtk.STOCK_MEDIA_STOP)
        stop_button.connect('clicked', self.on_stop)
        buttons.add(stop_button)

        return editor

    def get_output_control(self):
        widget = self.make_video_control()
        return widget

    def change_state(self, state):
        self.last_state = state
        self.pipeline.set_state(state)

    def on_play(self, button):
        self.change_state(gst.STATE_PLAYING)

    def on_stop(self, button):
        self.change_state(gst.STATE_READY)

    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            print 'Error: %s' % err, debug
            self.pipeline.set_state(gst.STATE_NULL)

    def on_sync_message(self, bus, message):
        if message.structure is None:
            return
        message_name = message.structure.get_name()
        if message_name == "prepare-xwindow-id":
            # Assign the sink windows.
            imagesink = message.src
            name = imagesink.get_name()

            widget = self.widgets_sinks.get(name)
            if not widget:
                assert self.widgets_queue, 'no widgets waiting to be connected!'
                widget = self.widgets_queue.pop(0)

            assert widget.window, '%s needs to be realized.' % widget

            imagesink.set_property("force-aspect-ratio", True)

            try:
                window_id = widget.window.xid
            except AttributeError:
                window_id = widget.window.handle

            imagesink.set_xwindow_id(window_id)

            self.widgets_sinks[name] = widget

