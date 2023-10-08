import RPi.GPIO as GPIO
import cv2
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

# Set GPIO pin numbers
TRIGGER_PIN = 16 # GPIO pin for the ultrasonic sensor's Trigger
ECHO_PIN = 11     # GPIO pin for the ultrasonic sensor's Echo

# Email configuration
SMTP_SERVER = "smpt.gmail.com"  # SMTP server address
SMTP_PORT = 587  # SMTP server port
SMTP_USERNAME = "anumitha6006@gmail.com"  # Your email address
SMTP_PASSWORD = "@anumitha11"  # Your email password
RECIPIENT_EMAIL = "jaishmurali30@gmail.com"  # Recipient's email address

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIGGER_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

def measure_distance():
    GPIO.output(TRIGGER_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIGGER_PIN, False)

    start_time = time.time()
    while GPIO.input(ECHO_PIN) == 0:
        start_time = time.time()

    while GPIO.input(ECHO_PIN) == 1:
        end_time = time.time()

    pulse_duration = end_time - start_time
    distance = pulse_duration * 17150  # Speed of sound (343 m/s) / 2
    return distance

def capture_image():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite("motion_capture.jpg", frame)
    cap.release()

def send_email():
    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = "Motion Detected"

    body = "Motion was detected at your home entrance."
    msg.attach(MIMEText(body, 'plain'))

    with open("motion_capture.jpg", 'rb') as attachment:
        image = MIMEImage(attachment.read(), name="motion_capture.jpg")
        msg.attach(image)

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    text = msg.as_string()
    server.sendmail(SMTP_USERNAME, RECIPIENT_EMAIL, text)
    server.quit()

try:
    while True:
        distance = measure_distance()
        if distance < 100:  # Adjust this threshold based on your needs
            print("Motion detected!")
            capture_image()
            send_email()
            time.sleep(10)  # Delay to prevent multiple alerts
        time.sleep(1)  # Adjust the polling interval
except KeyboardInterrupt:
    GPIO.cleanup()