#from mod_python import apache, util
import os, shutil

def log(text):
    f = open('/tmp/tramline.log', 'a')
    f.write(text)
    f.write('\n')
    f.close()
    
def inputfilter(filter):
    if filter.req.method != 'POST':
        filter.disable()
        return
    #del filter.req.headers_in['Content-Length']
    f = open('/tmp/filtertest.txt', 'ab')
    log('first read')
    s = filter.read()
    while s:
        #s = s[:200] + s[205:]
        log('writing (%s)' % len(s))
        # if 'head' not in s:
        f.write(s)
        f.flush()
        filter.write(s)
        log('loop read')
        s = filter.read()
    if s is None:
        log('closing')
        #filter.flush()
        filter.close()
        raise "error"
        #filter.disable()
    f.close()

def requesthandler(req):
    
    fs = util.FieldStorage(req)
    for key in fs.keys():
        value = fs[key]
        if isinstance(value, util.Field):
            f = open(os.path.join('/tmp/dumpingground', value.filename), 'wb')
            shutil.copyfileobj(value.file, f)
            f.close()
            
    return apache.DECLINED
