FROM python:3.8-slim

ARG WD=/usb-to-rtsp
WORKDIR $WD

WORKDIR /lvaextension

RUN pip install -U pip

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgstreamer1.0-0 \
    gstreamer1.0-plugins-ugly \
    \
    gir1.2-gst-rtsp-server-1.0 \
    \
    libgirepository1.0-dev \
    libcairo2-dev \
    \
    && pip install \
        pycairo \
        PyGObject \
        asyncio-glib \
        azure-iot-device~=2.3.0

EXPOSE 8554

COPY usb-to-rtsp-on-edge.py .

CMD [ "python", "usb-to-rtsp-on-edge.py" ]
