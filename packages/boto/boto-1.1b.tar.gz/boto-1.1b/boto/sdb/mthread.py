import boto
import threading
from datetime import datetime

class SimpleThread(threading.Thread):
    
    def __init__(self, name, domain_name, item_names):
        threading.Thread.__init__(self, name=name)
        print 'SimpleThread: %s %s' % (name, item_names)
        self.domain_name = domain_name
        self.conn = boto.connect_sdb()
        self.item_names = item_names
        self.items = []
        
    def run(self):
        for item_name in self.item_names:
            item = self.conn.get_attributes(self.domain_name, item_name)
            self.items.append(item)

def get_attrs(domain_name, query, num_threads):
    start = datetime.now()
    item_names = []
    conn = boto.connect_sdb()
    domain = conn.get_domain(domain_name)
    rs = domain.query(query)
    for item in rs:
        item_names.append(item.name)
    items = []
    threads = []
    n = len(item_names) / num_threads
    for i in range(0, num_threads+1):
        thread = SimpleThread('Thread-%d' % i, domain_name, item_names[n*i:n*(i+1)])
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
        items = items + thread.items
    end = datetime.now()
    print end-start
    return items

def get_attrs_no_threads(domain_name, query):
    start = datetime.now()
    item_names = []
    conn = boto.connect_sdb()
    domain = conn.get_domain(domain_name)
    rs = domain.query(query)
    items = []
    for item in rs:
        item_names.append(item.name)
    for item_name in item_names:
        item = conn.get_attributes(domain_name, item_name)
        items.append(item)
    end = datetime.now()
    print end-start
    return items


