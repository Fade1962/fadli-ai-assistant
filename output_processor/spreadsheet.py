from openpyxl import Workbook



def create_xlsx(filename, rows):


    wb = Workbook()


    ws = wb.active


    ws.title = "Fadli AI"



    for row in rows:

        ws.append(row)



    wb.save(filename)


    return filename
