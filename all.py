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
    post_ = session.method('wall.get', {'owner_id': group_id, 'count': n})
    return post_['items']


def create_date(date, months):
    """Return date object"""
    day = int(date.group(1))
    mon = months[date.group(2)]
    year = d.today().year
    return d(year, mon, day)


def extract_text_link(item, group_id):

    if item.get('copy_history', -1) != -1:
        item = item['copy_history'][0]
    post_id = item['id']
    link_ = 'https://vk.com/wall' + str(group_id) + '_' + str(post_id)
    return item['text'], link_


def search_pattern(text, link):
    months = {"января": 1, "февраля": 2, "марта": 3, "апреля": 4, "мая": 5, "июня": 6, "июля": 7,
              "августа": 8, "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12}

    date_pattern = r'(\d\d?)\s([а-я]{3,8})'  # 13 октября
    date = re.search(date_pattern, text)
    if date is None or date.group(2) not in months.keys():
        return None
    date_obj = create_date(date, months)

    text = text[date.end():]
    """can be None"""
    next_2_sent = re.compile(r"""([^\.\?!]+     # one sentence: any character exept ?.!
                                 (\.|\?|!))     # end of the sentence: punctuation
                                 {1,2}          # 1 or 2 sentences
                                 """, flags=re.VERBOSE)

    """Here i exclude all dates that for some reason don't have text after them. Need to check what are these 
    dates later"""
    try:
        text = next_2_sent.match(text).group()
    except AttributeError:
        return None
    replaced = [r'\(.+\)', r'\[.+\]']  # replace all braces
    for repl in replaced:
        text = re.sub(repl, '', text)
    return {'date': date_obj, 'description': text, 'link': link}


def write_file(uwu, counter_):
    """Just for tests"""
    with open('test_results.txt', 'a') as f:
        f.write(f'{counter_})\n')
        f.write(f'~date: {uwu["date"]}\n')
        f.write(f'~description: {uwu["description"]}\n')
        f.write(f'~link: {uwu["link"]}')
        f.write('\n-------------------------------------------------\n\n')
        return counter_ + 1


if __name__ == '__main__':
    counter = 1
    for value in groups.values():
        idi = value
        posts = get_posts(idi, 20)
        for post in posts:
            text_, lnk = extract_text_link(post, idi)
            bla = search_pattern(text_, lnk)
            if bla:
                """Here should be func that inserts values in database"""
                counter = write_file(bla, counter)
