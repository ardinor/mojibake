from flask import Blueprint, render_template
from sqlalchemy import func
from collections import Counter
import datetime

from mojibake.models import BreakinAttempts, BannedIPs, IPAddr
from mojibake.settings import DEBUG

monitor = Blueprint('monitor', __name__,
    template_folder='templates')

@monitor.route('/')
def bans_list():

    # Since we set up port knocking there are no longer any failed
    # attempts to access the server, use this date to show some historical
    # data instead
    #last_month = datetime.datetime.now().replace(day=1) - datetime.timedelta(days=1)
    last_month = datetime.datetime(2014, 10, 31)


    if DEBUG:
        breakin_attempts = BreakinAttempts.query.filter("strftime('%Y', date) = :year").params(year=last_month.strftime('%Y')). \
            filter("strftime('%m', date) = :month").params(month=last_month.strftime('%m')).order_by('-date').all()
        bans = BannedIPs.query.filter("strftime('%Y', date) = :year").params(year=last_month.strftime('%Y')). \
            filter("strftime('%m', date) = :month").params(month=last_month.strftime('%m')).order_by('-date').all()
    else:
        year = last_month.strftime('%Y')
        month = last_month.strftime('%m')
        breakin_attempts = BreakinAttempts.query.filter(func.YEAR(BreakinAttempts.date) == year). \
            filter(func.MONTH(BreakinAttempts.date) == month).order_by('-date').all()
        bans = BannedIPs.query.filter(func.YEAR(BannedIPs.date) == year). \
            filter(func.MONTH(BannedIPs.date) == month).order_by('-date').all()

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

    # Start with the /16
    list_ips_16 = []
    list_ips_24 = []
    for ip in common_ips:
        #count = ip.breakins.count()

        # Start with the /16
        split_ip = ip.ip_addr.split('.')
        list_ips_16 += [split_ip[0] + '.' + split_ip[1]]  # count *

        # Then the /24
        # [::-1] flips the string around (http://stackoverflow.com/a/931095)
        reverse_ip = ip.ip_addr[::-1]
        split_ip_24 = reverse_ip[reverse_ip.find('.')+1:]
        split_ip_24 = split_ip_24[::-1]
        list_ips_24 += [split_ip_24]  # count *

    ip_cntr_16 = Counter(list_ips_16)
    ip_cntr_24 = Counter(list_ips_24)

    #subnets = ip_cntr_16 + ip_cntr_24

    # for [ip_start, count] in ip_cntr.most_common():
    #     # How many times for this to be common as well?
    #     if count > 3:
    #         pass


    return render_template('monitoring/ips.html', common_ips=common_ips,
        subnets_16=ip_cntr_16, subnets_24=ip_cntr_24)
