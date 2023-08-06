# -*- coding: utf-8 -*-
import os
import sys
import smtplib
import pkg_resources
from email.MIMEText import MIMEText
from zc.buildout.buildout import _recipe
from collective.releaser import config
from collective.releaser.packet import _run_setup

ENTRY_POINT = 'release_hook'

def apply_hooks(**kwargs):
    """
    >>> import pkg_resources
    >>> d = pkg_resources.get_distribution('collective.releaser')
    >>> pwd = os.getcwd()
    >>> os.chdir(d.location)

    >>> from collective.releaser.hook import apply_hooks
    >>> if not os.path.isdir(os.getenv('HOME')):
    ...     os.mkdir(os.getenv('HOME'))

    >>> pypirc = os.path.join(os.getenv('HOME'), 'pypirc')
    >>> open(pypirc, 'w+').write('''
    ... [mail_hook]
    ... hook = collective.releaser:mail
    ... from = support@ingeniweb.com
    ... emails =
    ...     gael.pasgrimaud@ingeniweb.com
    ... ''')

    >>> apply_hooks(package_name='collective.releaser', version='0.1')
    running egg_info
    ...
    Content-Type: text/plain; charset="us-ascii"
    MIME-Version: 1.0
    Content-Transfer-Encoding: 7bit
    From: support@ingeniweb.com
    To: ...@ingeniweb.com
    Subject: [Release] collective.releaser 0.1
    <BLANKLINE>
    collective.releaser 0.1 has been released !
    <BLANKLINE>
    Work done in this version:
    ...
    <BLANKLINE>

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
    
    version=local_config.get('version', 'trunk')
    kicker = '%(name)s %(version)s has been released !'
    kicker = kicker % dict(name=dist.project_name, 
                           version=version)

    contents = [kicker, '', 'Work done in this version:']
    
    # extract the right section in CHANGES
    changes = open(CHANGES).read().split('\n')
    start = 0
    end = -1
    for no, line in enumerate(changes):
        if line.startswith(version) and start == 0:
            start = no + 2
        if start != 0 and no > start + 1 and line.startswith('='):
            end = no - 1
            break
    if start < len(changes):
        contents.extend(changes[start:end])

    for mto in emails:
        email = MIMEText('\n'.join(contents), 'plain')
        email['From'] = mfrom
        email['To'] = mto
        email['Subject'] = subject
        server.sendmail(mfrom, mto, email.as_string())


