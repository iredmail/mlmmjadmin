#!/usr/bin/env bash

# Purpose: Upgrade mlmmjadmin from old release.

# USAGE:
#
#   Run commands below as root user:
#
#       # bash upgrade_mlmmjadmin.sh
#

export SYS_USER_MLMMJ='mlmmj'
export SYS_GROUP_MLMMJ='mlmmj'
export SYS_USER_ROOT='root'

# iRedAdmin directory and config file.
export MA_ROOT_DIR='/opt/mlmmjadmin'
export MA_PARENT_DIR="$(dirname ${MA_ROOT_DIR})"
export MA_CONF="${MA_ROOT_DIR}/settings.py"
export MA_CUSTOM_CONF="${MA_ROOT_DIR}/custom_settings.py"

# Path to some programs.
export PYTHON_BIN='/usr/bin/python'

# Check OS to detect some necessary info.
export KERNEL_NAME="$(uname -s | tr '[a-z]' '[A-Z]')"

if [ X"${KERNEL_NAME}" == X'LINUX' ]; then
    if [ -f /etc/redhat-release ]; then
        # RHEL/CentOS
        export DISTRO='RHEL'
    elif [ -f /etc/lsb-release ]; then
        # Ubuntu
        export DISTRO='UBUNTU'
    elif [ -f /etc/debian_version ]; then
        # Debian
        export DISTRO='DEBIAN'
    elif [ -f /etc/SuSE-release ]; then
        # openSUSE
        export DISTRO='SUSE'
    else
        echo "<<< ERROR >>> Cannot detect Linux distribution name. Exit."
        echo "Please contact support@iredmail.org to solve it."
        exit 255
    fi
elif [ X"${KERNEL_NAME}" == X'FREEBSD' ]; then
    export DISTRO='FREEBSD'
    export PYTHON_BIN='/usr/local/bin/python'
elif [ X"${KERNEL_NAME}" == X'OPENBSD' ]; then
    export DISTRO='OPENBSD'
    export PYTHON_BIN='/usr/local/bin/python'
else
    echo "Cannot detect Linux/BSD distribution. Exit."
    echo "Please contact author iRedMail team <support@iredmail.org> to solve it."
    exit 255
fi

restart_mlmmjadmin()
{
    echo "* Restarting service: mlmmjadmin."
    if [ X"${KERNEL_NAME}" == X'LINUX' -o X"${KERNEL_NAME}" == X'FREEBSD' ]; then
        service mlmmjadmin restart
    elif [ X"${KERNEL_NAME}" == X'OPENBSD' ]; then
        rcctl restart mlmmjadmin
    fi

    if [ X"$?" != X'0' ]; then
        echo "Failed, please restart service 'mlmmjadmin' manually."
    fi
}

echo "* Detected Linux/BSD distribution: ${DISTRO}"

if [ -L ${MA_ROOT_DIR} ]; then
    export MA_ROOT_REAL_DIR="$(readlink ${MA_ROOT_DIR})"
    echo "* Found mlmmjadmin: ${MA_ROOT_DIR}, symbol link of ${MA_ROOT_REAL_DIR}"
else
    echo "<<< ERROR >>> Directory (${MA_ROOT_DIR}) is not a symbol link created by iRedMail. Exit."
    exit 255
fi

# Copy config file
if [ -f ${MA_CONF} ]; then
    echo "* Found old config file: ${MA_CONF}"
else
    echo "<<< ERROR >>> No old config file found ${MA_CONF}, exit."
    exit 255
fi

# Copy current directory to /opt
dir_new_version="$(dirname ${PWD})"
name_new_version="$(basename ${dir_new_version})"
NEW_MA_ROOT_DIR="${MA_PARENT_DIR}/${name_new_version}"
NEW_MA_CONF="${NEW_MA_ROOT_DIR}/settings.py"
if [ -d ${NEW_MA_ROOT_DIR} ]; then
    COPY_FILES="${dir_new_version}/*"
    COPY_DEST_DIR="${NEW_MA_ROOT_DIR}"
else
    COPY_FILES="${dir_new_version}"
    COPY_DEST_DIR="${MA_PARENT_DIR}"
fi

echo "* Copying new version to ${NEW_MA_ROOT_DIR}"
cp -rf ${COPY_FILES} ${COPY_DEST_DIR}

# Copy old config files
echo "* Copy ${MA_CONF}."
cp -p ${MA_CONF} ${NEW_MA_ROOT_DIR}/

if [ -f ${MA_CUSTOM_CONF} ]; then
    echo "* Copy ${MA_CUSTOM_CONF}."
    cp -p ${MA_CUSTOM_CONF} ${NEW_MA_ROOT_DIR}
fi

# Set owner and permission.
chown -R ${SYS_USER_MLMMJ}:${SYS_GROUP_MLMMJ} ${NEW_MA_ROOT_DIR}
chmod -R 0755 ${NEW_MA_ROOT_DIR}
chmod 0400 ${NEW_MA_CONF}

echo "* Removing old symbol link ${MA_ROOT_DIR}"
rm -f ${MA_ROOT_DIR}

echo "* Creating symbol link: ${NEW_MA_ROOT_DIR} -> ${MA_ROOT_DIR}"
cd ${MA_PARENT_DIR}
ln -s ${NEW_MA_ROOT_DIR} ${MA_ROOT_DIR}

echo "* mlmmjadmin has been successfully upgraded."
restart_mlmmjadmin

# Clean up.
cd ${NEW_MA_ROOT_DIR}/
rm -f settings.py{c,o} tools/settings.py{,c,o}

echo "* Upgrading completed."

cat <<EOF
<<< NOTE >>> If mlmmjadmin doesn't work as expected, please post your issue in
<<< NOTE >>> our online support forum: http://www.iredmail.org/forum/
EOF
