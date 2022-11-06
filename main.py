import os
import phonenumbers
from multiprocessing import Process, Value
import time
import pickle
from twilio.rest import Client
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

#twilio account variables
account_sid = 'xxxxxxxxxxxxxxxx'
auth_token = 'xxxxxxxxxxxxxxxxx'
client = Client(account_sid, auth_token)
twilio_phone = '+19896569349'

loc = Nominatim(user_agent="GetLoc")

#pickle
users = {}
pickle_out = open("users.pickle","wb")
pickle.dump(users, pickle_out)
pickle_out.close()

@app.route('/', methods=['GET', 'POST'])
def form():
    global users
    users = readPickleDict(users)
    if request.method == 'POST':
        phone = request.form.get('phone')
        val_phone = validate_phone(phone)
        destination = request.form.get('destination')
        destination_loc = loc.geocode(destination)
        if(val_phone is not None and destination_loc is not None):
            coords = (destination_loc.latitude, destination_loc.longitude)
            values = [coords,True]
            users[val_phone] = values
            writePickleDict(users)
            return render_template('welcome.html')
        elif(val_phone is None):
            return render_template('signin.html', msg="Invalid phone.")
        elif(destination_loc is None):
            return render_template('signin.html', msg="Invalid")
    return render_template('signin.html', msg=None)

def validate_phone(phone):
    try:
        p = phonenumbers.parse(phone,"US")
        if not phonenumbers.is_valid_number(p):
            p = "+1" + str(p)
            p = phonenumbers.parse(phone,"US")
        if not phonenumbers.is_valid_number(p):
            return None
        return phonenumbers.format_number(p, phonenumbers.PhoneNumberFormat.E164)
    except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
        return None

@app.route('/success', methods=['GET', 'POST'])
def success():
    if request.method == 'POST':
        return redirect(url_for('form'))
    return render_template('welcome.html')

def message(phone):
    message = client.messages.create(
                        to=phone,
                        from_=twilio_phone,
                        body='This is your wake up call from eazzZy sleep! You are approximately 5 minutes away from your destination!🌛🌟' )

def writePickleDict(x):
    pickle_out = open("users.pickle","wb")
    pickle.dump(x, pickle_out)
    pickle_out.close()

def readPickleDict(x):
    pickle_in = open("users.pickle","rb")
    x = pickle.load(pickle_in)
    return x

def track(phone, destination):
    f = open("location.txt", "r")
    longitude = f.readline()
    latitude = f.readline()
    curr_coords = (longitude, latitude)
    if geodesic(curr_coords, destination) <= 7: #if they're within the threshold of 7km, text user
        print("RECEIVING TEXT MESSAGE SOON ... !!!")
        message(phone)
        users[phone][2] = False
        writePickleDict(users)
        
def output():
    while True:
        global users
        users = readPickleDict(users)
        for user in users:
            if users[user][1]:
                destination = users[user][0]
                print("tracking on bus to " + str(destination) + "\n")
                track(user, destination)
        time.sleep(3) #refresh happens every 3 seconds

if __name__ == '__main__':
    process = Process(target=output)
    process.start()  
    app.run(debug=True, use_reloader=False)