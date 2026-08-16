import json, csv, os, shutil, zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from datetime import datetime

ROOT=os.path.dirname(os.path.abspath(__file__))
DB=os.path.join(ROOT,'db','database.json')
BACK=os.path.join(ROOT,'backups')

def now(): return datetime.now().isoformat(timespec='seconds')

def seed():
    if os.path.exists(DB): return
    data={
      'settings': {'store_name':'ArpanCart','currency':'₹','cod_enabled':True},
      'categories':[{'id':'cat1','name':'Puja Samagri','active':True},{'id':'cat2','name':'Grocery','active':True},{'id':'cat3','name':'Daily Essentials','active':True}],
      'products':[
        {'id':'p1','name':'Puja Samagri Starter Kit','category_id':'cat1','price':499,'stock':25,'active':True,'description':'Complete daily puja essentials.'},
        {'id':'p2','name':'Premium Puja Thali Set','category_id':'cat1','price':899,'stock':12,'active':True,'description':'Elegant puja thali set for home worship.'},
        {'id':'p3','name':'Monthly Essentials Pack','category_id':'cat3','price':1511,'stock':30,'active':True,'description':'Curated monthly household essentials.'}
      ],
      'services':[], 'customers':[], 'orders':[], 'coupons':[], 'reviews':[], 'logs':[]
    }
    save(data)

def load():
    seed()
    with open(DB,'r',encoding='utf8') as f:return json.load(f)

def save(d):
    os.makedirs(os.path.dirname(DB),exist_ok=True)
    tmp=DB+'.tmp'
    with open(tmp,'w',encoding='utf8') as f: json.dump(d,f,ensure_ascii=False,indent=2)
    os.replace(tmp,DB)

def backup():
    os.makedirs(BACK,exist_ok=True)
    fn=f"arpancart-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    path=os.path.join(BACK,fn); shutil.copy2(DB,path); return fn

class H(BaseHTTPRequestHandler):
    def send_json(self,obj,status=200):
        b=json.dumps(obj,ensure_ascii=False).encode(); self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b)
    def body(self):
        n=int(self.headers.get('Content-Length',0)); return json.loads(self.rfile.read(n) or '{}')
    def do_GET(self):
        p=urlparse(self.path).path
        if p=='/api/data': self.send_json(load()); return
        if p=='/api/backup':
            fn=backup(); self.send_json({'ok':True,'file':fn}); return
        if p.startswith('/backups/'):
            fn=os.path.basename(p); path=os.path.join(BACK,fn)
            if os.path.exists(path):
                self.send_response(200); self.send_header('Content-Type','application/json'); self.send_header('Content-Disposition',f'attachment; filename="{fn}"'); self.end_headers(); self.wfile.write(open(path,'rb').read()); return
        if p=='/': p='/index.html'
        path=os.path.join(ROOT,'public',p.lstrip('/'))
        if os.path.isfile(path):
            typ='text/html' if path.endswith('.html') else 'text/css' if path.endswith('.css') else 'application/javascript'
            b=open(path,'rb').read(); self.send_response(200); self.send_header('Content-Type',typ+'; charset=utf-8'); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b); return
        self.send_error(404)
    def do_POST(self):
        p=urlparse(self.path).path; d=load(); x=self.body()
        if p=='/api/products':
            x['id']='p'+datetime.now().strftime('%Y%m%d%H%M%S%f'); x['price']=float(x.get('price',0)); x['stock']=int(x.get('stock',0)); x['active']=True; d['products'].append(x)
        elif p=='/api/services/import':
            # expects CSV text in {csv:"..."}; columns: name,category,price,active
            rows=list(csv.DictReader(x.get('csv','').splitlines())); added=0
            for r in rows:
                if not r.get('name'): continue
                d['services'].append({'id':'s'+datetime.now().strftime('%Y%m%d%H%M%S%f')+str(added),'name':r['name'],'category':r.get('category','General'),'price':float(r.get('price') or 0),'active':str(r.get('active','true')).lower() not in ('false','0','no')}); added+=1
            x={'added':added}
        elif p=='/api/services':
            x['id']='s'+datetime.now().strftime('%Y%m%d%H%M%S%f'); x['price']=float(x.get('price',0)); x['active']=True; d['services'].append(x)
        elif p=='/api/categories':
            x['id']='cat'+datetime.now().strftime('%Y%m%d%H%M%S%f'); x['active']=True; d['categories'].append(x)
        elif p=='/api/orders':
            x['id']='o'+datetime.now().strftime('%Y%m%d%H%M%S%f'); x['created_at']=now(); x['status']='Pending'; d['orders'].append(x)
        elif p=='/api/backup':
            save(d); fn=backup(); self.send_json({'ok':True,'file':fn}); return
        else: self.send_json({'error':'Unknown endpoint'},404); return
        d['logs'].append({'time':now(),'action':p}); save(d); self.send_json({'ok':True,'data':d,'result':x})
    def do_PUT(self):
        p=urlparse(self.path).path; d=load(); x=self.body();
        collection=x.get('collection'); item_id=x.get('id'); item=x.get('item')
        if collection not in d or not isinstance(d[collection],list): self.send_json({'error':'Invalid collection'},400); return
        for i,v in enumerate(d[collection]):
            if v.get('id')==item_id: d[collection][i]={**v,**item}; save(d); self.send_json({'ok':True,'data':d}); return
        self.send_json({'error':'Not found'},404)
    def do_DELETE(self):
        p=urlparse(self.path).path; d=load(); x=self.body(); c=x.get('collection'); iid=x.get('id')
        if c in d: d[c]=[v for v in d[c] if v.get('id')!=iid]; save(d); self.send_json({'ok':True,'data':d}); return
        self.send_json({'error':'Invalid collection'},400)

if __name__=='__main__':
    seed(); port=int(os.environ.get('PORT','8080')); print(f'ArpanCart running at http://localhost:{port}'); ThreadingHTTPServer(('0.0.0.0',port),H).serve_forever()
