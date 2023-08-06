# -*- coding: utf-8 -*-
#       lyricwiki.py
#       
#       Copyright 2009 Amr Hassan <amr.hassan@gmail.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import json
import urllib

def _download(args):
	"""
		Downloads the json response and returns it
	"""
	
	base = "http://lyrics.wikia.com/api.php?"
	
	str_args = {}
	for key in args:
		str_args[key] = args[key].encode("utf-8")
	
	args = urllib.urlencode(str_args)
	
	return urllib.urlopen(base + args).read()

def _get_lyrics(page_title):
	args = {"action": "query",
		"prop": "revisions",
		"rvprop": "content",
		"titles": page_title,
		"format": "json",
		}
	
	revisions = json.loads(_download(args))["query"]["pages"].popitem()[1]
	
	if not "revisions" in revisions:
		return None
		
	content = revisions["revisions"][0]["*"]
	
	if content.startswith("#Redirect"):
		n_title = content[content.find("[[") + 2:content.rfind("]]")]
		return _get_lyrics(n_title)
	
	if "<lyrics>" in content:
		return content[content.find("<lyrics>") + len("<lyrics>") : content.find("</lyrics>")].strip()
	elif "<lyric>" in content:
		return content[content.find("<lyric>") + len("<lyric>") : content.find("</lyric>")].strip()

def get_lyrics(artist, title):
	"""
		Get lyrics by artist and title
	"""
	
	return _get_lyrics("%s:%s" %(artist.title(), title.title()))
