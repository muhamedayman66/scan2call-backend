import hashlib
import secrets
from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image


def generate_unique_hash(length: int = 10) -> str:
    """Generate a unique hash string"""
    return secrets.token_urlsafe(length)[:length]


def compress_image(
    image: InMemoryUploadedFile, quality: int = 85, max_size: tuple = (1920, 1080)
) -> InMemoryUploadedFile:
    """Compress and resize image"""
    img = Image.open(image)

    # Convert RGBA to RGB if necessary
    if img.mode in ("RGBA", "LA"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[-1])
        img = background

    # Resize if larger than max_size
    img.thumbnail(max_size, Image.Resampling.LANCZOS)

    # Save to BytesIO
    output = BytesIO()
    img.save(output, format="JPEG", quality=quality, optimize=True)
    output.seek(0)

    # Create new InMemoryUploadedFile
    return InMemoryUploadedFile(
        output,
        "ImageField",
        f"{image.name.split('.')[0]}.jpg",
        "image/jpeg",
        output.getbuffer().nbytes,
        None,
    )


def calculate_file_hash(file) -> str:
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    for byte_block in iter(lambda: file.read(4096), b""):
        sha256_hash.update(byte_block)
    file.seek(0)
    return sha256_hash.hexdigest()


def format_phone_number(phone: str) -> str:
    """Format phone number to international format"""
    # Remove any non-digit characters
    phone = "".join(filter(str.isdigit, phone))

    # Add +20 if Egyptian number
    if len(phone) == 10 and phone.startswith("0"):
        return f"+2{phone}"
    elif len(phone) == 11 and phone.startswith("01"):
        return f"+2{phone}"
    elif not phone.startswith("+"):
        return f"+{phone}"

    return phone


def validate_egyptian_plate(plate: str) -> bool:
    """Validate Egyptian license plate format"""
    import re

    # Egyptian format: ABC 1234 or ABC-1234
    pattern = r"^[A-Z]{3}[\s-]?\d{4}$"
    return bool(re.match(pattern, plate.upper()))
