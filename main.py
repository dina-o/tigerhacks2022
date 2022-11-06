import os
from flask import Flask, render_template, request, session, redirect, url_for
import phonenumbers
import pickle
import time
from multiprocessing import Process, Value

from geopy.geocoders import Nominatim
import geocoder
from geopy.distance import geodesic
from geopy import distance

from twilio.rest import Client

app = Flask(__name__)

users = {"+phonenumber": (36.9659, -78.0950)}


#twilio client set up
account_sid = os.environ["xxxx"]
auth_token  = os.environ["xxxx"]
client= Client(account_sid, auth_token)
twilio_phone = "+19896569349"

location = Nominatim(user_agent="GetLoc")

@app.route('/',methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        phone = request.form.get('phone')
        destination = request.form.get('destination')
        destination_location = location.geocode(destination)
        coords = (destination_location.latitude, destination_location.longitude)
        users = {phone: coords}        
    return render_template('welcome.html')

@app.route('/success', methods=['GET', 'POST'])
def success():
    if request.method == 'POST':
        return redirect(url_for('form'))
    return render_template('welcome.html')

def message(phone):
    message = client.messages.create(body="Hello from python", to="phone", from_="twilio_phone")

def track(phone, destination, threshold):
    current_location = geocoder.ip('me')
    current_coordinates = (38.9659, -78.0950)
    if geodesic(current_coordinates, destination).miles <= 5: #logic for user being close to destination
        message(phone)
        del users[phone]
        print("time to wake up!")

def main_loop():
    while True:
        for a, v in users:
            phone = a
            destination = v[0]
            threshold = 5
            track(phone, destination, threshold)


if __name__ == '__main__':
    app.run(debug=True)
    print("start")
    recording_on = Value('b', True)
    p = Process(target=main_loop)
    p.start()
    app.run(debug=True, use_reloader=False)
    p.join()