import py2tex
def translate (name, outfile):
    file = Interpret(filename)
    outfile.write (file.translation () [0])
    while file.translate () != None:
	for scrap in file.translation (): outfile.write (scrap)
    file.close ()
