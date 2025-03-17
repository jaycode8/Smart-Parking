import cv2
import pytesseract
import re

def extract_plate_number(ocr_text):
    """Extracts the first valid plate number from repetitive OCR output."""
    match = re.search(r'([A-Z]{2}\d{2}[A-Z]{2}\d{4})', ocr_text)
    return match.group(1) if match else None

def bright_plate_extraction(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    edges = cv2.Canny(gray, 50, 200)

    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    plate_num = ""
    im2 = img.copy()
    
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = w / float(h)
        area = w * h

        if 2 < aspect_ratio < 6 and area > 2000:
            print("hey")
            try:
                roi = gray[y-5:y+h+5, x-5:x+w+5]
                cv2.imwrite("roi.png", roi)
                roi = cv2.adaptiveThreshold(roi, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                            cv2.THRESH_BINARY_INV, 25, 15)
                cv2.imwrite("roi2.png", roi)

                text = pytesseract.image_to_string(roi, config='--psm 7 --oem 3')
                clean_text = re.sub(r'\W+', '', text)
                plate_num += clean_text
            except Exception as e:
                continue

    clean_plate = extract_plate_number(plate_num)
    
    return clean_plate if clean_plate else plate_num

def plate_extraction(img):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 15)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    dilation = cv2.dilate(thresh, kernel, iterations=1)

    contours, _ = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    sorted_contours = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[0])
    plate_num = ""
    im2 = gray.copy()
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