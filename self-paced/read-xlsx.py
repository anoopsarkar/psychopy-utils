import openpyxl
wb = openpyxl.load_workbook("test.xlsx")
print wb.get_sheet_names()
for ws in wb:
    for row in ws.rows:
        for cell in row:
            print cell.value,
        print
