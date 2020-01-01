import sys
sys.path.append('/usr/share/inkscape/extensions')
sys.path.append('/snap/inkscape/5874/share/inkscape/extensions')

import inkex


class TugasAkhir(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)

        self.OptionParser.add_option("-d", "--directory", action="store", type="string", dest="directory", default="/home/",
                                     help="Output directory")
        self.OptionParser.add_option("-f", "--filename", action="store", type="string", dest="file",
                                     default="output.gcode", help="File name")
        self.OptionParser.add_option("", "--add-numeric-suffix-to-filename", action="store", type="inkbool",
                                     dest="add_numeric_suffix_to_filename", default=False,
                                     help="Add numeric suffix to file name")


        # laser configuration
        self.OptionParser.add_option("", "--laseron", action="store", type="string", dest="laser_command",
                                     default="M03", help="Laser gcode command")
        self.OptionParser.add_option("", "--laseroff", action="store", type="string", dest="laser_off_command",
                                     default="M05", help="Laser gcode end command")

        # export raster configurations
        self.OptionParser.add_option("", "--raster-method", action="store", type="int",
                                     dest="raster_method", default=1)
    
    def effect(self):
        if self.options.raster_method == 1:  # R2L - Raster 2 Laser
            from raster2laser_gcode import GcodeExport

            e = GcodeExport()
            # e.options.directory = self.options.directory
            # e.options.filename = self.options.filename
            e.affect()
        elif self.options.raster_method == 2:  # JTPL - JTP Laser Tool
            from laser import laser_gcode

            e = laser_gcode()
            # e.options.directory = self.options.directory
            # e.options.filename = self.options.filename
            e.affect()


if __name__ == '__main__':
    tugas_akhir = TugasAkhir()
    tugas_akhir.affect()