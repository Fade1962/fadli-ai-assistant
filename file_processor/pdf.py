import pymupdf


def process_pdf(filename):

    try:

        document = pymupdf.open(filename)

        pages = []

        for page in document:

            text = page.get_text()

            if text:
                pages.append(text)

        document.close()

        result = "\n\n".join(pages).strip()

        if not result:

            return (
                "PDF berhasil dibuka, "
                "tetapi tidak ditemukan teks. "
                "Kemungkinan PDF berupa hasil scan/gambar."
            )

        return result


    except Exception as error:

        print(
            "PDF PROCESS ERROR:",
            repr(error)
        )

        raise
