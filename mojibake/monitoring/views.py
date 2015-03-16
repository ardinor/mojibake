from flask import Blueprint, render_template
from sqlalchemy import func
from collections import Counter
import datetime

from mojibake.models import BreakinAttempts, BannedIPs, IPAddr, SubnetDetails
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

    if DEBUG:
        subnet_details = SubnetDetails.query.filter("strftime('%Y', date_added) = :year"). \
                                                    params(year=last_month.strftime('%Y')). \
                                                    filter("strftime('%m', date_added) = :month"). \
                                                    params(month=last_month.strftime('%m')). \
                                                    order_by('-date').all()
    else:
        subnet_details = SubnetDetails.query.filter(func.YEAR(SubnetDetails.date_added) == year). \
                                                    filter(func.MONTH(SubnetDetails.date_added) == month). \
                                                    order_by('-date').all()

    return render_template('monitoring/common.html', common_ips=common_ips,
        subnet_details=subnet_details)
