How to fire the indexer:

  - python snap/search/indexer.py \
    -i /var/entransit/snap \
    -d /var/entransit/xapdb \
    -t /var/entransit/queue &

How to reindex:

  - find /var/entransit/snap/ \
    -printf 'add\n%p\n' > /var/entransit/queue/reindex

  - Fire indexer again if not running


Xapian
======

There are binary debian packages for Xapian 0.9.2 now.
