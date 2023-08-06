version = '1.1.0'
release = True
revision = ''

if release:
    fullVersion = '%s' % (version,)
else:
    fullVersion = '%s-%s' % (version, revision)
    
titleVersion = 'v%s' % (fullVersion,)
