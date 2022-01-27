import sqlite3


def find_duplicates():
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()
    sql_query = """
                WITH CTE AS
                (SELECT id, source, date_time, RANK() OVER (PARTITION BY date_time,
                source ORDER BY num) rnk
                FROM (SELECT *, ROW_NUMBER() OVER(PARTITION BY date_time,
                source ORDER BY date_time, source) num
                FROM VK_events) X)
                SELECT id FROM CTE WHERE rnk > 1
                """

    cursor.execute(sql_query)
    result = cursor.fetchall()
    # print(result)
    conn.commit()
    conn.close()
    return result  # [(2,), (3,), (4,), (5,)]


def delete_rows(id_list):
    try:
        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()
        for id_ in id_list:
            sql_delete_query = f'DELETE from VK_events where id == {id_[0]}'
            cursor.execute(sql_delete_query)
            conn.commit()
        conn.close()
    except sqlite3.Error as error:
        print("Failed to delete record from sqlite table", error)
    finally:
        if conn:
            conn.close()
            print("the sqlite connection is closed")


def main():
    delete_rows(find_duplicates())


if __name__ == '__main__':
    main()
