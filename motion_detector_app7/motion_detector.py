import cv2
import time
from datetime import datetime
import pandas

first_frame = None
status_list = [None, None]
times = []
df = pandas.DataFrame(columns=["Start", "End"])

video = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# if got multiple camera
# 0 = first camera, 1 = second..
# movie.mp4 can put video file as the first parameter also
a = 0

while True:
    a = a+1
    check, frame = video.read()  # read the first frame
    status = 0  # change the status back to zero whethever a new frame is read
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # blur the image, remove noice, increase accuracy
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    # (21,21) width and height of the Gaussian kernel
    # 0 for the standard deviation

    # dont consider first 40 frames as first frame as the camera might start as black image (loading), which makes the difference to be very high--> delta will be exactly like your frame cuz its 100% diff from the black img of first frame
    if (first_frame is None) and (a < 40):
        a = a + 1
        continue
    elif first_frame is None:
        # first frame is the background img (from the first frame of the video)
        first_frame = gray
        # dont run rest of the code, go back to beginning of the loop (next iteration)
        continue

    # compare the background img to the current img
    # return another img
    delta_frame = cv2.absdiff(first_frame, gray)

    thresh_frame = cv2.threshold(delta_frame, 30, 255, cv2.THRESH_BINARY)[1]
    # delta_frame, limit = 30, if >30 , paint white, threshold library)
    # there are many types of threshold library
    # return a tuple (1st item is the value of the threshold, 2nd is the actual frame return from the threshold method)
    # for threshold binary need to access only 2nd item

    thresh_frame = cv2.dilate(thresh_frame, None, iterations=10)
    # iteration= how many times you want to check the image for black holes, bigger value --> smoother
    # frame, the threshold kernal, iteration

# find Contours of distinct object
# if got two white continuos area in the img, but they are distinct, will get two contours for each area
    (cnts, _) = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL,
                                 cv2.CHAIN_APPROX_SIMPLE)  # find the area of the white color
# filter the contours area > 10000 pixels (detect bigger object)
    for contour in cnts:
        if cv2.contourArea(contour) < 10000:
            continue
         # create tuple with 4 coordinates
         # get values frm the bounding rectangle of the current contour
        # draw the rectangle in the current frame to tell where got motion
        status = 1  # change status to 1 if there is at least one motion

        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)

    status_list.append(status)
    # store the timestamp where the object enters and leaves

    # modify the list to only last two items, to save memory
    status_list = status_list[-2:]

    if status_list[-1] == 1 and status_list[-2] == 0:
        times.append(datetime.now())
    if status_list[-1] == 0 and status_list[-2] == 1:
        times.append(datetime.now())

    cv2.imshow("Gray Frame", gray)
    cv2.imshow("Delta Frame", delta_frame)
    cv2.imshow("Threshold Frame", thresh_frame)
    cv2.imshow("Color Frame", frame)

    key = cv2.waitKey(1)
    # print(first_frame)
    # print(gray)
    # print(delta_frame)
    # type q key, break the while loop
    if (key == ord('q')):
        if status == 1:
            # when the object is in the frame and the window stop, need to append the time list again to indicate the time
            times.append(datetime.now())
            # else the status will ends at 1
            # [0,0,0,1,1,1,0,0,0,1,1,1] #got enter no leave at the end
        break

    # print(status)  # will be one if there is at least one motion
print(status_list)  # print all status
print(times)

# list of 6 -> 3 start time, 3 end
# from 0 to 6 with the step of 2
# from 0 , access times[0] and times[1]
# next will go to 2, access times[2] and times[3]
for i in range(0, len(times), 2):
    df = df.append({"Start": times[i], "End": times[i+1]}, ignore_index=True)

df.to_csv("Times.csv")
video.release()
# release the camera (close the camera)
# release the video first before destroy
cv2.destroyAllWindows()
