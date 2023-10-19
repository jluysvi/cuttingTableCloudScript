from datetime import datetime as dt
import csv
import serial
import time
import logging
import requests
import msal
import threading
import tkinter as tk

#Start the serial port.
daily_cuts = 0
daily_target = 0
sync_history = False
history_file = 'history.csv'

def retrieveHistory():
    global history_file   
    current_date = dt.now().strftime('%Y-%m-%d')
    global daily_cuts
    global daily_target

    #Search for the current date in the history file and update the cut number next to it.
    with open(history_file, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        csvdata = list(reader)
        for row in csvdata[1:]:
            if row[0] == current_date:
                daily_cuts = int(row[1])
                daily_target = int(row[2])
    
    print("Daily Cuts from history: " + str(daily_cuts))

def serialAndHistory():
    #arduinoSerial = serial.Serial('/dev/ttyS4', 9600)
    global history_file
    found = False
    new_cuts = False
    global daily_cuts
    global daily_target
    global sync_history

    while True:
        #If there is anything waiting in the serial buffer, check to see if it's the correct character and then increment the cutter count.
        
        '''serialvalue = arduinoSerial.readline().strip().decode('utf-8')
        if serialvalue == 'A':
            daily_cuts += 1
            new_cuts = True '''

        '''userin = input()
        if userin == 'A':
            daily_cuts += 1
            new_cuts = True'''

        if new_cuts:
            new_cuts = False

            #Set the current date and make it a string.
            current_date = dt.now().strftime('%Y-%m-%d')

            #Search for the current date in the history file and update the cut number next to it.
            with open(history_file, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                csvdata = list(reader)
                for row in csvdata[1:]:
                    if row[0] == current_date:
                        row[1] = str(daily_cuts)
                        row[2] = str(daily_target)
                        found = True

            #If the current date is not in the history file, it needs to be added and the file needs to be set to one.
            if not found:
                daily_cuts = 1
                csvdata.insert(1, [current_date, str(daily_cuts), str(daily_target)])

            with open(history_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(csvdata)

            print("Number of cuts: " + str(daily_cuts))

            sync_history = True

        time.sleep(0.1)

def updateCloudHistory():
    #Info for the MSAL
    authority = "https://login.microsoftonline.com/06a84b25-20fc-4a79-90eb-25c66dc36993"
    client_id = "27bc7257-6b2e-4480-9490-940067c4a26f"
    scope = [ "https://graph.microsoft.com/.default" ]
    secret = ".On8Q~4lRarjGt1aNfodai~AWDG_yF4CAaZCeaCR"
    #ID's for the drive and the files locations, as well as the sheet ID.
    drive_id = "b!3t909SHqSU-VuuWyN4bJ7OgPxkZ8zRpDpMZPdo8Zl8suSeloy-UuTJxLb1cB0KnM"
    historycsv_id = "54bab9b8-13b4-4cc4-9e6a-a68cc14a78f7"
    global sync_history
    while True:
        if sync_history:
            sync_history = False
            try:
                app = msal.ConfidentialClientApplication(client_id, authority=authority, client_credential=secret,)
            except requests.exceptions.ConnectionError as e:
                print("No connection for history sync.")
                time.sleep(60)
            else:
                result = None
                result = app.acquire_token_silent(scope, account=None)

                if not result:
                    logging.info("No suitable token exists in cache. Let's get a new one from AAD.")
                    result = app.acquire_token_for_client(scopes=scope)

                with open('history.csv', 'r') as file:
                    # Read the contents of the file as a string
                    csv_content = file.read()

                if "access_token" in result:
                    endpoint = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{historycsv_id}/content"
                    response = requests.put(endpoint, headers={'Content-Type': 'text/plain','Authorization': 'Bearer ' + result['access_token']}, data=csv_content).json()
                    print("Successfully updated cloud file.")
        
                else:
                    print(result.get("error"))
                    print(result.get("error_description"))
                    print(result.get("correlation_id"))

def getCloudTarget():
    #Info for the MSAL
    authority = "https://login.microsoftonline.com/06a84b25-20fc-4a79-90eb-25c66dc36993"
    client_id = "27bc7257-6b2e-4480-9490-940067c4a26f"
    scope = [ "https://graph.microsoft.com/.default" ]
    secret = ".On8Q~4lRarjGt1aNfodai~AWDG_yF4CAaZCeaCR"
    #ID's for the drive and the files locations, as well as the sheet ID.
    drive_id = "b!3t909SHqSU-VuuWyN4bJ7OgPxkZ8zRpDpMZPdo8Zl8suSeloy-UuTJxLb1cB0KnM"
    configfile_id = "1bc4f3b9-2b2b-4d23-8741-03382084bec7"
    configsheet_id = "{00000000-0001-0000-0000-000000000000}"
    number_cell = "C4"
    global daily_target
    while True:
        try:        
            app = msal.ConfidentialClientApplication(client_id, authority=authority, client_credential=secret,)
        except requests.exceptions.ConnectionError as e:
            print("No connection for target sync, waiting 1 minute to retry.")
            time.sleep(60)
        else:
            result = None
            result = app.acquire_token_silent(scope, account=None)

            if not result:
                logging.info("No suitable token exists in cache. Let's get a new one from AAD.")
                result = app.acquire_token_for_client(scopes=scope)

            with open(history_file, 'r') as file:
                # Read the contents of the file as a string
                csv_content = file.read()

            if "access_token" in result:
                endpoint = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{configfile_id}/workbook/worksheets/{configsheet_id}/range(address='{number_cell}')"
                response = requests.get(endpoint, headers={'Authorization': 'Bearer ' + result['access_token']}).json()
                print(response['values'][0][0])
                daily_target = int((response['values'][0][0]))

            else:
                print(result.get("error"))
                print(result.get("error_description"))
                print(result.get("correlation_id"))

            time.sleep(60)

def displayValues():
    root = tk.Tk()
    root.title("Labels Example")
    root.attributes('-fullscreen', True)

    root.configure(bg="white", cursor="none")

    font_size_small = 30
    font_size_large = 300

    global daily_cuts
    global daily_target

    cutsdisplay = tk.Variable(root, daily_cuts)
    targetdisplay = tk.Variable(root, daily_target)

    label1 = tk.Label(root, bg="white", fg="white", text="Total", font=("Arial", font_size_small))
    label2 = tk.Label(root, bg="white", fg="white", textvariable=cutsdisplay, font=("Arial", font_size_large))
    label3 = tk.Label(root, bg="white", fg="white", text="Daily Target", font=("Arial", font_size_small))
    label4 = tk.Label(root, bg="white", fg="white", textvariable=targetdisplay  , font=("Arial", font_size_large))

    label1.grid(row=0, column=0, pady=(15, 0))
    label2.grid(row=1, column=0)
    label3.grid(row=2, column=0)
    label4.grid(row=3, column=0)

    def end_fullscreen(event):
        root.attributes('-fullscreen', False)

    root.bind("<Escape>", end_fullscreen)

    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=10)
    root.grid_rowconfigure(2, weight=1)
    root.grid_rowconfigure(3, weight=10)
    root.grid_columnconfigure(0, weight=1)

    def updateValues():
        nonlocal cutsdisplay
        nonlocal targetdisplay
        global daily_cuts
        global daily_target
        cutsdisplay.set(daily_cuts)
        targetdisplay.set(daily_target)
        root.update_idletasks()
        root.after(100, updateValues)

    updateValues()
    root.mainloop()


retrieveHistory()

t1 = threading.Thread(target=serialAndHistory)
t2 = threading.Thread(target=updateCloudHistory)
t3 = threading.Thread(target=getCloudTarget)
t4 = threading.Thread(target=displayValues)

t1.start()
t2.start()
t3.start()
t4.start()