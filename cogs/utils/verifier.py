import re
from datetime import datetime

import aiohttp
import cv2
import easyocr
import numpy as np

# ======================================================
# OCR READER
# ======================================================

reader = easyocr.Reader(
    ["en"],
    gpu=False,
)

# ======================================================
# DOWNLOAD IMAGE
# ======================================================

async def download_image(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return None

            data = await response.read()

    image = np.frombuffer(data, np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    return image


# ======================================================
# PREPROCESS IMAGE
# ======================================================

def preprocess(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    gray = cv2.GaussianBlur(
        gray,
        (3, 3),
        0,
    )

    _, thresh = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU,
    )

    return thresh
    # ======================================================
# EXTRACT MINUTES
# ======================================================

def extract_minutes(results):
    """
    Extract workout duration from OCR results.

    Priority:
    1. Time field (Garmin)
    2. Any Xm Ys format
    3. XX min format
    4. HH:MM:SS
    5. MM:SS
    """

    # -----------------------------------------
    # Check every OCR line individually
    # -----------------------------------------

    for _, text, _ in results:

        line = text.lower().strip()

        # 15m 18s
        match = re.search(
            r"(\d{1,3})\s*m(?:in)?\s*(\d{1,2})?\s*s",
            line,
        )

        if match:
            return int(match.group(1))

        # 60 min
        match = re.search(
            r"(\d{1,3})\s*(?:min|mins|minute|minutes)$",
            line,
        )

        if match:
            return int(match.group(1))

    # -----------------------------------------
    # Fallback to combined OCR text
    # -----------------------------------------

    full_text = " ".join(
        text.lower()
        for _, text, _ in results
    )

    # Look specifically after the word "Time"
    match = re.search(
        r"time.*?(\d{1,3})\s*m(?:in)?\s*(\d{1,2})?\s*s",
        full_text,
        re.IGNORECASE | re.DOTALL,
    )

    if match:
        return int(match.group(1))

    # HH:MM:SS
    match = re.search(
        r"(\d{1,2}):(\d{2}):(\d{2})",
        full_text,
    )

    if match:
        hours = int(match.group(1))
        minutes = int(match.group(2))

        return hours * 60 + minutes

    # MM:SS
    match = re.search(
        r"(\d{1,2}):(\d{2})",
        full_text,
    )

    if match:
        return int(match.group(1))

    return None
    # ======================================================
# EXTRACT WORKOUT DATE
# ======================================================

def extract_workout_date(results):
    """
    Extract a workout date from OCR results.

    Supports:
    July 14, 2026
    July 14,2026
    Jul 14, 2026
    Jul 14,2026
    """

    full_text = " ".join(
        text for _, text, _ in results
    )

    # Normalize commas
    full_text = re.sub(r",\s*", ", ", full_text)

    pattern = (
        r"(January|February|March|April|May|June|July|August|"
        r"September|October|November|December|"
        r"Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)"
        r"\s+"
        r"(\d{1,2})"
        r",\s*"
        r"(\d{4})"
    )

    match = re.search(
        pattern,
        full_text,
        re.IGNORECASE,
    )

    if not match:
        return None

    date_string = f"{match.group(1)} {match.group(2)}, {match.group(3)}"

    for fmt in ("%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(
                date_string,
                fmt,
            ).date()
        except ValueError:
            pass

    return None


# ======================================================
# OCR CONFIDENCE
# ======================================================

def calculate_confidence(results):
    """
    Returns the average OCR confidence (0.00 - 1.00)
    """

    if not results:
        return 0.0

    scores = [
        confidence
        for _, _, confidence in results
    ]

    return round(
        sum(scores) / len(scores),
        2,
    )
# ======================================================
# VERIFY WORKOUT
# ======================================================

async def verify_workout(image_url):
        """
        Downloads the workout screenshot, performs OCR,
        extracts workout information, and returns the results.
        """

        # Download image
        image = await download_image(image_url)

        if image is None:
            return {
                "success": False,
                "reason": "Unable to download image.",
            }

        # Preprocess image
        processed = preprocess(image)

        # Run OCR
        results = reader.readtext(processed)

        # Combine OCR text
        full_text = " ".join(
            text
            for _, text, _ in results
        )

        # =====================================
        # DEBUG OUTPUT
        # =====================================

        print("\n========== OCR ==========")
        print(full_text)
        print("=========================\n")

        print("\n========== OCR LINES ==========")

        for _, text, confidence in results:
            print(f"[{confidence:.2f}] {text}")

        print("===============================\n")

        # =====================================
        # Extract information
        # =====================================

        minutes = extract_minutes(results)
        workout_date = extract_workout_date(results)
        confidence = calculate_confidence(results)

        # =====================================
        # More debug info
        # =====================================

        print(f"Minutes Found      : {minutes}")
        print(f"Workout Date Found : {workout_date}")
        print(f"OCR Confidence     : {confidence}")

        # =====================================
        # Return data
        # =====================================

        return {
            "success": minutes is not None,
            "minutes": minutes,
            "workout_date": workout_date,
            "confidence": confidence,
            "text": full_text,
            "results": results,
        }
