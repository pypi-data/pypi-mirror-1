import os
import sys
tpath = os.path.sep.join(os.path.abspath(__file__).split(os.path.sep)[:-1])
ppath = os.path.sep.join(os.path.abspath(__file__).split(os.path.sep)[:-2])
sys.path.append(ppath)

try:
    from templess import templess
except IOError:
    import templess
import test_templess_functional
import time

context = {
    'title': 'test template',
    'body': 'body contents',
}
def test_simple():
    template = templess.template(open('%s/templates/simple.html' % (tpath,)))
    template.render_to_string(context)

def test_test_context():
    # we reload here because the test context has another template 
    # instantiation inside it for the macro
    reload(test_templess_functional)
    t = open('%s/templates/testtemplate.html' % (tpath,))
    template = templess.template(t)
    template.render_to_string(test_templess_functional.context)
    t.close()

def time_renders(callable, num):
    starttime = time.time()
    startclock = time.clock()
    for i in xrange(num):
        callable()
    return (time.time() - starttime, time.clock() - startclock)

if __name__ == '__main__':
    num = raw_input('Number of times to try: ').strip()
    try:
        num = int(num)
    except TypeError:
        sys.exit(1)
    time_spent, clock_spent = time_renders(test_simple, num)
    print 'test with simple context'
    print 'time spent: %s msecs' % time_spent
    print 'time per hit:', (time_spent / num)
    print 'hits per second:', (num / time_spent)
    print 'cpu time spent: %s msecs' % clock_spent
    print 'cpu time per hit:', (clock_spent / num)
    print 'cpu hits per second:', (num / clock_spent)
    print
    time_spent, clock_spent = time_renders(test_test_context, num)
    print 'test with test_templess context'
    print 'time spent: %s msecs' % time_spent
    print 'time per hit:', (time_spent / num)
    print 'hits per second:', (num / time_spent)
    print 'cpu time spent: %s msecs' % clock_spent
    print 'cpu time per hit:', (clock_spent / num)
    print 'cpu hits per second:', (num / clock_spent)
