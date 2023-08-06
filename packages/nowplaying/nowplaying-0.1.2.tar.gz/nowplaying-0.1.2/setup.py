
from distutils.core import setup

import os
def get_build():
	path = "./.build"
	if os.path.exists(path):
		fp = open(path, "r")
		build = eval(fp.read())
		fp.close()
	else:
		build = 1
	
	fp = open(path, "w")
	fp.write(str(build+1))
	fp.close()
	
	return unicode(build)
	
setup(
	name="nowplaying",
	version = "0.1." + get_build(),
	description = "Simple now-playing lookup for D-Bus enabled players",
	license = "gpl3",
	author = "Amr Hassan",
	author_email = "amr.hassan@gmail.com",
	packages = ["nowplaying"],
	)
