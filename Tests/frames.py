import cv2

capture = cv2.VideoCapture("C:/Users/Алекс/Desktop/Main papka/Фото/Ustroy Destroy/Part 2.mp4")

frameNr = 0

while (True):

    success, frame = capture.read()

    if success:
        print("suc")
        cv2.imwrite(f'C:/Users/Алекс/Desktop/Main papka/Фото/Ustroy Destroy/frame_{frameNr}.jpg', frame)


    else:
        break

    frameNr = frameNr + 1

capture.release()
