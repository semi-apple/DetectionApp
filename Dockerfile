# syntax=docker/dockerfile:1

# set base image to the 22.04 release of Ubuntu
FROM python:3.10

# create work dir
WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel

# install tools
RUN echo "Tools installing..." && \
    apt-get update && apt-get install -y \
    xvfb \
    libgl1 \
    libxcb-xinerama0 \
    libxkbcommon-x11-0 \
    libxcb1 \
    libx11-xcb1 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libdbus-1-3 \
    qt5-qmake \
    qtbase5-dev && \
    rm -rf /var/lib/apt/lists/*

# Install python packages with pip
RUN echo "(*) Installing python packages with pip..." && \
    pip install --no-cache-dir -r requirements.txt


# copy all code to work dir
COPY . /app

EXPOSE 8000

ENV QT_QPA_PLATFORM=xcb
ENV QT_DEBUG_PLUGINS=1
ENV QT_DEBUG_COMPONENT=1

ENV DISPLAY=:99

CMD Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset & \
    python Application/DetectionApp.py

# RUN sudo apt-get install '^libxcb.*-dev' libx11-xcb-dev libglu1-mesa-dev libxrender-dev libxi-dev libxkbcommon-dev libxkbcommon-x11-dev
# rm /home/s4764481/anaconda3/envs/detection_app/lib/python3.9/site-packages/cv2/qt/plugins/platforms/libqxcb.so