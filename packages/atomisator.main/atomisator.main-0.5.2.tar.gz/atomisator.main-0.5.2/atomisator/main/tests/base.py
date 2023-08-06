import os

test_dir = os.path.dirname(__file__)
package_dir = os.path.split(test_dir)[0]
test_conf = os.path.join(test_dir, 'atomisator.cfg')

def set_conf():
    template = open(os.path.join(test_dir, 'atomisator.cfg_tmpl')).read()
    cfg = template % {'test_dir': test_dir}
    f = open(test_conf, 'w')
    f.write(cfg)
    f.close()

def tear_conf():
    if os.path.exists(test_conf):
        os.remove(test_conf)
    xml = os.path.join(test_dir, 'atomisator.xml')
    if os.path.exists(xml):
        os.remove(xml)


