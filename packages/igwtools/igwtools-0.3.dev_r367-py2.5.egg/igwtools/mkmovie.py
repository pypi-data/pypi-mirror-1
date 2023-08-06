import os, sys
import tempfile
import shutil
from optparse import OptionParser

def make_movie(filenames, moviefile, options = ""):
    # sort list of filenames
    filenames.sort()

    # create a temporary directory to store video frames
    tempd = tempfile.mkdtemp()

    #loop through all files
    for fname in filenames:
        # create image of each xyp file

        # load xyp file

        # save frame
        pass

    # Convert frames to movie
    cmd = "ffmpeg -i " +  tempd + "/frame%04d.pgm"  + options + moviefile
    os.system(cmd)

    # clean up the frame images and the temp directory
    shutil.rmtree(tempd)

def make_movie_entry():
    usage = """ %prog [options] FILE(s) """
    parser = OptionParser(usage=usage, 
                          version="%prog (igwtools) " + str(__version__))

    parser.add_option("-v", "--verbose", action="store_true",
      help = "be verbose")

    (options, args) = parser.parse_args()

    make_movie(args)

