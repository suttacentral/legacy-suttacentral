"""Deploy to production server tasks."""

from tasks.helpers import *
import requests
import sc

def prettyerrors(errors):
    out = []
    for obj in errors:
        for k,v in sorted(obj.items()):
            out.append('{}: {}'.format(k, v))
    return '\n'.join(out)

def get_request_data(r):
    """returns the JSON data for request, only if there are no errors"""
    try:
        d = r.json()
    except Exception as e:
        d = None
    
    if r.status_code != 200 or d and d['errors']:
        warning("Connection failed with status code of {}".format(r.status_code))
        if d['errors']:
            warning(prettyerrors(d['errors']))
        else:
            warning(r.text)
        return None
    return d

@task
def purge_cache(force=False):
    """Send fpurge_ts POST request to Cloudflare to purge cache"""
    api_key = sc.config.cloudflare['api_key']
    email = sc.config.cloudflare['email']
    base_url = 'https://api.cloudflare.com/client/v4/'
    

    if not api_key or not email:
        warning("Unable to make request because Cloudflare api_key or email is not defined")
        return
    
    # First discover object id (we could probably cache this)
    r = requests.get(url=base_url + 'zones/', 
                      headers={
                        'X-Auth-Email': email,
                        'X-Auth-Key': api_key,
                        'Content-Type': 'application/json'
                     })

    
    d = get_request_data(r)
    if d is None:
        return
    object_id = d['result'][0]['id']
    
    r = requests.delete(url=base_url + 'zones/{}/purge_cache'.format(object_id), 
                        headers={
                            'X-Auth-Email': email,
                            'X-Auth-Key': api_key,
                            'Content-Type': 'application/json'
                        },
                        data={
                            #"purge_everything": True
                            "files": ["https://suttacentral.net"]
                        })
    d = get_request_data(r)
    if d:
        notice("Success")
        
