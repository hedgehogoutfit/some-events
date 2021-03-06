import vk_api
import re
from datetime import date as d


groups = {'Книжный клуб Бездействие': -62622395,
          'Уличная эпистемология': -165566939,
          'Книжный клуб в СПб': -55130788,
          'Итальянская 16': -161320870,
          'Дискуссионный клуб': -204499696,
          'Книжный клуб Книгочай': -37124231,
          }


def get_posts(group_id, n):  # n is amount of posts
    """Return list of n dictionaries with posts"""
    session = vk_api.VkApi(token='')
    post_ = session.method('wall.get', {'owner_id': group_id, 'count': n, 'post_type': 'post'})
    return post_['items']


def create_date(date, months):
    """Return date object"""
    day = int(date.group(1))
    mon = months[date.group(2)]
    year = d.today().year
    return d(year, mon, day)


def filter_old_events(date_obj):
    if date_obj < d.today():
        return True
    return False


def extract_text_link(advert, group_id):

    if advert.get('copy_history', -1) != -1:  # check if it's a repost
        advert = advert['copy_history'][0]
    post_id = advert['id']
    link_ = 'https://vk.com/wall' + str(group_id) + '_' + str(post_id)
    return advert['text'], link_


months = {"января": 1, "февраля": 2, "марта": 3, "апреля": 4, "мая": 5, "июня": 6,
          "июля": 7, "августа": 8, "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12}


def search_pattern(tuple_text_link):
    some_post, link = tuple_text_link
    date_pattern = r'(\d\d?)\s*([а-я]{3,8})'  # 13 октября
    date = re.search(date_pattern, some_post)
    if date is None or date.group(2) not in months.keys():
        return None

    date_ = date.group()  # full date like 6 июня
    text_after_date = some_post[date.end():]  # text slice from date end
    description = cut_description(text_after_date)
    place = clean_text(search_place(text_after_date))
    address = clean_text(search_address(text_after_date))
    return date_, description, place, address, link


def extract_time(description):
    pass


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
                     r'(?<=Место встречи:)\n?.+\n']
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
        f.write(f'date: {date} \n')
        f.write(description)
        f.write(f'place: {place} \naddress: {address}')
        f.write(f'\nlink: {link} \n')
        f.write('--------------------------------------------------------------------\n')
        return counter_ + 1


def main():
    counter = 1
    for group in groups.items():
        posts = get_posts(group[1], 10)
        for post in posts:
            info_ = search_pattern(extract_text_link(post, group[1]))
            if info_:
                """Here should be func that inserts values in database"""
                counter = write_file(counter, group[0], info_[0], info_[1], info_[2], info_[3], info_[4])


if __name__ == '__main__':
    main()
