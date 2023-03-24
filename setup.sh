#! /bin/bash

if [ "$(uname)" == "Darwin" ]; then
    if ! command -v brew > /dev/null; then
        echo "Homebrew is not installed. Installing now..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
    fi

    if [ "$EUID" -eq 0 ]; then
        echo "Homebrew does not support running as root. Please run the script without sudo."
        exit 1
    fi

    brew update
    brew install \
        python3 \
        ffmpeg \
        sdl2 \
        sdl2_image \
        sdl2_mixer \
        sdl2_ttf \
        portmidi \
        gstreamer \
		git 

elif [ "$(uname)" == "Linux" ]; then
    if [ "$EUID" -ne 0 ]; then
        echo "Please run the script as root or with sudo permissions."
        exit 1
    fi

    apt update
    apt install -y \
        python3 \
        python3-pip \
        python3-dev \
        python3-pygame \
        python3-sdl2 \
        build-essential \
        git \
        ffmpeg \
        libsdl2-dev \
        libsdl2-image-dev \
        libsdl2-mixer-dev \
        libsdl2-ttf-dev \
        libportmidi-dev \
        libswscale-dev \
        libavformat-dev \
        libavcodec-dev \
        zlib1g-dev \
        libgstreamer1.0-dev \
        gstreamer1.0-plugins-base \
        gstreamer1.0-plugins-good
fi

# Install submodules (ZPL)
git submodule update --init --recursive

pip3 install -U \
    pip \
    wheel \
    Cython \
    pygame \
    qrcode \
    python-barcode \
    git+https://github.com/kivy/kivy.git@master