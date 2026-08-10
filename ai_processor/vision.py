import os

from google import genai
from google.genai import types


GEMINI_API_KEY = os.environ.get(
    "GEMINI_API_KEY",
    ""
)


def get_mime_type(filename):

    extension = os.path.splitext(
        filename
    )[1].lower()

    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }

    return mime_types.get(
        extension,
        "image/jpeg"
    )


def analyze_image(
    filename,
    prompt=None
):

    if not GEMINI_API_KEY:

        raise Exception(
            "GEMINI_API_KEY_MISSING"
        )


    if not prompt:

        prompt = """
Kamu sedang menganalisis sebuah gambar
yang dikirim oleh Fadli.

Analisis gambar secara langsung.

Jelaskan:

1. Apa yang terlihat.
2. Objek utama.
3. Orang jika memang terlihat.
4. Teks yang terlihat.
5. Konteks gambar.
6. Jika berupa desain:
   - layout
   - warna
   - typography
   - hierarchy
   - komposisi
   - kekurangan
   - saran perbaikan
7. Jika berupa dokumen:
   - isi utama
   - informasi penting
   - tabel jika ada
8. Jika berupa screenshot:
   - jelaskan isi layar
   - error jika ada
   - informasi penting.

Jangan hanya melakukan OCR.

Gunakan kemampuan vision untuk memahami
isi visual gambar.

Jangan mengarang sesuatu yang tidak terlihat.

Jika sesuatu tidak jelas, katakan tidak jelas.
"""


    print(
        "VISION → Gemini"
    )


    client = genai.Client(
        api_key=GEMINI_API_KEY
    )


    with open(
        filename,
        "rb"
    ) as file:

        image_bytes = file.read()


    mime_type = get_mime_type(
        filename
    )


    response = client.models.generate_content(

        model="gemini-2.5-flash",

        contents=[

            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type
            ),

            prompt

        ]
    )


    answer = getattr(
        response,
        "text",
        None
    )


    if not answer:

        raise Exception(
            "GEMINI_VISION_EMPTY"
        )


    return answer.strip()
