VERSION = $(shell dpkg-parsechangelog | sed -n 's/^Version: //p')
DIST = $(shell dpkg-parsechangelog | sed -n 's/^Distribution: //p')

all: build

build:
	sed -i "/ version=/s/='[^']*'/='$(VERSION)'/" setup.py

install:

clean:

test:
	debuild -I.git -I*.ex -b -us -uc && sudo debi

release:
	debuild -I.git -I*.ex -tc && debrelease --dput $(DIST)-test

