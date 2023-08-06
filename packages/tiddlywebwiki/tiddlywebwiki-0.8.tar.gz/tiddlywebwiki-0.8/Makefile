# Simple Makefile for some common tasks. This will get 
# fleshed out with time to make things easier on developer
# and tester types.
.PHONY: test dist upload

all:
	@echo "No target"

empty:
	wget http://tiddlywiki.com/empty.html -O tiddlywebwiki/empty.html

status_plugin:
	wget http://github.com/tiddlyweb/tiddlyweb-plugins/raw/master/status/status.py -O status.py

wikklytextrender_plugin:
	wget http://github.com/tiddlyweb/tiddlyweb-plugins/raw/master/wikklytextrender/wikklytextrender.py -O wikklytextrender.py

twebplugins: status_plugin wikklytextrender_plugin

ServerSideSideSavingPlugin:
	wget http://svn.tiddlywiki.org/Trunk/association/plugins/ServerSideSavingPlugin.js -O tiddlywebwiki/ServerSideSavingPlugin.js
	wget http://svn.tiddlywiki.org/Trunk/association/plugins/ServerSideSavingPlugin.js.meta -O tiddlywebwiki/ServerSideSavingPlugin.js.meta

TiddlyWebAdaptor:
	wget http://svn.tiddlywiki.org/Trunk/association/adaptors/TiddlyWebAdaptor.js -O tiddlywebwiki/TiddlyWebAdaptor.js
	wget http://svn.tiddlywiki.org/Trunk/association/adaptors/TiddlyWebAdaptor.js.meta -O tiddlywebwiki/TiddlyWebAdaptor.js.meta

TiddlyWebConfig:
	wget http://svn.tiddlywiki.org/Trunk/association/plugins/TiddlyWebConfig.js -O tiddlywebwiki/TiddlyWebConfig.js
	wget http://svn.tiddlywiki.org/Trunk/association/plugins/TiddlyWebConfig.js.meta -O tiddlywebwiki/TiddlyWebConfig.js.meta

twikiplugins: ServerSideSideSavingPlugin TiddlyWebAdaptor TiddlyWebConfig

remotes: empty twebplugins twikiplugins

clean:
	rm -r dist || true

test:
	py.test -x test

dist: test
	python setup.py sdist

upload: clean remotes test pypi peermore

pypi: 
	python setup.py sdist upload

peermore:
	scp -P 8022 dist/tiddlywebwiki-*.gz cdent@tiddlyweb.peermore.com:public_html/tiddlyweb.peermore.com/dist
	scp -P 8022 CHANGES cdent@tiddlyweb.peermore.com:public_html/tiddlyweb.peermore.com/dist/CHANGES.tiddlywebwiki
