import urllib2
import urllib
import os
import json
from math import ceil
import sys
import re
 
TWITPIC_SHOW_URL = 'http://api.twitpic.com/2/users/show.{format}'
TWITPIC_PICS_PAGE = 20
TWITPIC_FULL_URL = 'http://twitpic.com/{short_id}/full'
 
twitpic_cdn_re = re.compile(r'(http://(\w)+(\.cloudfront\.net)' +
                            r'(/(\w|\.|\?)+)+)')
 
USAGE = '''
        Welcome to twitpic pics retriever. Usage:
        python photograb.py [username] [path]
        '''
 
 
def expanduser(path):
    if path.find('~') >= 0:
            path = path.replace('~', os.path.expanduser('~'))
    return path
 
 
def format_filename(timestamp):
    timestamp = timestamp.replace(r'-', '_')
    timestamp = timestamp.replace(r' ', '_')
    timestamp = timestamp.replace(r'/', '_')
    timestamp = timestamp.replace(r':', '_')
    return '{0}.jpg'.format(timestamp)
 
 
def get_twitpic_image_url(content):
    results = twitpic_cdn_re.search(content)
    return content[results.start():results.end()]
 
 
def get_req(base_url, params):
    data = urllib.urlencode(params)
    full_url = '{base_url}?{data}'.format(base_url=base_url, data=data)
    response = urllib2.urlopen(full_url)
    return json.loads(response.read())
 
 
def main(username, pics_dest):
    user_images_count_req = get_req(TWITPIC_SHOW_URL.format(format='json'),
                                    {'username': username})
    photo_count = int(user_images_count_req['photo_count'])
    pages_count = int(ceil(photo_count / float(TWITPIC_PICS_PAGE)))
    print ('There are {count} images available ' +
           'on twitpic ({pages} pages).').format(count=photo_count,
                                                 pages=pages_count)
    print 'retrieving pictures...'
 
    for page_num in range(1, pages_count + 1):
        print 'page {page_num}...'.format(page_num=page_num)
        page_req = get_req(TWITPIC_SHOW_URL.format(format='json'),
                           {'username': username,
                            'page': page_num})
 
        for image in page_req['images']:
            short_id = image['short_id']
            timestamp = image['timestamp']
            filename = format_filename(timestamp)
            content = urllib2.urlopen(TWITPIC_FULL_URL.format(
                                      short_id=short_id)).read()
            cdn_url = get_twitpic_image_url(content)
            urllib.urlretrieve(cdn_url, os.path.join(pics_dest, filename))
 
    print 'done.'
 
 
if __name__ == '__main__':
    try:
        if sys.argv[1].find('-h') >= 0 and sys.argv[1].find('-h') <= 1:
            print USAGE
            sys.exit(0)
    except IndexError:
        pass
    try:
        username = sys.argv[1]
    except IndexError:
        print '[error] username not specified.'
        print USAGE
        sys.exit(1)
    try:
        path = sys.argv[2]
        path = expanduser(path)
        if not(os.path.exists(path)):
            print '[error] {path} does not exists.'.format(path=path)
            sys.exit(1)
    except IndexError:
        print '[error] path not specified'
        sys.exit(1)
    print 'username: {u}'.format(u=username)
    print 'destination: {d}'.format(d=path)
    main(username, path)
