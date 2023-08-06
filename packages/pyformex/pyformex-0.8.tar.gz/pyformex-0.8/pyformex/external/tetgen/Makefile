# $Id$
# Makefile for tetgen

NAME=tetgen
VERSION= 1.4.2
NAMEVER= ${NAME}${VERSION}
MYNAMEVER= ${NAME}-${VERSION}
ARCHIVE= ${NAMEVER}.tar.gz
URI= http://www.wias-berlin.de/people/si/${ARCHIVE}
PATCHFILE= ${MYNAMEVER}.patch

# The remainder is fairly generic
GET= ${ARCHIVE}
UNPACK= ${NAMEVER}
PATCH= ${NAMEVER}/makefile
BUILD= ${NAMEVER}/${NAME}


#.phony: default get unpack patch build install clean all

default: build
all: get unpack patch build install clean
get: ${GET}
unpack: ${UNPACK}
patch: ${PATCH} 
build: ${BUILD}


${GET}:
	wget ${URI}

${UNPACK}: ${ARCHIVE}
	tar xvzf $<
	touch $@

${PATCH}: ${UNPACK}
	pushd ${UNPACK}; patch -p0 < ../${PATCHFILE}; popd

${BUILD}: ${PATCH}
	make -C ${UNPACK}


install: ${BUILD}
	/usr/bin/install -m0755 $< /usr/local/bin

clean:
	rm -rf ${UNPACK}
	rm -f ${GET}

# End




