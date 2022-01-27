import sqlite3


def create_table():
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE if not exists VK_events (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                   "source VARCHAR(255), date_time TIMESTAMP, description VARCHAR(255), "
                   "place VARCHAR(255), address VARCHAR(255), link VARCHAR(255))")
    print('the table VK_events already exists in events.db')
    conn.commit()
    conn.close()


def transfer_to_sql(data0, data1, data2, data3, data4, data5):
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO VK_events(source, date_time, description, place, address, link)"
                   " VALUES (?, ?, ?, ?, ?, ?)", (data0, data1, data2, data3, data4, data5))
    conn.commit()
    conn.close()


def main():
    create_table()
    transfer_to_sql(source, date, description, place, address, link)


if __name__ == '__main__':
    main()
