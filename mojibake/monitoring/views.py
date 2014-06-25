from flask import Blueprint, render_template
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
    full_ips = IPAddr.query.filter_by(breakins.count > 3).all()

    common_ips = {}
    subnets = {}

    return render_template('monitoring/ips.html', common_ips=common_ips,
        subnets=subnets)
