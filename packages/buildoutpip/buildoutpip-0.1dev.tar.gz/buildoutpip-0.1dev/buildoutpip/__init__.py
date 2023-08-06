import urllib

def extension(buildout):
	if buildout['buildout'].has_key('requirements'):
		# pip part definition
		for req in buildout['buildout']['requirements'].split():
			if 'http' in req:
				f = urllib.urlopen(req)
				for line in f.readlines():
					# check if line is a find-links item
					if '--find-links' in line:
						section, url = line.split('=')
						url = url.strip('=')
						if buildout['buildout'].has_key('find-links'):
							buildout['buildout']['find-links'] += '\n%s'%url
						else:
							buildout['buildout']['find-links'] = '\n%s'%url
					else:
						buildout['buildout']['eggs'] += line
