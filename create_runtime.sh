#!/bin/sh

SUDO='sudo'
if [ "$USER" = "root" ]; then
   echo 'shame shame, running as root.'
   SUDO=''
fi
if [ -d /opt/python ]; then
    echo 'prefixing opt python to path'
    PATH="/opt/python/bin:$PATH"
fi
if [ "$( uname )" = "Darwin" ]; then
    export CFLAGS=-Qunused-arguments
    export CPPFLAGS=-Qunused-arguments
fi

rm -rf runtime

if [ ! -d ./pipcache ]; then
	mkdir ./pipcache
fi

export PIP='/opt/python/bin/pip install --download-cache=./pipcache'

$SUDO $PIP virtualenv &&
export PIP='pip install --download-cache=./pipcache'
virtualenv -p $(which python2.7) runtime &&
#git checkout -- runtime/README.md &&

. runtime/bin/activate &&

$PIP elasticsearch &&
$PIP Celery &&
$PIP redis &&
$PIP requests &&
$PIP boto &&
$PIP librabbitmq &&
echo 'done' &&
exit 0 || (  echo 'failed'; exit 1; )
