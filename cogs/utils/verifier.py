import re
import aiohttp
import easyocr
import numpy as np
import cv2

from datetime import datetime

# ==========================================
# OCR
# ==========================================

reader = easyocr.Reader(
    ["en"],
    gpu=False,
)


# ==========================================
# DOWNLOAD IMAGE
# ==========================================

async def download_image(url: str):

    async with aiohttp.ClientSession() as session:

        async with session.get(url) as response:

            if response.status != 200:
                return None

            data = await response.read()

    image = np.frombuffer(
        data,
        np.uint8,
    )

    image = cv2.imdecode(
        image,
        cv2.IMREAD_COLOR,
    )

    return image


# ==========================================
# PREPROCESS
# ==========================================

def preprocess(image):

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY,
    )

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


# ==========================================
# EXTRACT MINUTES
# ==========================================

def extract_minutes(text):

    text = text.lower()

    #
    # Look after the word "time"
    #

    search_text = text

    if "time" in text:
        search_text = text.split(
            "time",
            1,
        )[1]

    #
    # 15m 18s
    #

    match = re.search(
        r"(\d{1,3})\s*m(?:in)?s?\s*(\d{1,2})?\s*s?",
        search_text,
    )

    if match:
        return int(match.group(1))

    #
    # 60 min
    #

    match = re.search(
        r"(\d{1,3})\s*(min|mins|minute|minutes)",
        search_text,
    )

    if match:
        return int(match.group(1))

    #
    # 1:15:18
    #

    match = re.search(
        r"(\d{1,2}):(\d{2}):(\d{2})",
        search_text,
    )

    if match:

        hours = int(match.group(1))
        minutes = int(match.group(2))

        return hours * 60 + minutes

    #
    # 15:18
    #

    match = re.search(
        r"(\d{1,2}):(\d{2})",
        search_text,
    )

    if match:
        return int(match.group(1))

    return None
    # ==========================================
    # EXTRACT WORKOUT DATE
    # ==========================================

    def extract_workout_date(text):

        #
        # Garmin sometimes omits the space after commas.
        #

        text = text.replace(",", ", ")

        #
        # Look for:
        #
        # July 14, 2026
        # Jul 14, 2026
        #

        match = re.search(

            r"(January|February|March|April|May|June|July|August|September|October|November|December|"
            r"Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
            r"\s+\d{1,2},?\s*\d{4}",

            text,

            re.IGNORECASE,

        )

        if not match:
            return None

        date_text = match.group(0)

        #
        # Normalize spacing
        #

        date_text = date_text.replace(",", ", ")

        date_text = " ".join(date_text.split())

        #
        # Try full month first
        #

        try:

            return datetime.strptime(
                date_text,
                "%B %d, %Y",
            ).date()

        except ValueError:
            pass

        #
        # Try abbreviated month
        #

        try:

            return datetime.strptime(
                date_text,
                "%b %d, %Y",
            ).date()

        except ValueError:
            pass

        return None


    # ==========================================
    # OCR CONFIDENCE
    # ==========================================

    def calculate_confidence(results):

        if not results:
            return 0

        return round(

            sum(result[2] for result in results)

            / len(results),

            2,

        )
        # ==========================================
        # VERIFY WORKOUT
        # ==========================================

async def verify_workout(image_url):

    # Download image
    image = await download_image(image_url)

    if image is None:
        return {
            "success": False,
            "reason": "Unable to download image.",
        }

    # Preprocess image
    processed = preprocess(image)

    # OCR
    results = reader.readtext(processed)

    # Combine OCR text
    full_text = " ".join(
        result[1]
        for result in results
    )

    # Debug
    print("\n========== OCR ==========")
    print(full_text)
    print("=========================\n")

    # Extract data
    minutes = extract_minutes(full_text)
    workout_date = extract_workout_date(full_text)

    # Confidence
    confidence = calculate_confidence(results)

    return {
        "success": minutes is not None,
        "minutes": minutes,
        "workout_date": workout_date,
        "confidence": confidence,
        "text": full_text,
    }