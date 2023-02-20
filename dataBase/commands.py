from dataBase.db import connection


async def read():
    with connection.cursor() as cursor:
        cursor.execute("""SELECT * FROM info_user;""")
        data = cursor.fetchall()
        list_data = []
        for i in data:
            list_data.append(i)
        return list_data


# Whatsapp
async def add_deatil(data):
    id_order = data['id']
    user_name = data['name']
    phone = data['phone']
    product = data['product']
    sku = data['sku']
    status = data['status']
    price = data['price'],
    address = data['address']
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO info_user(id_order, user_name, phone, product, status, sku, price, address) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);", (id_order, user_name, phone, product, status, sku, price, address))


async def get_data_info2():
    data = []
    with connection.cursor() as cursor:
        cursor.execute("SELECT id_order FROM info_user;")
        for i in cursor.fetchall():
            data.append(int(i[0]))
    return data