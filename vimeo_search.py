import json
import requests
import base64
import argparse
import math

ACCESS_TOKEN = ''
CLIENT_IDENTIFIER = ''
CLIENT_SECRET = ''
AUTH_STRING = base64.b64encode(f'{CLIENT_IDENTIFIER}:{CLIENT_SECRET}'.encode('ascii')).decode('ascii')

# GET https://api.vimeo.com/videos

def search_vimeo(query:str, cc_filter:str = None):
    '''
    cc_filter options:
    CC - Return videos under any Creative Commons license.
    CC-BY - Return CC BY, or attribution-only, videos.
    CC-BY-NC - Return CC BY-NC, or Attribution-NonCommercial, videos.
    CC-BY-NC-ND - Return CC BY-NC-ND, or Attribution-NonCommercial-NoDerivs, videos.
    CC-BY-NC-SA - Return CC BY-NC-SA, or Attribution-NonCommercial-ShareAlike, videos.
    CC-BY-ND - Return CC BY-ND, or Attribution-NoDerivs, videos.
    CC-BY-SA - Return CC BY-SA, or Attribution-ShareAlike, videos.
    CC0 - Return CC0, or public domain, videos.
    '''
    if cc_filter not in [None, 'CC', 'CC-BY', 'CC-BY-NC', 'CC-BY-NC-ND', 'CC-BY-NC-SA', 'CC-BY-ND', 'CC-BY-SA', 'CC0']:
        raise ValueError('cc_filter must be one of: CC, CC-BY, CC-BY-NC, CC-BY-NC-ND, CC-BY-NC-SA, CC-BY-ND, CC-BY-SA, CC0')
    
    url = "https://api.vimeo.com/videos"
    headers = {'content-type': 'application/json', 'Authorization': f'Basic {AUTH_STRING}'}
    page = 1
    ret = []
    while response := requests.get(url,
                                    headers=headers, 
                                    params={
                                        'direction': 'desc',
                                        'filter': cc_filter,
                                        'query': query,
                                        'sort': 'relevant',
                                        'per_page': '100',
                                        'page': f'{page}'
                                    }):
        response_json = response.json()
        ret.extend(response_json['data'])
        page += 1
        if response_json['paging']['next'] == None:
            break
    return ret

def duration_filter(j, min_duration: int, max_duration: int):
    if not min_duration:
        min_duration = 0
    if not max_duration:
        max_duration = math.inf
    return [video for video in j if min_duration <= video['duration'] <= max_duration]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('query', help='Search query')
    parser.add_argument('--cc_filter', default=None, choices=['CC', 'CC-BY', 'CC-BY-NC', 'CC-BY-NC-ND', 'CC-BY-NC-SA', 'CC-BY-ND', 'CC-BY-SA', 'CC0'], help='Creative Commons filter')
    parser.add_argument('--min_duration', type=int, default=None, help='Minimum duration in seconds')
    parser.add_argument('--max_duration', type=int, default=None, help='Maximum duration in seconds')
    parser.add_argument('--output', default=None, help='Output file')
    args = parser.parse_args()
    j = search_vimeo(args.query, args.cc_filter)
    if args.min_duration or args.max_duration:
        j = duration_filter(j, args.min_duration, args.max_duration)
    j = [x['link'] for x in j]
    if args.output:
        with open(args.output, 'w') as f:
            print(*j, file=f, sep='\n')
    else:
        print(*j, sep='\n')
