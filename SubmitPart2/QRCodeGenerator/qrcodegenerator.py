from flask import Flask, render_template, request, send_file
import qrcode
import io

app = Flask(__name__)


# Display QrCode Form
@app.route("/")
def index():
    return render_template("qrcodeform.html")


# Post the form and return the qrcode png
@app.route("/qrgenerate", methods=["POST", "GET"])
def qrgenerate():
    stringIn = request.form.get("stringIn")

    # Create a QR code instance
    qr = qrcode.QRCode(
        version=1,  # QR code version (adjust as needed)
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # Error correction level
        box_size=10,  # Size of each box in the QR code
        border=4,  # Border around the QR code
    )

    # Add the data (your input string) to the QR code
    qr.add_data(stringIn)
    qr.make(fit=True)

    # Create a QR code image using PIL (Python Imaging Library)
    img = qr.make_image(fill_color="black", back_color="white")
    # Create an in-memory file object to hold the image
    img_buffer = io.BytesIO()
    img.save(img_buffer, "PNG")

    img_buffer.seek(0)
    return send_file(img_buffer, mimetype="qrcode.png")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
