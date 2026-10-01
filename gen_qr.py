"""gen_qr.py — QR codes for all receive rails → assets/qr/*.png (black on white, max scannability)."""
import os, qrcode

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qr")
os.makedirs(OUT, exist_ok=True)

RAILS = {
    "qr-evm.png": "0x11B185ceFcB2A001FFDddf0f226437D16EbF5437",
    "qr-btc.png": "bitcoin:bc1qa7txyzk3yqxgln09uzujqcy47eua4f8afsdhec",
    "qr-sol.png": "solana:D1dCds8PrFFAPS5WqyVEai828UmEw77zVidtgeQSte78",
    "qr-ln.png": "lightning:metatronscribe@coinos.io",
}
for name, data in RAILS.items():
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=8, border=3)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    p = os.path.join(OUT, name)
    img.save(p)
    print("saved", p, os.path.getsize(p), "bytes")
print("DONE")
