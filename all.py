import vk_api
import re
from datetime import date as d
from datetime import datetime
import insertings
import select_event


groups = {'Книжный клуб Бездействие': -62622395,
          'Уличная эпистемология': -165566939,
          'Книжный клуб в СПб': -55130788,
          'Итальянская 16': -161320870,
          'Дискуссионный клуб': -204499696,
          'Книжный клуб Книгочай': -37124231,
          }


def get_posts(group_id, n):  # n is amount of posts
    """Return list of n dictionaries with posts"""
    session = vk_api.VkApi(token='250a634d14a734f4e6a2422fd581ef4d3aabcd51646097676a6b4fac22baa74831ef5aec48ccbe4009706')
    post_ = session.method('wall.get', {'owner_id': group_id, 'count': n})
    return post_['items']


def filter_old_events(event_date):
    """Take timestamp of event and compare to date"""
    if datetime.fromtimestamp(event_date).date() < d.today():
        print('outdated event: ', datetime.fromtimestamp(event_date).date())
        return True
    return False


def extract_text_link(advert, group_id):
    """Return as tuple (text of advert, vk-link to wall post containing that advert)."""
    if advert.get('copy_history', -1) != -1:  # check if it's a repost
        advert = advert['copy_history'][0]
    post_id = advert['id']
    link_ = 'https://vk.com/wall' + str(group_id) + '_' + str(post_id)
    return advert['text'], link_


months = {"января": 1, "февраля": 2, "марта": 3, "апреля": 4, "мая": 5, "июня": 6,
          "июля": 7, "августа": 8, "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12}


def search_pattern(timestamp, tuple_text_link):
    some_post, link = tuple_text_link
    date_pattern = r'(\d\d?)\s*([а-я]{3,8})'  # 13 октября
    date = re.search(date_pattern, some_post)
    if date is None or date.group(2) not in months.keys():
        return None
   
    text_after_date = some_post[date.end():]  # text slice from date end

    date_ = create_datetime(create_date_string(timestamp, date.groups(),
                                         extract_time(text_after_date)))
    if filter_old_events(date_):
        return None
    description = cut_description(text_after_date)
    place = clean_text(search_place(text_after_date))
    address = clean_text(search_address(text_after_date))
    return date_, description, place, address, link


def extract_time(description):
    """Extract time from description. Return string 00:00 or 00.00"""
    template = '(\d\d:\d\d)|(\d\d.\d\d)'
    time = re.search(template, description)
    if time:
        return time.group()
    else:
        return '00:00'


def event_date_with_year(timestamp, event_date):
    """Take timestamp of posting advert + date like ('6', 'июня');
     return string %d/%m/%Y"""
    dt_object = datetime.fromtimestamp(timestamp)  # get date of posting advert as datetime object
    # print('timestamp', dt_object)
    dt_string = dt_object.strftime("%d/%m/%Y")  # get date of posting advert as string
    # print(event_date[1])
    if int(dt_string[3:5]) > months[event_date[1]]:
        year = int(dt_string[6:]) + 1
    else:
        year = int(dt_string[6:])
    return f'{event_date[0]}/{months[event_date[1]]}/{year}'  # string %d/%m/%Y


def create_date_string(timestamp, date, time):
    """Take timestamp, date like ('2', 'июня'); return string like 2/06/2021 09:15."""
    dt_string = f'{event_date_with_year(timestamp, date)} {time[:2]}:{time[3:]}'  # "2/06/2021 09:15"
    return dt_string


def create_datetime(date_string):
    """Return timestamp object from string like 2/06/2021 09:15"""
    # print('def create_datetime')
    # print(datetime.strptime(date_string, "%d/%m/%Y %H:%M"))
    return datetime.timestamp(datetime.strptime(date_string, "%d/%m/%Y %H:%M"))


def clean_text(text):
    template = '[^\wа-яА-Я\d\n\s:;-_]'
    return re.sub(template, '', text, count=0, flags=re.IGNORECASE + re.ASCII)


def cut_description(text):
    template = r'(?<=\n).+\n'
    if re.search(template, text):
        crop_point = re.search(template, text).end()
        return text[:crop_point]
    else:
        return text[:400]


def search_place(cropped_text):
    try:
        template1 = [r'(?<=Место:)\n?.+\n', r'(?<=Место проведения:)\n?.+\n',
                     r'(?<=Место встречи:)\n?.+\n', r'(?<=Где:)\n?.+\n']
        place = ''
        for template_ in template1:
            result = re.search(template_, cropped_text, flags=re.IGNORECASE)
            if result:
                place = result.group()
        return place
    except AttributeError:
        return None


def search_address(cropped_text):
    try:
        template2 = [r'(?<=Адрес проведения:)\n?.+\n', r'(?<=Адрес:)\n?.+\n']
        address = ''
        for template_ in template2:
            result = re.search(template_, cropped_text, flags=re.IGNORECASE)
            if result:
                address = result.group()
        return address
    except AttributeError:
        return None


def write_file(counter_, source_group, date, description, place, address, link):
    with open('all_results.txt', 'a', encoding='utf-8') as f:
        f.write(f'{counter_}) source: {source_group} \n')
        f.write(f'date: {datetime.fromtimestamp(date)} \n')
        #
        f.write(description)
        f.write(f'place: {place} \naddress: {address}')
        f.write(f'\nlink: {link} \n')
        f.write('--------------------------------------------------------------------\n')
        return counter_ + 1


def main():
    counter = 1
    insertings.create_table()
    select_event.write_select_in_html()
    # for group in groups.items():
    #     posts = get_posts(group[1], 10)  # here you can put any group id and number of posts
    #     for post in posts:
    #         timestamp = post['date']
    #         info_ = search_pattern(timestamp, extract_text_link(post, group[1]))
    #         if info_:
    #             # write to VK_events table inside events.db
    #             insertings.transfer_to_sql(group[0], info_[0], info_[1], info_[2], info_[3], info_[4])
    #             # counter = write_file(counter, group[0], info_[0], info_[1], info_[2], info_[3], info_[4])
               


if __name__ == '__main__':
    main()
