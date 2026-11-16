s=open('site/page.html').read()
s=s.replace('__DATA__',open('data/dataset.json').read()).replace('__EXAMPLE__',open('data/example.json').read())
open('site/index.html','w').write(s); print('site/index.html', len(s)//1024, 'KB')
