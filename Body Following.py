from djitellopy import tello
import cv2
import cvzone
from cvzone.PoseModule import PoseDetector
import time

detector = PoseDetector()

cap = cv2.VideoCapture(0)
_, img = cap.read()
h1, w1, _ = 480, 640, True

gesture = ''
colourG = (0, 0, 255)
snapTime = 0

xPID = cvzone.PID([0.22, 0, 0.1], w1 // 2)
yPID = cvzone.PID([0.27, 0, 0.1], h1 // 2, axis=1)
zPID = cvzone.PID([0.00016, 0, 0.0003], 300000, limit=[-20, 15])

myPlotx = cvzone.LivePlot(yLimit=[-100, 100], char='x')
myPloty = cvzone.LivePlot(yLimit=[-100, 100], char='Y')
myPlotz = cvzone.LivePlot(yLimit=[-100, 100], char='Z')

following = False

#me = tello.Tello()
#me.connect()
#print(me.get_battery())
#me.streamoff()
#me.streamon()
#me.takeoff()
#me.move_up(80)

while True:

    _, img = cap.read()
    #img = me.get_frame_read().frame
    img = cv2.resize(img, (640, 480))

    img = detector.findPose(img, draw=True)
    lmList, bboxInfo = detector.findPosition(img, draw=True)

    xVal = 0
    yVal = 0
    zVal = 0

    if bboxInfo:
        cx, cy = bboxInfo['center']
        x, y, w, h = bboxInfo['bbox']
        area = w * h

        xVal = int(xPID.update(cx))
        yVal = int(yPID.update(cy))
        zVal = int(zPID.update(area))

        angArmL = detector.findAngle(img, 13, 11, 23, draw=False)
        angArmR = detector.findAngle(img, 14, 12, 24, draw=False)
        CrossL, img, _ = detector.findDistance(15, 12, img, draw=False)
        CrossR, img, _ = detector.findDistance(16, 11, img, draw=False)
        CrossP, img, _ = detector.findDistance(16, 8, img, draw=False)

        if detector.angleCheck(angArmL, 98) and detector.angleCheck(angArmR, 278):
            gesture = 'Tracking mode: OFF'
            following = False
            colourG = (0, 0, 255)

        elif CrossL < 70 and CrossR < 70:
            gesture = 'Tracking mode: ON'
            following = True
            colourG = (0, 255, 0)

        if CrossP < 100:
            snapTime = time.time()
            cv2.putText(img, gesture, (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)

        if snapTime > 0:
            totaltime = time.time()-snapTime

            if totaltime < 1.9:
                cv2.putText(img, " ", (120, 260), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)

            if totaltime > 2:
                snapTime = 0
                cv2.imwrite(f'Images/{time.time()}.jpg', img)
                cv2.putText(img, "Saves", (120, 260), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)

        # elif detector.angleCheck(angArmL, 170) and detector.angleCheck(angArmR, 188):
        # gesture = 'Cross '

        cv2.putText(img, gesture, (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, colourG, 3)

        imgPlotx = myPlotx.update(xVal)
        imgPloty = myPloty.update(yVal)
        imgPlotz = myPlotz.update(zVal)

        img = xPID.draw(img, [cx, cy])
        img = yPID.draw(img, [cx, cy])
        imageStacked = cvzone.stackImages([img, imgPlotx, imgPloty, imgPlotz], 2, 0.5)
        # cv2.putText(imageStacked, str(area), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
    else:
        imageStacked = cvzone.stackImages([img], 1, 0.75)

    #if following:
    #    me.send_rc_control(0, -zVal, 0, xVal)
    #else:
    #    me.send_rc_control(0, 0, 0, 0)

    cv2.imshow("ImageStacked", imageStacked)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        #me.land()
        break
cv2.destroyWindow()
