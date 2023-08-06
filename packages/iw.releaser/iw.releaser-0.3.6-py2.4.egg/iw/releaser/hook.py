# -*- coding: utf-8 -*-
import os
import sys
import smtplib
import pkg_resources
from email.MIMEText import MIMEText
from zc.buildout.buildout import _recipe
from iw.releaser import config
from iw.releaser.packet import _run_setup

ENTRY_POINT = 'release_hook'

def apply_hooks(**kwargs):
    """
    >>> import pkg_resources
    >>> d = pkg_resources.get_distribution('iw.releaser')
    >>> pwd = os.getcwd()
    >>> os.chdir(d.location)

    >>> from iw.releaser.hook import apply_hooks
    >>> if not os.path.isdir(os.getenv('HOME')):
    ...     os.mkdir(os.getenv('HOME'))

    >>> pypirc = os.path.join(os.getenv('HOME'), 'pypirc')
    >>> open(pypirc, 'w+').write('''
    ... [mail_hook]
    ... hook = iw.releaser:mail
    ... from = support@ingeniweb.com
    ... emails =
    ...     gael.pasgrimaud@ingeniweb.com
    ... ''')

    >>> apply_hooks(package_name='iw.releaser', version='0.1')
    running egg_info
    ...
    Content-Type: text/plain; charset="us-ascii"
    MIME-Version: 1.0
    Content-Transfer-Encoding: 7bit
    From: support@ingeniweb.com
    To: ...@ingeniweb.com
    Subject: [Release] iw.releaser 0.1
    <BLANKLINE>
    trunk (...)
    ==================
    <BLANKLINE>
    ...

    >>> os.remove(pypirc)
    >>> os.chdir(pwd)

    """
    hooks = []
    for name in config.get_sections():
        section = config.get_section(name)
        if section.has_key('hook'):
            hooks.append(name)
    if not hooks:
        return

    name = kwargs.get('package_name',
                      os.path.split(os.getcwd())[-1].strip())

    if os.path.isfile('setup.py'):
        # make sure our setup is the first in sys.path
        sys.path.insert(0, os.getcwd())
        _run_setup('egg_info')
    else:
        raise pkg_resources.DistributionNotFound(
                 "Not able to find %s distribution in %s" % (name, os.getcwd()))

    try:
        dist = pkg_resources.get_distribution(name)
    except pkg_resources.DistributionNotFound:
        gen = pkg_resources.find_on_path(name, '.')
        try:
            dist = gen.next()
        except StopIteration:
            raise pkg_resources.DistributionNotFound(
                 "Not able to find %s distribution in %s" % (name, os.getcwd()))

    for name in hooks:
        section = config.get_section(name)
        package, entry = _recipe(dict(recipe=config.get_option(name, 'hook')))
        hook_meth = pkg_resources.load_entry_point(
                package, ENTRY_POINT, entry)
        local_config = kwargs.copy()
        local_config.update(section)
        hook_meth(dist, config.get_config(), **local_config)

def mail_hook(dist, global_config, **local_config):
    host = local_config.get('host', 'localhost')
    port = local_config.get('port', '25')
    server = smtplib.SMTP(host, int(port))

    subject = local_config.get('subject',
                               '[Release] %(name)s %(version)s')
    subject = subject.strip() % dict(name=dist.project_name,
                                     version=local_config.get('version',''))

    mfrom = local_config['from'].strip()
    emails = local_config['emails'].split()
    emails = [e.strip() for e in emails]

    if os.path.isfile('CHANGES'):
        CHANGES = 'CHANGES'
    elif os.path.isfile('CHANGES.txt'):
        CHANGES = 'CHANGES.txt'
    else:
        return
    contents = open(CHANGES).read()

    for mto in emails:
        email = MIMEText(contents, 'plain')
        email['From'] = mfrom
        email['To'] = mto
        email['Subject'] = subject
        server.sendmail(mfrom, mto, email.as_string())


