
from setuptools import setup

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
	name="lyricwiki",
	version = "0.1." + get_build(),
	description = "Download lyrics from LyricWiki",
	license = "gpl3",
	author = "Amr Hassan",
	author_email = "amr.hassan@gmail.com",
	scripts = ["lyrics"],
	py_modules = ["lyricwiki"]
	)
