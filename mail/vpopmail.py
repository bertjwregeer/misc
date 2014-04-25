from __future__ import print_function

import sys
import os
from os import path

vmail_path = '/usr/local/vmail/domains/{0}/{1}'

insert_domain = "INSERT INTO domain (domain, transport, active, created) VALUES (\"{0}\", \"virtual\", 1, NOW());"
insert_alias  = "INSERT INTO alias (address, goto, active, created, Domain_id) VALUES (\"{0}@{2}\", \"{1}\", 1, NOW(), (SELECT id FROM domain WHERE domain = \"{2}\"));"
insert_mailbox = "INSERT INTO mailbox (username, password, name, local_part, active, access_restriction, homedir, maildir, uid, gid, created, delete_pending, alt_email, Domain_id) VALUES (\"{0}@{3}\", '{1}', '{2}', '{0}', 1, 'ALL', '/usr/local/vmail/domains/{3}/{0}', 'maildir:~/Maildir/', 127, 127, NOW(), 0, '', (SELECT id FROM domain WHERE domain = '{3}'));"

def main():
    if len(sys.argv) != 3:
        print("Not enough arguments: {} <domain directory> <output_dir>".format(sys.argv[0]), file=sys.stderr)
        exit(-1)

    dpath = path.abspath(sys.argv[1])
    opath = path.abspath(sys.argv[2])

    domain = dpath.split('/')[-1]

    opath_sql = path.join(opath, '{}.{}'.format(domain, 'sql'))
    opath_sh  = path.join(opath, '{}.{}'.format(domain, 'sh'))

    sql = ['BEGIN;']
    sh = []

    sh.append('rm -rf /usr/local/vmail/domains/{}'.format(domain))
    sh.append('mkdir /usr/local/vmail/domains/{}'.format(domain))

    print("Working on: {}".format(domain), file=sys.stderr)

    allfiles = os.listdir(dpath)
    dotfiles = [f for f in allfiles if '.qmail-' in f]
    maildirs = [d for d in allfiles if os.path.isdir(path.join(dpath, d))]

    passwd = path.join(dpath, 'vpasswd')

    # Parse the passwd file

    with open(passwd) as f:
        f_allusers = f.readlines()

    sql.append(insert_domain.format(domain))

    for user in f_allusers:
        (username, password, _, _, name, mpath, quota) = user.strip().split(':')

        if not path.isdir(mpath):
            print("Username missing maildir: {}".format(username), file=sys.stderr)

        sh.append('cp -PR {0} {1}'.format(mpath, vmail_path.format(domain, username)))
        sh.append('bash /root/bin/imapdir2maildir++.sh {}'.format(vmail_path.format(domain, username)))
        sh.append('perl /root/bin/binc2dovecot.pl {}'.format(vmail_path.format(domain, username)))
        sh.append('rmdir {}/IMAPdir'.format(vmail_path.format(domain, username)))
        sh.append('chown -R vmail:vmail {}'.format(vmail_path.format(domain, username)))

        sql.append(insert_mailbox.format(username, password, name, domain))

    for dotfile in dotfiles:
        (_, alias) = dotfile.split('-', 1)
        alias = alias.replace(':', '-')

        with open(path.join(dpath, dotfile)) as f:
            gotos = f.readlines()

        all_goto = []
        for goto in gotos:
            goto = goto.strip()

            if goto[0] == '&':
                all_goto.append(goto[1:])
                continue
            if goto[0] == '|':
                continue
            
            if '@' in goto:
                all_goto.append(goto)
                continue

            print("Alias has invalid goto: {} -> {}".format(alias, goto))

        if len(all_goto) != 0:
            sql.append(insert_alias.format(alias, ','.join(all_goto), domain))

    # Update the mailbox_count and alias_count in domain
    sql.append('UPDATE domain SET alias_count = (SELECT count(id) FROM alias WHERE alias.Domain_id = domain.id), mailbox_count = (SELECT count(id) FROM mailbox WHERE mailbox.Domain_id = domain.id);')
    sql.append('COMMIT;')

    with open(opath_sql, 'w') as f:
        for statement in sql:
            print(statement, file=f)

    with open(opath_sh, 'w') as f:
        for statement in sh:
            print(statement, file=f)

if __name__ == '__main__':
    main()
