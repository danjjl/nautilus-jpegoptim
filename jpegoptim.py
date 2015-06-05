#!/usr/bin/python
import subprocess
import os

from gi.repository import Gtk, GObject

class MyWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Compress photos")
        self.set_icon(Gtk.IconTheme.get_default().load_icon('eog', 128, 0))

        self.box_main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(self.box_main)

        self.compression = Gtk.HScale(adjustment=Gtk.Adjustment(value=100, lower=0, upper=100, step_incr=1))
        self.compression.set_digits(0)
        self.box_main.pack_start(self.compression, True, True, 0)


        self.box_size = Gtk.Box(spacing=6)
        self.box_main.pack_start(self.box_size, True, True, 0)

        self.progressbar = Gtk.ProgressBar()
        self.box_size.pack_start(self.progressbar, True, True, 0)
        self.size_label = Gtk.Label("Size reduction:    ")
        self.box_size.pack_start(self.size_label, True, True, 0)


        self.box_button = Gtk.Box(spacing=6)
        self.box_main.pack_start(self.box_button, True, True, 0)

        self.button_compress = Gtk.Button(label="Compress photos")
        self.button_compress.connect("clicked", self.compress)
        self.box_button.pack_start(self.button_compress, True, True, 0)

        self.button_calculate = Gtk.Button(label="Calculate size reducation")
        self.button_calculate.connect("clicked", self.calculate)
        self.box_button.pack_start(self.button_calculate, True, True, 0)

        self.files = " ".join("'%s'" % f for f in os.environ["NAUTILUS_SCRIPT_SELECTED_FILE_PATHS"].splitlines())
        self.num_files = len(self.files.split())


    def compress(self, widget):
        self.action = ''
        self.text   = 'Done'        
        self.jpegoptim()


    def calculate(self, widget):
        self.action = '--noaction'
        self.text   = 'Size'
        self.jpegoptim()


    def jpegoptim(self):
        #TODO find how to disable buttons when working
        self.fraction = 0
        self.progressbar.set_fraction(0.0)

        task = self.work()
        GObject.idle_add(task.next)


    def work(self):
        out = subprocess.Popen('jpegoptim '+ self.action +' --totals -m'+ str(int(self.compression.get_value())) + ' ' + self.files, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(out.stdout.readline, ''):
            self.fraction = self.fraction + 1.0
            self.progressbar.set_fraction(self.fraction/self.num_files)
            yield True
            
        retval = out.wait()
        self.line =  line.split()
        
        self.progressbar.set_fraction(1.0)
        self.size_label.set_text(self.text + " reduction: " + self.line[4])
        yield False


GObject.threads_init()
win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
