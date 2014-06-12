import re
import gzip
import os
import time
import json
import codecs
import urllib.request, urllib.parse  # urllib.error
import pytz
from datetime import timedelta, datetime
#from jinja2 import Environment, FileSystemLoader

from mojibake.app import db, models
from mojibake.settings import API_URL, API_KEY, LOG_DIR, SEARCH_STRING, \
    FAIL2BAN_SEARCH_STRING, ROOT_NOT_ALLOWED_SEARCH_STRING

DIR = os.path.dirname(os.path.realpath(__file__))

#env = Environment(loader=FileSystemLoader(DIR))
#template = env.get_template('template.html')

def tz_setup():
    if time.localtime().tm_isdst:
        displayed_time = time.tzname[time.daylight]
        time_offset = (time.altzone * -1) / 3600
    else:
        displayed_time = time.tzname[0]
        time_offset = (time.timezone * -1) / 3600

    if time_offset > 0:
        time_offset = '+{}'.format(time_offset)

    #Get zone info (aka just set the system time to UTC already)
    #a = os.popen("cat /etc/sysconfig/clock | grep ZONE")  # RHEL
    a = os.popen("cat /etc/timezone")   # Debian
    cat_res = a.read()
    if cat_res:
        #cat_res = cat_res.replace('ZONE="', '')  # Debian doesn't need this
        cat_res = cat_res.replace('"\n', '')
        try:
            sys_tz = pytz.timezone(cat_res)
        except pytz.UnknownTimeZoneError:
            # Couldn't get the time zone properly
            sys_tz = None
    else:
        sys_tz = None


    return displayed_time, time_offset, sys_tz

def check_ip_location(ip):

    params = {'format': 'json', 'key': API_KEY, 'ip': ip, 'timezone': 'false'}
    print('Checking IP - {}'.format(ip))
    url_params = urllib.parse.urlencode(params)
    url = API_URL + '?' + url_params
    url_obj = urllib.request.urlopen(url)
    response = url_obj.read()
    url_obj.close()
    response_dict = json.loads(response)

    return_dict = {}

    if 'cityName' in response_dict and response_dict['cityName'] != '-':
        return_dict['region'] = response_dict['cityName'] + ', ' + response_dict['regionName']
    elif response_dict['regionName'] != '-':
        return_dict['region'] = response_dict['regionName']

    return_dict['county'] = response_dict['countryName']

    return return_dict

def parse_content(content, breakin_attempt, banned_ip, last_month, auth_log):

    for j in content:
        if auth_log:
            # Catch the usual
            # Jun 10 12:40:05 defestri sshd[11019]: Invalid user admin from 61.174.51.217
            m = re.search(SEARCH_STRING, j)
            if m is None:
                # Also catch these
                # Jun  8 04:31:10 defestri sshd[5013]: User root from 116.10.191.234 not allowed because none of user's groups are listed in AllowGroups
                m = re.search(ROOT_NOT_ALLOWED_SEARCH_STRING, j)
            if m:
                if m.group('log_date')[:3] == last_month.strftime('%b'):
                    log_date = datetime.strptime(m.group('log_date'), '%b %d %H:%M:%S')
                    log_date = log_date.replace(year=last_month.year)
                    # Set the time zone info for the system
                    #log_date = log_date.replace(tzinfo=sys_tz)
                    # Convert it to UTC time
                    #log_date = log_date.astimezone(pytz.utc)

                    #sometimes there's multiple entries per second, since we're
                    #not that concerned about to the second accuracy just increment
                    #the seconds until we find a unique log date to put in
                    if log_date in breakin_attempt:
                        while log_date in breakin_attempt:
                            ns = log_date.second+1
                            if ns >= 60:
                                ns = 0
                            log_date = log_date.replace(second=ns)
                    breakin_attempt[log_date] = (m.group('ip_add'), m.group('user'))

        else:
            m = re.search(FAIL2BAN_SEARCH_STRING, j)
            if m:
                    b_time = datetime.strptime(m.group('log_date'),
                                '%Y-%m-%d %H:%M:%S,%f')
                    if b_time.month == last_month.month:
                        banned_ip[b_time] = m.group('ip_add')


    return breakin_attempt, banned_ip

def read_logs(log_dir):

    banned_ip = {}
    breakin_attempt = {}

    last_month = datetime.now().replace(day=1) - timedelta(days=1) #.strftime('%b')
    two_month_ago = last_month.replace(day=1) - timedelta(days=1)

    for i in os.listdir(log_dir):
        if 'auth.log' in i or 'fail2ban.log' in i:
            modified_date = datetime.strptime(time.ctime(os.path.getmtime(
                            os.path.join(log_dir, i))), "%a %b %d %H:%M:%S %Y")
            if  modified_date > two_month_ago:
                if 'auth.log' in i:
                    auth_log = True
                else:
                    auth_log = False
                if os.path.splitext(i)[1] == '.gz':
                    # Use zcat?
                    f = gzip.open(os.path.join(log_dir, i), 'r')
                    file_content = f.read()
                    split_text = file_content.split('\n')
                    breakin_attempt, banned_ip = parse_content(split_text,
                                                               breakin_attempt,
                                                               banned_ip,
                                                               last_month,
                                                               auth_log)

                else:
                    with open(os.path.join(log_dir, i), 'r') as f:
                        breakin_attempt, banned_ip = parse_content(f,
                                                                   breakin_attempt,
                                                                   banned_ip,
                                                                   last_month,
                                                                   auth_log)

    return breakin_attempt, banned_ip

def insert_into_db(ips, breakin_attempts, bans):

    ip_items = {}

    for ip, location in ips.items():
        # Query to see if already exists first
        ip_addr = models.IPAddr.query.filter_by(ip_addr=ip).first()
        if ip_addr is None:
            ip_addr = models.IPAddr(ip)
            if 'region' in location:
                ip_addr.region = location['region']
            ip_addr.country = location['country']
            db.session.add(ip_addr)
            db.session.commit()
        ip_items[ip] = ip_addr

    for attempt_date, attempt_details in breakin_attempts.items:
        new_attempt = models.BreakinAttempts(date=attempt_date,
            user=attempt_details[1])
        new_attempt.ipaddr = ip_items[attempt_details[0]]
        db.session.add(new_attempt)
        db.session.commit()

    for banned_date, banned_ip in bans.items():
        new_ban = models.BannedIPs(date=banned_date)
        new_ban.ipaddr = ip_items[banned_ip]
        db.session.add(new_ban)
        db.session.commit()

def parse():

    print('Begin.')
    last_month = datetime.now().replace(day=1) - timedelta(days=1)
    print('Timezone setup...')
    displayed_time, time_offset, sys_tz = tz_setup()
    print('Reading logs...')
    breakin_attempt, banned_ip = read_logs(LOG_DIR)
    unique_ips = set()
    for i in breakin_attempt.values():
        unique_ips.add(i[0])
    ip_and_location = {}
    print('Checking IP locations...')
    for i in unique_ips:
        ##ip_and_location[i] = check_ip_location(i)
        # be a good citizen and only hit the site every two seconds
        time.sleep(2)

    insert_into_db(ip_and_location, breakin_attempt, banned_ip)

    print('Building output...')
    #output_parsed_template = template.render(displayed_time=displayed_time,
    #                                         time_offset=time_offset,
    #                                         last_month=last_month,
    #                                         breakin_attempts=breakin_attempt,
    #                                         bans=banned_ip,
    #                                         ips=ip_and_location)

    #with codecs.open(os.path.join(DIR, 'index.html'), encoding='utf-8', mode='wb') as f:
    #    f.write(output_parsed_template)

    print('Finished!')

if __name__ == '__main__':

    run()
