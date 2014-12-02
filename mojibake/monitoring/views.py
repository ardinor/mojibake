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

    return render_template('monitoring/index.html', last_month=last_month,
        breakin_attempts=breakin_attempts,
        bans=bans)


@monitor.route('/common')
def common_ips():
    # Need to tune how many attempts are needed for it to be common
    # Also set the date to be last month as well? Happy showing data from all time?
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
        # If we've seen this /24 more than twice
        if ip_cntr_24[ip_24] >= 2:
            # Begin by making a range of the IPs we've seen in the /24
            ip_range = []
            for ip in ips:
                reverse_ip = ip[::-1]
                split_ip_24 = reverse_ip[:reverse_ip.find('.')]
                split_ip_24 = int(split_ip_24[::-1])
                ip_range += [split_ip_24]
            # Find the difference between the highest and lowest IPs seen
            ip_range_diff = max(ip_range) - min(ip_range)
            # Find the nearest power of 2 (credit to http://mccormick.cx/news/entries/nearest-power-of-two)
            subnet_range = pow(2, int(log(ip_range_diff, 2) + 0.5))
            # Calculate the net mask, it'll be 256 - the subnet range (e.g. 256 - 64 = 192)
            net_mask = '255.255.255.{}'.format(256 - subnet_range)
            # Calculate the CIDR notation
            cidr = 8 - int(log(ip_range_diff, 2) + 0.5)
            # Calculate the number of hosts
            no_hosts = pow(2, 8 - cidr) - 2 # subnet_range - 2  # this won't work for /16, need to add 8 to it?
            cidr = '/{}'.format(24 + cidr)

            # Next work out the subnet id
            range_step = 0
            while range_step < 256:
                next_step = range_step + subnet_range
                if range_step < min(ip_range) < next_step: # and range_step < min(ip_range) < next_step:
                    break
                range_step = next_step
            subnet_id = '{}.{}'.format(ip_24, range_step)
            subnets_to_block[subnet_id] = {'net_mask': net_mask,
                                               'cidr': cidr,
                                               'no_hosts': no_hosts}


    return render_template('monitoring/common.html', common_ips=common_ips,
        subnets_16=ip_cntr_16, subnets_24=ip_cntr_24,
        subnets_to_block=subnets_to_block)
