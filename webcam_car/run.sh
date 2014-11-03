/opt/mjpg-streamer/mjpg_streamer -i "/opt/mjpg-streamer/input_raspicam.so -fps 15 -q 50 -x 640 -y 480" -o "/opt/mjpg-streamer/output_http.so -p 9000 -w /opt/mjpg-streamer/www" &
cd /home/pi/python
python starterkit_webcam.py &

