from _sndfile import sndfile_version, Format
from _sndfile import *
import _sndfile

print sndfile_version()

f = Format(type='wav')
print f

majors = available_file_formats()
print available_encoding('wav')
