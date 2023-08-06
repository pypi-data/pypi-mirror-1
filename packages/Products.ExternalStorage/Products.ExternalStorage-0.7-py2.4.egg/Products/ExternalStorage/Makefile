NAME=ExternalStorage
MAJOR_VERSION=0
MINOR_VERSION=6
RELEASE_TAG=
PACKAGE_NAME=${NAME}-${MAJOR_VERSION}.${MINOR_VERSION}${RELEASE_TAG}

PYTHON=/usr/bin/python
TMPDIR=/tmp

ZOPE=/usr/local/zope
SOURCE_DIR=${ZOPE}/source
CURDIR=${SOURCE_DIR}/${NAME}
#BASE_DIR=${CURDIR}/..
BASE_DIR=${SOURCE_DIR}
SOFTWARE_HOME=${ZOPE}/Zope/2.7/Zope/lib/python
INSTANCE_HOME=${ZOPE}/instance/zope2.7-cmf1.5-plone2.1
PACKAGES=${NAME}

RM=rm -f
RMRF=rm -rf
FIND=find
XARGS=xargs
CD=cd
LN=ln -sfn
CP=cp
TAR=tar
MKDIR=mkdir -p

.PHONY: clean test reindent reindent_clean sdist
.PHONY: default

# The default step (invoked when make is called without a target)
default: clean test

clean:
	find . \( -name '*~' -o -name '*.py[co]' -o -name '*.bak' \) -exec rm {} \; -print

# Grab reindent.pt from Python Tools CVS:
# http://cvs.sourceforge.net/viewcvs.py/python/python/dist/src/Tools/scripts
reindent:
	~/scripts/reindent.py -r -v .

test:
	export INSTANCE_HOME=${INSTANCE_HOME}; \
	export SOFTWARE_HOME=${SOFTWARE_HOME}; \
	cd ${CURDIR}/tests && ${PYTHON} runalltests.py

# Create a source distribution file (implies clean).
sdist: reindent clean sdist_tgz

# Create a tgz archive file as a source distribution.
sdist_tgz:
	echo "${MAJOR_VERSION}.${MINOR_VERSION}${RELEASE_TAG}" > \
          ${CURDIR}/version.txt
	${MKDIR} ${TMPDIR}/${PACKAGE_NAME}
	${CD} ${TMPDIR}/${PACKAGE_NAME} && \
          for package in ${PACKAGES}; do ${LN} ${BASE_DIR}/$$package .; done && \
          ${CD} ${TMPDIR} && ${TAR} czhf ${SOURCE_DIR}/${PACKAGE_NAME}.tgz \
           --exclude=${PACKAGE_NAME}.tgz \
           --exclude=CVS \
           --exclude=.svn \
           --exclude=.cvsignore \
           --exclude=*.pyc \
           --exclude=TAGS \
           --exclude=*~ \
           --exclude=.#* \
		   ${PACKAGE_NAME}
	${RMRF} ${TMPDIR}/${PACKAGE_NAME}
