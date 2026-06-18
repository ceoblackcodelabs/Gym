import qrcode
from qrcode.constants import ERROR_CORRECT_H
from io import BytesIO
import base64
from django.conf import settings
from django.urls import reverse
import os


def generate_membership_qr(request, membership_id):
    """
    Generate QR code for membership check-in
    Returns base64 encoded image string
    """
    # Build the URL for the membership detail view
    base_url = request.build_absolute_uri('/')
    detail_url = reverse('godmode:membership_detail', kwargs={'pk': membership_id})
    full_url = f"{base_url.rstrip('/')}{detail_url}"

    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(full_url)
    qr.make(fit=True)

    # Create image
    img = qr.make_image(fill_color="#ff3333", back_color="#0a0a0a")

    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/png;base64,{img_str}"


def generate_member_checkin_qr(request, membership_id, user_id):
    """
    Generate QR code with check-in data
    """
    base_url = request.build_absolute_uri('/')
    checkin_url = reverse('godmode:member_checkin', kwargs={
        'membership_id': membership_id,
        'user_id': user_id
    })
    full_url = f"{base_url.rstrip('/')}{checkin_url}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(full_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#00c853", back_color="#0a0a0a")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/png;base64,{img_str}"