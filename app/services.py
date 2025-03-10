import cv2
import pytesseract
import re

def plate_extraction(img):
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Apply adaptive thresholding for better contrast
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 15)

    # Apply morphological transformations to refine the text regions
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    dilation = cv2.dilate(thresh, kernel, iterations=1)

    # Find contours
    contours, _ = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    sorted_contours = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[0])
    plate_num = ""
    for cnt in sorted_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        height, width = gray.shape

        if height / float(h) > 6 or w < 10:
            continue

        if h / float(w) < 1:
            continue

        if width / float(w) > 15:
            continue

        area = h * w
        if area < 100:
            continue

        roi = thresh[y-2:y+h+2, x-2:x+w+2]
        roi = cv2.bitwise_not(roi)
        roi = cv2.medianBlur(roi, 3)

        try:
            text = pytesseract.image_to_string(roi, config='-c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ --psm 8 --oem 3')
            clean_text = re.sub('[\W_]+', '', text)
            plate_num += clean_text
        except Exception as e:
            print(f"OCR Error: {e}")

    return plate_num if plate_num else None