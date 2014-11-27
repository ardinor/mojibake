from flask import Blueprint, render_template
from sqlalchemy import func
from collections import Counter
import datetime
from math import log

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

    CIDR_24 = {0: '/24', 128: '/25', 192: '/26',
               224: '/27', 240: '/28', 248: '/29',
               252: '/30', 254: '/31', 255: '/32'}

    CIDR_16 = {0: '/24', 128: '/25', 192: '/26',
               224: '/27', 240: '/28', 248: '/29',
               252: '/30', 254: '/31', 255: '/32'}

    # Need to tune how many attempts are needed for it to be common
    common_ips = IPAddr.query.join(BreakinAttempts).group_by(IPAddr.ip_addr). \
        having(func.count(IPAddr.breakins)>=3).all()

    list_ips_16 = []
    list_ips_24 = []
    common_16s = {}
    common_24s = {}
    for ip in common_ips:
        # Start with the /16
        split_ip = ip.ip_addr.split('.')
        split_ip_16 = split_ip[0] + '.' + split_ip[1]
        list_ips_16 += [split_ip_16]
        if split_ip_16 in common_16s.keys():
            common_16s[split_ip_16] += [ip.ip_addr]
        else:
            common_16s[split_ip_16] = [ip.ip_addr]

        # Then the /24
        # [::-1] flips the string around (http://stackoverflow.com/a/931095)
        reverse_ip = ip.ip_addr[::-1]
        split_ip_24 = reverse_ip[reverse_ip.find('.')+1:]
        split_ip_24 = split_ip_24[::-1]  # flip it back
        list_ips_24 += [split_ip_24]
        if split_ip_24 in common_24s.keys():
            common_24s[split_ip_24] += [ip.ip_addr]
        else:
            common_24s[split_ip_24] = [ip.ip_addr]

    ip_cntr_16 = Counter(list_ips_16)
    ip_cntr_24 = Counter(list_ips_24)

    subnets_to_block = {}

    for ip_24, ips in common_24s.items():
        if ip_cntr_24[ip_24] >= 2:
            ip_range = []
            for ip in ips:
                reverse_ip = ip[::-1]
                split_ip_24 = int(reverse_ip[:reverse_ip.find('.')])
                ip_range += [split_ip_24]
            ip_range_diff = max(ip_range) - min(ip_range)
            # find the nearest power of 2 (credit to http://mccormick.cx/news/entries/nearest-power-of-two)
            subnet_range = pow(2, int(log(ip_range_diff, 2) + 0.5))
            no_hosts = subnet_range - 2
            net_mask = '255.255.255.{}'.format(256 - subnet_range)
            cidr = 8 - int(log(ip_range_diff, 2) + 0.5)
            cidr = '/{}'.format(24 + cidr)
            subnets_to_block[ip_24] = {'net_mask': net_mask,
                                               'cidr': cidr,
                                               'no_hosts': no_hosts}


    return render_template('monitoring/ips.html', common_ips=common_ips,
        subnets_16=ip_cntr_16, subnets_24=ip_cntr_24,
        subnets_to_block=subnets_to_block)
