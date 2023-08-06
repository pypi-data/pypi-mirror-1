
from distutils.core import setup
import glob

import os
def get_build():
	path = "./.build"
	
	if os.path.exists(path):
		fp = open(path, "r")
		build = eval(fp.read())
		if os.path.exists("./.increase_build"):
			build += 1
		fp.close()
	else:
		build = 1
	
	fp = open(path, "w")
	fp.write(str(build))
	fp.close()
	
	return unicode(build)

setup(
	name="nowplaying",
	version = "0.2." + get_build(),
	description = "Simple now-playing lookup for D-Bus enabled players",
	license = "gpl3",
	author = "Amr Hassan",
	author_email = "amr.hassan@gmail.com",
	packages = ["np"],
    py_modules = ["nowplaying"],
    data_files = [("/usr/share/python-nowplaying/players", glob.glob("players/*"))]
	)
