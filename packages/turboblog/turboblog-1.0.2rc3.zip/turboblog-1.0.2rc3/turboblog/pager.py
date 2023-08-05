def pager(sliceable, default_size=10, default_from=0):
    def decorator(fn, sliceable=sliceable,
                   default_from=default_from,
                   default_size=default_size):
        def wrapper(self, *args, **kw):
            from math import ceil
            def var(name):
                return 'tg_pager_' + sliceable + '_' + name
            pfrom = int(kw.pop(var('from'), default_from))
            psize = int(kw.pop(var('size'), default_size))
            d = fn(self, *args, **kw)
            try:
                ptotal = len(d[sliceable])
            except:
                ptotal = d[sliceable].count()
            if not psize:
                psize = ptotal - pfrom
                d[sliceable] = list(d[sliceable][pfrom:pfrom+psize])
            d[sliceable] = d[sliceable][pfrom:pfrom+psize]
            d[var('from')] = pfrom
            d[var('size')] = psize
            d[var('total')] = ptotal
            d[var('pages')] = int(ceil(float(ptotal)/psize))
            return d
        return wrapper
    return decorator

def add_params(k):
    if ('arc_year' in k) and ('arc_month' in k):
        return ';arc_year=%d;arc_month=%d'%(k['arc_year'],k['arc_month'])
    if 'tag_name' in k:
        return ';tagged=%d'%k['tag_name'].id
    return ""

def next_link(k):
    nl = ""
    if k['tg_pager_blog_posts_total'] > k['tg_pager_blog_posts_from']+k['tg_pager_blog_posts_size'] :
        nl = "<a href=\"%s?tg_pager_blog_posts_from=%d%s\">Next Entries &raquo;</a>"%(k['blog'].link(),k['tg_pager_blog_posts_from']+ k['tg_pager_blog_posts_size'], add_params(k))
    return nl
    
def previous_link(k):
    pl = ""
    if k['tg_pager_blog_posts_from'] > k['tg_pager_blog_posts_pages']:
        pl = "<a href=\"%s?tg_pager_blog_posts_from=%d%s\">&laquo; Previous Entries</a>"%(k['blog'].link(),k['tg_pager_blog_posts_from']- k['tg_pager_blog_posts_size'], add_params(k))
    return pl

