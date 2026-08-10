from pptx import Presentation



def create_pptx(filename, title, body):


    prs = Presentation()


    slide = prs.slides.add_slide(

        prs.slide_layouts[1]

    )


    slide.shapes.title.text = title


    slide.placeholders[1].text = body


    prs.save(filename)


    return filename
