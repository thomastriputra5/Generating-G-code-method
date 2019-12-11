import inkex

class TugasAkhir(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)

        self.OptionParser.add_option("-d", "--directory",                       action="store", type="string",          dest="directory",                           default="",                             help="Output directory")
        self.OptionParser.add_option("-f", "--filename",                        action="store", type="string",          dest="file",                                default="output.gcode",                 help="File name")            
        self.OptionParser.add_option("",   "--add-numeric-suffix-to-filename",  action="store", type="inkbool",         dest="add_numeric_suffix_to_filename",      default=False,                          help="Add numeric suffix to file name")  
                
        self.OptionParser.add_option("",   "--laseron",                         action="store", type="string",          dest="laser_command",                       default="M03",                          help="Laser gcode command")
        self.OptionParser.add_option("",   "--laseroff",                        action="store", type="string",          dest="laser_off_command",                   default="M05",                          help="Laser gcode end command")       
    
    def effect(self):
        self.error("Hello World")


tugas_akhir = TugasAkhir()
tugas_akhir.affect()