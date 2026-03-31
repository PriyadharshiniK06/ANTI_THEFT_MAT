import cv2
import serial
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

# Function to capture image from webcam
def capture_image(output_path='captured_image.jpg'):
    cam = cv2.VideoCapture(0)  # Open default camera
    if not cam.isOpened():
        print("Error: Could not open webcam.")
        return None

    ret, frame = cam.read()
    if ret:
        cv2.imwrite(output_path, frame)
        print(f"Image saved as {output_path}")
    else:
        print("Failed to capture image.")

    cam.release()
    cv2.destroyAllWindows()
    return output_path

# Function to send email with the captured image as attachment
def send_email_with_attachment(sender_email, sender_password, recipient_email, subject, body, file_path):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Add body to the email
    msg.attach(MIMEText(body, 'plain'))

    # Attach the file
    if file_path and os.path.exists(file_path):
        with open(file_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f"attachment; filename={os.path.basename(file_path)}"
        )
        msg.attach(part)

    # Send the email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Using Gmail's SMTP server
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        server.quit()

# Function to listen to the USB port
def listen_to_usb(port='COM3', baudrate=9600):
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        print(f"Listening on {port} at {baudrate} baud.")
        while True:
            data = ser.readline().decode().strip()  # Read data from the USB port
            if data == 'A':  # Trigger condition
                print("Signal received: 'A'")
                return True
    except Exception as e:
        print(f"Error with USB port: {e}")
        return False

# Main script
if __name__ == "__main__":
    # Email configuration
    sender_email = "your_email@gmail.com"
    sender_password = "your_app_password"  # Use the App Password generated from Google
    recipient_email = "recipient_email@gmail.com"
    subject = "Captured Image"
    body = "Here is the image captured from the webcam."

    # USB port configuration
    usb_port = 'COM3'  # Replace with your USB port (e.g., /dev/ttyUSB0 for Linux)
    baudrate = 9600

    # Wait for signal from USB
    if listen_to_usb(port=usb_port, baudrate=baudrate):
        # Capture image
        image_path = capture_image()

        # Send the captured image as an email attachment
        if image_path:
            send_email_with_attachment(sender_email, sender_password, recipient_email, subject, body, image_path)
