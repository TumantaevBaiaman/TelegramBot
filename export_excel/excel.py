from dataBase import commands
import xlsxwriter

async def export_data():
    workbook = xlsxwriter.Workbook('info_user.xlsx')
    worksheet = workbook.add_worksheet("1 sheet")
    row = 1
    col = 0
    head_style = workbook.add_format(
        {
            'bold': True, 'border': 2, 'align': 'center', 'bg_color': "green", "color": "white"
        }
    )
    align_text = workbook.add_format(
        {
            'align': 'center'
        }
    )
    bg_text = workbook.add_format(
        {
            'bg_color': 'green', 'color': 'white'
        }
    )
    columns = [
        'id_order',
        'username',
        'phone',
        'product',
        'status',
        'sku',
        'price',
        'address'
    ]
    data = await commands.read()
    worksheet.set_column('A:A', 25)
    worksheet.set_column('B:B', 25)
    worksheet.set_column('C:C', 25)
    worksheet.set_column('D:D', 70)
    worksheet.set_column('E:E', 25)
    worksheet.set_column('F:F', 25)
    worksheet.set_column('G:G', 15)
    worksheet.set_column('H:H', 40)
    for index, value in enumerate(columns):
        worksheet.write(0, index, value, head_style)
    for i in data:
        worksheet.write(row, col, i[0], align_text)
        worksheet.write(row, col + 1, i[1])
        worksheet.write(row, col + 2, i[2])
        worksheet.write(row, col + 3, i[3])
        worksheet.write(row, col + 4, i[4])
        worksheet.write(row, col + 5, i[5])
        worksheet.write(row, col + 6, i[6], bg_text)
        worksheet.write(row, col + 7, i[7])
        row += 1
    workbook.close()