import cv2

def show_image(img):
    img_copy = img.copy()
    resize = cv2.resize(img_copy, (1600, 1200), interpolation=cv2.INTER_LINEAR)
    cv2.imshow('frame', resize)