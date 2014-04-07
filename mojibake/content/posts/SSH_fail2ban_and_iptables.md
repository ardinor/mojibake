title: SSH, fail2ban & iptables
date: 2013-11-06 22:49:30
tags: SSH, fail2ban, iptables
category: Security
lang: en

So I've had this server for a little over a month now, and early on I set SSH up with key login to ensure no-one else can log in. After chatting with a friend about all the brute force attempts one of his servers is on the receiving end of I decided to take a look at the failed login attempts on mine.

    :::bash
    cat /var/log/auth.log | grep 'sshd.*Invalid'

I was somewhat surprised to see the number of attempts on even a fairly new server. It doesn't take them long to find servers apparently!

    Nov  6 08:03:22 defestri sshd[31088]: Invalid user apolline from 115.114.14.195
    Nov  6 08:37:11 defestri sshd[31107]: Invalid user appolenia from 115.114.14.195
    Nov  6 09:11:00 defestri sshd[31121]: Invalid user april from 115.114.14.195
    Nov  6 09:45:21 defestri sshd[31140]: Invalid user ar from 115.114.14.195
    Nov  6 10:20:17 defestri sshd[31156]: Invalid user arabella from 115.114.14.195
    Nov  6 10:55:07 defestri sshd[31175]: Invalid user araceli from 115.114.14.195
    Nov  6 11:29:26 defestri sshd[31261]: Invalid user arao from 115.114.14.195
    Nov  6 12:03:37 defestri sshd[31282]: Invalid user arcadia from 115.114.14.195
    Nov  6 12:38:09 defestri sshd[31301]: Invalid user ardelle from 115.114.14.195
    Nov  6 13:12:18 defestri sshd[31317]: Invalid user ardis from 115.114.14.195
    Nov  6 13:46:16 defestri sshd[31334]: Invalid user aretha from 115.114.14.195
    Nov  6 14:19:53 defestri sshd[31350]: Invalid user aretina from 115.114.14.195
    Nov  6 14:53:42 defestri sshd[31369]: Invalid user ari from 115.114.14.195
    Nov  6 15:27:43 defestri sshd[31385]: Invalid user aria from 115.114.14.195
    Nov  6 16:01:42 defestri sshd[31402]: Invalid user ariadne from 115.114.14.195
    Nov  6 16:35:39 defestri sshd[31421]: Invalid user ariana from 115.114.14.195
    Nov  6 22:03:31 defestri sshd[31721]: Invalid user oracle from 74.63.200.36
    Nov  6 22:03:33 defestri sshd[31723]: Invalid user oracle from 74.63.200.36
    Nov  6 22:03:34 defestri sshd[31725]: Invalid user oracle from 74.63.200.36

I have of course set up fail2ban which on the default settings, bans them after six failed attempts for one hour. But it seems this lot are pretty persistent. First up, let's harden fail2ban a bit, reduce the number of failed attempts to three and increase the ban time to one day.

    sudo nano /etc/fail2ban/jail.local

Scroll down to the section with bantime and maxretry and set as:

    # ban time 24 hours
    bantime = 86400
    maxretry = 3

Scroll down to the ssh section as well and set it to three maximum retries:

    [ssh]
    enabled = true
    port = ssh
    filter = sshd
    logpath = /var/log/auth.log
    maxtry = 3

Then finally restart fail2ban.

    :::bash
    sudo service fail2ban restart

Now that that's taken care of, let's take it one further step. We can see there's one IP (115.114.14.195, an Indian IP) that seems to have taken a likening to trying and brute forcing it's way in. Let's just ban him at the kernal firewall instead.

Let's first open up the existing test rules for iptables (if you have any):

    sudo nano /etc/iptables.test.rules

And let's make a new section for banned IPs:

    ## Banned IPs
    -A INPUT -s 115.114.14.195 -j DROP
    -A OUTPUT -d 115.114.14.195 -j DROP

Then double check how it looks:

    sudo iptables -L

If that looks okay we'll save it to the master iptables file:

    sudo sh -c "iptables-save > /etc/iptables.up.rules"

That ought to keep him out. Funnily enough my friend had log in attempts from the same IP. Whoever it is they certainly get around.

Obviously moving SSH to a different port would stop some of these casual attempts at finding open SSH services but let's leave SSH where it is for the time being to ensure these changes workout as intended.
