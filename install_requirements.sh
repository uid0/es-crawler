#!/bin/sh
SUDO='sudo'
if [ "$USER" = "root" ]; then
   echo 'shame shame, running as root.'
   SUDO=''
fi

PYTHON_VERSION='2.7.6'
# TODO: move setup tools and geoip to config vars
export "PATH=/opt/python/bin:$PATH"

if [ "$( uname )" = "Darwin" ]; then
    brew install libjpeg freetype ffmpeg imagemagick ghostscript redis
    echo "darwin base complete"
fi

# if [ -f "/etc/debian_version" ]; then
#     $SUDO apt-get install -y \
#         build-essential \
#         python python-dev python-pip python-virtualenv \
#         libffi-dev libjpeg-dev libgif-dev \
#         exuberant-ctags \
#         libxml2-utils \
#         ffmpeg \
#         imagemagick \
#         ghostscript \
#         sqlite3 libpcre3-dev &&
#     echo "debian base complete"
#
# fi

if [ -f "/etc/redhat-release" ]; then

    # Install support for EPEL to get erlang
    $SUDO rpm -Uvh http://download.fedoraproject.org/pub/epel/6/i386/epel-release-6-8.noarch.rpm

    $SUDO yum groupinstall -y development
    $SUDO yum install -y \
        python-setuptools wget curl screen vim  vim-enhanced \
        zlib-devel openssl-devel sqlite-devel bzip2-devel \
        libffi-devel libjpeg-devel libzip-devel \
        libxml2-devel ctags \
        redis \
        ffmpeg \
        imagemagick \
        ImageMagick-devel \
        ghostscript \
        pcre-devel \
        erlang

    $SUDO yum install -y \
        http://dl.fedoraproject.org/pub/epel/6/x86_64/GeoIP-1.4.8-1.el6.x86_64.rpm \
        http://dl.fedoraproject.org/pub/epel/6/x86_64/GeoIP-devel-1.4.8-1.el6.x86_64.rpm \
        http://dl.fedoraproject.org/pub/epel/6/x86_64/redis-2.4.10-1.el6.x86_64.rpm \
        http://www.rabbitmq.com/releases/rabbitmq-server/v3.3.4/rabbitmq-server-3.3.4-1.noarch.rpm
    echo "redhat base complete"

    # Setup rabbitmq
    #$SUDO chkconfig rabbitmq-server on

fi

# install python
if [ ! -d /opt/python ]; then
    if [ !  -d ~/python-build/ ]; then
        mkdir ~/python-build/
    fi

    ( cd ~/python-build;
        if [ ! -f Python-$PYTHON_VERSION.tgz ] ; then
            wget -c https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz &&
            tar zxf Python-$PYTHON_VERSION.tgz
        fi
        cd Python-$PYTHON_VERSION &&
        ./configure --prefix=/opt/python &&
        make &&
        $SUDO make install
    )

    # ok, we now have python installed to /opt/python

    # need pip / virtualenv
    ( cd ~/python-build;
        wget -c https://pypi.python.org/packages/source/s/setuptools/setuptools-3.6.tar.gz &&
        tar zxf setuptools-3.6.tar.gz &&
        cd setuptools-3.6 &&
        $SUDO $(which python2.7) setup.py install
    )

    # install the pip bits.  i really do not like this.
    #curl https://raw.githubusercontent.com/pypa/pip/master/contrib/get-pip.py | python2.7
    ( cd ~/python-build;
        wget https://bootstrap.pypa.io/get-pip.py &&
        $SUDO $(which python2.7) get-pip.py
    )
fi

echo 'all done'
which python2.7
which gcc

