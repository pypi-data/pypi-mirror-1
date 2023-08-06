#---------- find_urls.py----------#
# Functions to identify and extract URLs and email addresses

import re

def fix_urls(text):
    pat_url = re.compile(  r'''(?x) (((\s((http|ftp|https)://(\S*)\.)|((http|ftp|https)://))\S+\.\S+)|((\S+)\.(\S+)\.(\S+))) ''')
    pat_email = re.compile(r'''(?x) ((\S+)@(\S+)\.(\S+))''')

    for url in re.findall(pat_url, text):
        if url[0].startswith('http'):
            text = text.replace(url[0], '<a href="%(url)s">%(url)s</a>' % {"url" : url[0]})
        else:
            text = text.replace(url[0], '<a href="http://%(url)s">%(url)s</a>' % {"url" : url[0]})

    for email in re.findall(pat_email, text):
        text = your_string.replace(email[1], '<a href="mailto:%(email)s">%(email)s</a>' % {"email" : email[1]})

    return text

if __name__ == '__main__':
    print fix_urls("test http://google.com asdasdasd some more text")