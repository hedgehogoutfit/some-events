import sqlite3
from datetime import datetime


def select_from_sql():
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()
    cursor.execute('select * from VK_events')
    data_ = cursor.fetchall()
    conn.commit()
    conn.close()
    # print(data_)
    return data_


def write_select_in_html():
    data = select_from_sql()
    print('results for select from the table VK_events / events.db:')
    for row in data:
        print(row)
        with open('events.html', 'a', encoding='utf-8') as out_file:
            out_file.write(f'id: {row[0]}<br>\n')
            for index in list(range(1, 7)):
                try:
                    if index == 2:
                        out_file.write((datetime.fromtimestamp(row[index])).strftime("%d/%m/%Y %H:%M"))
                    else:
                        out_file.write(row[index])
                except TypeError:
                    out_file.write(str(row[index]))
                out_file.write('<br>')
                out_file.write('\n')


def main():
    write_select_in_html()


if __name__ == '__main__':
    main()
