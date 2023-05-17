from flask import Flask, render_template, request, redirect, url_for
import cv2
import os
import csv
import numpy as np
import os
from PIL import Image
import pickle
import pandas as pd
import cv2
import numpy as np
import face_recognition
import os
from datetime import date
from datetime import datetime
from werkzeug.utils import secure_filename
 
today = date.today()

UPLOAD_FOLDER = '/ImagesAttendence'




app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
 




	


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/register', methods=['POST', 'GET'])
def register():
     if request.method == 'POST':
        name = request.form['name']
        id = request.form['id']
        degree = request.form['degree']
        department = request.form['department']
        year = request.form['year']
        image_file = request.files['image']
        image_file.save('ImagesAttendence/'+name+'-'+id+ '-'+ degree+'-'+department+'-'+year+'.jpg')
        path = 'ImagesAttendence'
        images = []
        classNames = []
        myList = os.listdir(path)
        print(myList)
        for cl in myList:
            curImg = cv2.imread(f'{path}/{cl}')
            images.append(curImg)
            classNames.append(os.path.splitext(cl)[0])
            print(classNames)
    
        def findEncodings(images):
            encodeList = []
            for img in images:
                img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
                encode = face_recognition.face_encodings(img)[0]
                encodeList.append(encode)
            return encodeList
        encodeListKnown = findEncodings(images)
        print('Encoding Complete') 
        msg = 'Registered successfully'
        return render_template("home.html", msg = msg)


@app.route('/sign_up', methods=['POST', 'GET'])
def sign_up():
    return render_template("register.html")


@app.route('/take_attendance', methods=['POST', 'GET'])
def take_attendance():
    if request.method == "POST":
        fields = ['Id','Name','Degree','Department','Year','time']
        filename = 'Attendance-' + str(today) + '.csv'
        if not os.path.exists('Attendance-' + str(today) + '.csv'): 
            with open(filename, 'w') as csvfile: 
                csvwriter = csv.writer(csvfile) 
                csvwriter.writerow(fields)
        path = 'ImagesAttendence'
        images = []
        classNames = []
        myList = os.listdir(path)
        print(myList)
        for cl in myList:
            curImg = cv2.imread(f'{path}/{cl}')
            images.append(curImg)
            classNames.append(os.path.splitext(cl)[0])
        print(classNames)

        def findEncodings(images):
            encodeList = []
            for img in images:
                img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
                encode = face_recognition.face_encodings(img)[0]
                encodeList.append(encode)
            return encodeList

        def markAttendance(name):
            path = 'Attendance-' + str(today) + '.csv'
            s = name
            for j in range(0,5):
                i = s.find('-')
                if j == 0:
                    name = s[:i]
                elif j == 1:
                    id = s[:i]
                elif j == 2:
                    degree = s[:i] 
                elif j == 3:
                    department = s[:i] 
                elif j == 4:
                    year = s 
                s = s[i+1:]                
            with open(path,'r+') as f:
                myDataList = f.readlines()
                nameList = []
                for line in myDataList:
                    entry = line.split(',')       
                    nameList.append(entry[0])
                if id not in nameList:
                    now = datetime.now()
                    dtString = now.strftime('%H:%M:%S')
                    f.writelines(f'\n{id},{name},{degree},{department},{year},{dtString}')
	

        encodeListKnown = findEncodings(images)
        print('Encoding Complete')

        cap = cv2.VideoCapture(0)

        while True:
            success, img = cap.read()
            imgS = cv2.resize(img,(0,0),None,0.25,0.25)
            imgS = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)	

            faceCurFrame = face_recognition.face_locations(imgS)
            encodesCurFrame = face_recognition.face_encodings(imgS,faceCurFrame)

            for encodeFace,faceLoc in zip(encodesCurFrame,faceCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown,encodeFace) 	
                faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
        #print(faceDis)
                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    name = classNames[matchIndex].upper()
                    markAttendance(name)

        #print(name)
                    y1,x2,y2,x1 = faceLoc
        #y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4
                    cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
                    cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
                    cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
                    

            cv2.imshow('webcam',img)
            cv2.waitKey(1)

    return render_template("mark_attendance.html")

@app.route('/count', methods=['POST', 'GET'])
def count():
    if request.method == "POST":
        import os
        directory_path = "ImagesAttendence"
        count = 0
 
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            count += 1
    return render_template("home.html", show = 0,count = count)

@app.route('/view_attendance', methods=['POST', 'GET'])
def view_attendance():
    if request.method == "POST":
        data = pd.read_csv('Attendance-' + str(today) + '.csv')
    return render_template('attendance.html', tables=[data.to_html()], titles=[''])

@app.route('/profile', methods=['POST', 'GET'])
def profile():
    if request.method == "POST":
        path = 'ImagesAttendence'
        images = []
        classNames = []
        myList = os.listdir(path)
        print(myList)
        for cl in myList:
            curImg = cv2.imread(f'{path}/{cl}')
            images.append(curImg)
            classNames.append(os.path.splitext(cl)[0])
        print(classNames)

        def findEncodings(images):
            encodeList = []
            for img in images:
                img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
                encode = face_recognition.face_encodings(img)[0]
                encodeList.append(encode)
            return encodeList

        

        encodeListKnown = findEncodings(images)
        print('Encoding Complete')

        cap = cv2.VideoCapture(0)

        while True:
            success, img = cap.read()
            imgS = cv2.resize(img,(0,0),None,0.25,0.25)
            imgS = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)	

            faceCurFrame = face_recognition.face_locations(imgS)
            encodesCurFrame = face_recognition.face_encodings(imgS,faceCurFrame)

            for encodeFace,faceLoc in zip(encodesCurFrame,faceCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown,encodeFace) 	
                faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
        #print(faceDis)
                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    name = classNames[matchIndex].upper()

        #print(name)
                    y1,x2,y2,x1 = faceLoc
        #y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4
                    cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
                    cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
                    cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
                    

            cv2.imshow('webcam',img)
            cv2.waitKey(1)

    return render_template("mark_attendance.html")


if __name__ == "__main__":
    app.run(debug=True)



