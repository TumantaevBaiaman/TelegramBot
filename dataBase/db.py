import psycopg2
from config.settings import DB_INFO
try:
    connection = psycopg2.connect(
        host=DB_INFO.get('host'),
        user=DB_INFO.get('user'),
        password=DB_INFO.get('password'),
        database=DB_INFO.get('db_name'),
    )
    connection.autocommit = True

    with connection.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS info_user(
                id_order bigint NOT NULL,
                user_name varchar(50) NOT NULL,
                phone varchar(50) NOT NULL,
                product varchar(255) NOT NULL,
                status varchar(50),
                sku varchar(50) NOT NULL,
                price varchar(50) NOT NULL,
                address varchar (150) NOT NULL
                );
                """
        )

except Exception as ex:
    print("Error")

finally:
    pass