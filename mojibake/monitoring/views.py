from flask import Blueprint, render_template
from sqlalchemy import func
from collections import Counter
import datetime

from mojibake.models import BreakinAttempts, BannedIPs, IPAddr

monitor = Blueprint('monitor', __name__,
    template_folder='templates')

@monitor.route('/')
def bans_list():

    #displayed_time = 'CET'
    #time_offset = '+1'

    #last_month = datetime.datetime.now().replace(day=1) - datetime.timedelta(days=1)
    last_month = datetime.datetime.now()  # for testing

    breakin_attempts = BreakinAttempts.query.filter("strftime('%Y', date) = :year").params(year=last_month.strftime('%Y')). \
        filter("strftime('%m', date) = :month").params(month=last_month.strftime('%m')).order_by('-date').all()
    bans = BannedIPs.query.filter("strftime('%Y', date) = :year").params(year=last_month.strftime('%Y')). \
        filter("strftime('%m', date) = :month").params(month=last_month.strftime('%m')).order_by('-date').all()

    #displayed_time=displayed_time,
    #    time_offset=time_offset,

    return render_template('monitoring/index.html', last_month=last_month,
        breakin_attempts=breakin_attempts,
        bans=bans)

@monitor.route('/ips')
def ip_list():
    # Need to tune how many attempts are needed for it to be common
    common_ips = IPAddr.query.join(BreakinAttempts).group_by(IPAddr.ip_addr). \
        having(func.count(IPAddr.breakins)>=3).all()

    ip_list = []
    for ip in common_ips:
        split_ip = ip.ip_addr.split('.')
        ip_list.append(split_ip[0] + '.' + split_ip[1])
    ip_cntr = Counter(ip_list)

    for [ip_start, count] in ip_cntr.most_common():
        # How many times for this to be common as well?
        if count > 5:


    subnets = {}

    return render_template('monitoring/ips.html', common_ips=common_ips,
        subnets=subnets)
