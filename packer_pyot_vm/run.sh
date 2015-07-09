#!/bin/bash

set -e


if [ ! -f /tmp/packer/packer ]; then

    if [ ! -f /tmp/packer.zip ]; then
        echo "Downloading packer - saving it in /tmp/packer.zip"
        wget http://dl.bintray.com/mitchellh/packer/0.5.1_linux_386.zip -O /tmp/packer.zip
    fi

    echo "Unzipping packer - inside /tmp/packer"
    unzip /tmp/packer.zip -d /tmp/packer
fi

echo "Running packer - /tmp/packer/packer"
/tmp/packer/packer build template.json
