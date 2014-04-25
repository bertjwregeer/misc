#!/usr/bin/env python

"""

Drupal to Blogofile convertor
-----------------------------

Usage:

    1. Create virtualenv
    2. $venv/bin/pip install sqlalchemy mysql-python pyyaml
    3. $venv/bin/python drupaltoblogofile.py "mysql://username:password@localhost/drupal_db" output_dir

The first argument is a SQLAlchemy DB URL, the second argument is where to place the output.

"""

import sys
import os
import os.path
import time
import datetime

import yaml

from sqlalchemy import create_engine
from sqlalchemy.sql import text, select, and_, join

def main():
    if len(sys.argv) != 3:
        print("Not enough arguments...")
        exit(0)

    write_to = os.path.abspath(sys.argv[2])

    if os.path.exists(write_to) and not os.path.isdir(write_to):
        print("Target already exists, and is not directory")
        exit(-1)

    if os.path.isdir(write_to):
        print("Target already exists, will overwrite files...")
        print("Sleeping for 5 seconds")
        time.sleep(5)
    else:
        os.mkdir(write_to)

    engine = create_engine(sys.argv[1], echo=True)
    conn = engine.connect()

    nodes = select(
        ["node.nid, node.vid, node.title, node_revisions.body, node.created"]
        ).where(
            and_(
                "node.status = 1",
                "node.vid = node_revisions.vid"
                )
        ).select_from("node, node_revisions")

    tags = select(
            ["term_data.name"]
            ).where(
                    and_(
                        "term_node.vid = :vid",
                        "term_node.nid = :nid"
                    )
            ).select_from(
                    join("term_node", "term_data", text("term_node.tid = term_data.tid")))

    url_alias = select(
            ["src, dst"]
            ).where(
                    "url_alias.src = CONCAT('node/', :nid)"
            ).select_from("url_alias")

    for rnode in conn.execute(nodes):
        (nid, vid, title, body, created) = rnode

        created_date = datetime.datetime.fromtimestamp(created)

        node = {
                'nid': nid,
                'vid': vid,
                'title': title,
                'body': body,
                'created': created,
                'created_year': created_date.strftime('%Y'),
                'created_month': created_date.strftime('%m'),
                'created_day': created_date.strftime('%d'),
                'created_formatted': created_date.strftime('%Y-%m-%d %H:%M:%S'),
                'tags': [],
                'alias': '',
                }

        for rtag in conn.execute(tags, vid=vid, nid=nid):
            (tag,) = rtag

            node['tags'].append(tag)

        node['tags'] = ', '.join(node['tags'])
        

        alias = conn.execute(url_alias, nid=nid).first()

        if alias is not None:
            node['alias'] = ', '.join(alias)

        year_dir = os.path.join(write_to, node['created_year'])
        try:
            os.mkdir(year_dir)
        except:
            pass

        with open(os.path.join(year_dir, '{}-{}-{} - {}.md'.format(node['created_year'], node['created_month'], node['created_day'], node['title']).replace('/', ':')), 'w') as f:
            f.write('---\n')
            f.write(
                yaml.dump(
                {
                    'title': node['title'],
                    'categories': node['tags'],
                    'date': node['created_formatted'],
                    'aliases': node['alias'],
                },
                default_flow_style=False
                )
            )
            f.write('---\n')
            f.write(node['body'])
            f.write('\n')

if __name__ == '__main__':
    main()

