from flask import Flask, jsonify, request, send_from_directory, session, redirect, abort
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image
import sqlite3, os, random, shutil, zipfile, time, json
from datetime import datetime

BASE=os.path.dirname(os.path.abspath(__file__))
DB=os.path.join(BASE,'data','art.db')
UPLOAD=os.path.join(BASE,'uploads')
FRONT=os.path.join(BASE,'frontend')
DETAIL=os.path.join(FRONT,'img','details')
BACKUP=os.path.join(BASE,'backup')
os.makedirs(os.path.dirname(DB),exist_ok=True)
os.makedirs(UPLOAD,exist_ok=True)
os.makedirs(os.path.join(UPLOAD,'works'),exist_ok=True)
os.makedirs(os.path.join(UPLOAD,'site'),exist_ok=True)
os.makedirs(BACKUP,exist_ok=True)
app=Flask(__name__, static_folder=FRONT, static_url_path='')
app.secret_key='xiangpan-local-secret-change-me'
app.config['MAX_CONTENT_LENGTH']=200*1024*1024

CATS=[('书法',['篆书','楷书','行书','隶书','草书']),('绘画',['素描','油画']),('诗文',[]),('篆刻',[]),('信札',[])]
PERIODS=['1990-1999','2000-2009','2010-2019','2020-2029','2030-2039']
NAMES=['石鼓文临习','篆书作品','临吴昌硕书','金文小品','行书册页','篆书四条屏','墨竹小品','山水清音','自作诗稿','闲居札记','篆刻印屏','信札一通']

def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def init_db():
    c=db(); cur=c.cursor()
    cur.executescript('''
    CREATE TABLE IF NOT EXISTS site_config(id INTEGER PRIMARY KEY CHECK(id=1),site_name TEXT,logo TEXT,avatar TEXT,artist_name TEXT,artist_bio TEXT,social_links TEXT);
    CREATE TABLE IF NOT EXISTS categories(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT UNIQUE);
    CREATE TABLE IF NOT EXISTS subcategories(id INTEGER PRIMARY KEY AUTOINCREMENT,category_id INTEGER,name TEXT,UNIQUE(category_id,name));
    CREATE TABLE IF NOT EXISTS periods(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT UNIQUE);
    CREATE TABLE IF NOT EXISTS works(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,category_id INTEGER,subcategory_id INTEGER,work_no TEXT UNIQUE,creation_time TEXT,size TEXT,description TEXT,main_image TEXT,created_at TEXT);
    CREATE TABLE IF NOT EXISTS work_images(id INTEGER PRIMARY KEY AUTOINCREMENT,work_id INTEGER,filename TEXT,is_main INTEGER DEFAULT 0);
    CREATE TABLE IF NOT EXISTS admins(id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL,role TEXT NOT NULL DEFAULT 'admin',display_name TEXT,created_at TEXT,updated_at TEXT);
    CREATE TABLE IF NOT EXISTS operation_logs(id INTEGER PRIMARY KEY AUTOINCREMENT,admin_id INTEGER,admin_name TEXT,action TEXT,detail TEXT,created_at TEXT);
    ''')
    if not cur.execute('SELECT 1 FROM site_config WHERE id=1').fetchone():
        cur.execute('INSERT INTO site_config VALUES(1,?,?,?,?,?,?)',('向攀书法艺术','','/img/avatar.webp','向攀','字际宇，别署广邑向攀，斋号涤堂。中国书法家协会会员，重庆书协篆书委员会委员。好习吴昌硕篆书、行书。','[]'))
    for name,subs in CATS:
        cur.execute('INSERT OR IGNORE INTO categories(name) VALUES(?)',(name,))
        cid=cur.execute('SELECT id FROM categories WHERE name=?',(name,)).fetchone()[0]
        for s in subs: cur.execute('INSERT OR IGNORE INTO subcategories(category_id,name) VALUES(?,?)',(cid,s))
    for p in PERIODS: cur.execute('INSERT OR IGNORE INTO periods(name) VALUES(?)',(p,))
    count=cur.execute('SELECT COUNT(*) FROM works').fetchone()[0]
    imgs=sorted([x for x in os.listdir(DETAIL) if x.lower().endswith(('.webp','.jpg','.jpeg','.png'))], key=lambda x:x)
    if count==0 and imgs:
        catrows=cur.execute('SELECT id,name FROM categories').fetchall(); subrows=cur.execute('SELECT id,category_id,name FROM subcategories').fetchall()
        for i in range(1,501):
            cat=random.choice(catrows); subs=[s for s in subrows if s['category_id']==cat['id']]; sub=random.choice(subs) if subs else None
            period=random.choice(PERIODS); year=random.randint(int(period[:4]),int(period[-4:]))
            name=f'{random.choice(NAMES)} {i:03d}'
            fn=imgs[(i-1)%len(imgs)]
            cur.execute('INSERT INTO works(name,category_id,subcategory_id,work_no,creation_time,size,description,main_image,created_at) VALUES(?,?,?,?,?,?,?,?,?)',(name,cat['id'],sub['id'] if sub else None,f'XP-{i:04d}',str(year),'约 '+random.choice(['四尺','六尺','八尺','册页','斗方']),'书法艺术作品，作为网站演示数据。',fn,datetime.now().isoformat(timespec='seconds')))
            wid=cur.lastrowid
            # 2-4 images from the same supplied calligraphy set
            n=random.randint(2,min(4,len(imgs)))
            picks=[fn] + random.sample([x for x in imgs if x != fn], n-1)
            for j,f in enumerate(picks): cur.execute('INSERT INTO work_images(work_id,filename,is_main) VALUES(?,?,?)',(wid,f,1 if f==fn else 0))
    now=datetime.now().isoformat(timespec='seconds')
    # 超级管理员必须作为正式管理员记录写入 SQLite 数据库。
    # 首次初始化时创建：admin / admin123；之后只从数据库读取，不在登录时依赖硬编码账号。
    admin_row=cur.execute('SELECT id,role FROM admins WHERE username=?',('admin',)).fetchone()
    if not admin_row:
        cur.execute('INSERT INTO admins(username,password_hash,role,display_name,created_at,updated_at) VALUES(?,?,?,?,?,?)',
                    ('admin',generate_password_hash('admin123'),'super','超级管理员',now,now))
    elif admin_row['role']!='super':
        cur.execute("UPDATE admins SET role='super',display_name='超级管理员',updated_at=? WHERE username='admin'",(now,))
    c.commit(); c.close()

init_db()

def image_url(filename):
    if not filename: return ''
    if filename.startswith('/uploads/') or filename.startswith('/img/') or filename.startswith('http://') or filename.startswith('https://'):
        return filename
    # 兼容旧数据：如果同名文件已上传到后台目录，则优先使用上传文件；否则使用演示书法图片。
    if os.path.exists(os.path.join(UPLOAD, 'works', filename)):
        return '/uploads/works/' + filename
    if os.path.exists(os.path.join(UPLOAD, 'site', filename)):
        return '/uploads/site/' + filename
    return '/img/details/' + filename

def public_work(r):
    d=dict(r); d['main_image']=image_url(d.get('main_image')); return d

def auth(): return session.get('admin')

@app.route('/')
def home(): return send_from_directory(FRONT,'index.html')
@app.route('/<path:p>')
def static_page(p):
    if p.startswith('api/') or p.startswith('uploads/'): abort(404)
    f=os.path.join(FRONT,p)
    if os.path.isfile(f): return send_from_directory(FRONT,p)
    return send_from_directory(FRONT,'index.html')
@app.route('/uploads/<path:p>')
def uploads(p): return send_from_directory(UPLOAD,p)

@app.get('/api/site')
def api_site():
    c=db(); r=c.execute('SELECT * FROM site_config WHERE id=1').fetchone(); c.close(); return jsonify(dict(r))

@app.get('/api/home/random')
def api_random():
    c=db(); rows=c.execute('SELECT w.*,c.name category,sc.name subcategory FROM works w LEFT JOIN categories c ON c.id=w.category_id LEFT JOIN subcategories sc ON sc.id=w.subcategory_id ORDER BY RANDOM() LIMIT 12').fetchall(); c.close(); return jsonify([public_work(x) for x in rows])

@app.get('/api/categories')
def api_categories():
    c=db()
    try:
        rows=c.execute('SELECT id,name FROM categories ORDER BY id').fetchall()
        out=[]
        for r in rows:
            subs=c.execute('SELECT id,name FROM subcategories WHERE category_id=? ORDER BY id',(r['id'],)).fetchall()
            out.append({'id':r['id'],'name':r['name'],'subs':[x['name'] for x in subs],'subitems':[dict(x) for x in subs]})
        return jsonify(out)
    finally:
        c.close()
@app.get('/api/periods')
def api_periods():
    c=db(); rows=c.execute('SELECT * FROM periods ORDER BY id').fetchall(); c.close(); return jsonify([dict(x) for x in rows])

@app.get('/api/creation-time-range')
def api_creation_time_range():
    # 时间筛选范围直接读取作品数据中的最小、最大有效年份。
    c=db()
    rows=c.execute("SELECT creation_time FROM works WHERE creation_time IS NOT NULL AND TRIM(creation_time)<>''").fetchall()
    c.close()
    years=[]
    for r in rows:
        try:
            y=int(str(r['creation_time']).strip())
            if 1 <= y <= datetime.now().year:
                years.append(y)
        except (TypeError,ValueError):
            pass
    if years:
        return jsonify({'min_year':min(years),'max_year':max(years),'has_data':True})
    y=datetime.now().year
    return jsonify({'min_year':y,'max_year':y,'has_data':False})

@app.get('/api/works')
def api_works():
    page=max(1,int(request.args.get('page',1))); size=min(100,max(1,int(request.args.get('size',20)))); kw=request.args.get('keyword','').strip(); cat=request.args.get('category','').strip(); sub=request.args.get('subcategory','').strip(); period=request.args.get('period','').strip(); time_min=request.args.get('time_min','').strip(); time_max=request.args.get('time_max','').strip()
    wh=[]; args=[]
    if kw: wh.append('(w.name LIKE ? OR w.work_no LIKE ? OR w.description LIKE ?)'); args += [f'%{kw}%']*3
    if cat: wh.append('c.name=?'); args.append(cat)
    if sub: wh.append('sc.name=?'); args.append(sub)
    if period: wh.append('w.creation_time BETWEEN ? AND ?'); args += [period[:4],period[-4:]]
    if time_min:
        try: args.append(int(time_min)); wh.append("CAST(w.creation_time AS INTEGER) >= ?")
        except ValueError: pass
    if time_max:
        try: args.append(int(time_max)); wh.append("CAST(w.creation_time AS INTEGER) <= ?")
        except ValueError: pass
    where=' WHERE '+' AND '.join(wh) if wh else ''
    c=db(); total=c.execute(f'SELECT COUNT(*) FROM works w LEFT JOIN categories c ON c.id=w.category_id LEFT JOIN subcategories sc ON sc.id=w.subcategory_id {where}',args).fetchone()[0]
    rows=c.execute(f'SELECT w.*,c.name category,sc.name subcategory FROM works w LEFT JOIN categories c ON c.id=w.category_id LEFT JOIN subcategories sc ON sc.id=w.subcategory_id {where} ORDER BY w.id DESC LIMIT ? OFFSET ?',args+[size,(page-1)*size]).fetchall(); c.close()
    return jsonify({'items':[public_work(x) for x in rows],'total':total,'page':page,'size':size,'pages':(total+size-1)//size})

@app.get('/api/works/<int:wid>')
def api_work(wid):
    c=db(); r=c.execute('SELECT w.*,c.name category,sc.name subcategory FROM works w LEFT JOIN categories c ON c.id=w.category_id LEFT JOIN subcategories sc ON sc.id=w.subcategory_id WHERE w.id=?',(wid,)).fetchone(); imgs=c.execute('SELECT * FROM work_images WHERE work_id=? ORDER BY id',(wid,)).fetchall(); c.close()
    if not r: abort(404)
    d=public_work(r); d['images']=[{'id':x['id'],'url':image_url(x['filename']),'is_main':bool(x['is_main'])} for x in imgs]; return jsonify(d)

@app.post('/api/admin/login')
def login():
    data=request.get_json() or {}
    username=(data.get('username') or '').strip()
    password=data.get('password') or ''
    c=db(); row=c.execute('SELECT * FROM admins WHERE username=?',(username,)).fetchone(); c.close()
    if row and check_password_hash(row['password_hash'],password):
        session['admin_id']=row['id']; session['admin']=row['username']; session['admin_role']=row['role']; session['admin_name']=row['display_name'] or row['username']
        write_log('登录','管理员登录')
        return jsonify({'ok':True,'admin':session['admin_name'],'role':row['role']})
    return jsonify({'ok':False,'message':'账号或密码错误'}),401

@app.post('/api/admin/logout')
def logout():
    if auth(): write_log('退出登录','管理员退出登录')
    session.clear(); return jsonify({'ok':True})

def need():
    if not auth(): return jsonify({'message':'请先登录'}),401

def current_admin():
    return session.get('admin_name') or session.get('admin') or '管理员'

def is_super(): return session.get('admin_role')=='super'

def write_log(action, detail=''):
    try:
        c=db(); c.execute('INSERT INTO operation_logs(admin_id,admin_name,action,detail,created_at) VALUES(?,?,?,?,?)',(session.get('admin_id'),current_admin(),action,detail,datetime.now().isoformat(timespec='seconds'))); c.commit(); c.close()
    except Exception: pass

def save_upload(file, folder='works', exact_size=None):
    if not file or not file.filename: return None
    ext=os.path.splitext(file.filename)[1].lower()
    if ext not in ['.jpg','.jpeg','.png','.webp','.gif']: return None
    name=f'{int(time.time()*1000)}_{random.randint(1000,9999)}{ext}'
    path=os.path.join(UPLOAD,folder,name); os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        if exact_size:
            with Image.open(file.stream) as im:
                if im.size != exact_size: raise ValueError(f'图片必须为 {exact_size[0]}×{exact_size[1]} 像素')
                file.stream.seek(0)
        file.save(path)
    except (ValueError,OSError) as e:
        if os.path.exists(path): os.remove(path)
        raise ValueError(str(e))
    return f'/uploads/{folder}/{name}'

def delete_saved_files(urls):
    for u in urls:
        if u and u.startswith('/uploads/'):
            path=os.path.join(BASE,u.lstrip('/').replace('/',os.sep))
            if os.path.exists(path):
                try: os.remove(path)
                except OSError: pass

def validate_work_fields(f):
    name=(f.get('name') or '').strip()
    if not name: return None,'作品名称不能为空'
    category_id=f.get('category_id') or None; subcategory_id=f.get('subcategory_id') or None
    if not category_id: return None,'请选择作品分类'
    c=db()
    try:
        if subcategory_id and not c.execute('SELECT 1 FROM subcategories WHERE id=? AND category_id=?',(subcategory_id,category_id)).fetchone(): return None,'所选细分类与一级分类不匹配'
    finally: c.close()
    return {'name':name,'category_id':category_id,'subcategory_id':subcategory_id,'work_no':(f.get('work_no') or '').strip() or None,'creation_time':(f.get('creation_time') or '').strip(),'size':(f.get('size') or '').strip(),'description':f.get('description') or ''},None

@app.post('/api/admin/works')
def create_work():
    if (x:=need()): return x
    data,err=validate_work_fields(request.form)
    if err: return jsonify({'ok':False,'message':err}),400
    files=[x for x in request.files.getlist('images') if x and x.filename]
    if len(files)>20: return jsonify({'ok':False,'message':'单件作品最多上传20张图片'}),400
    c=db(); saved=[]
    try:
        cur=c.execute('INSERT INTO works(name,category_id,subcategory_id,work_no,creation_time,size,description,main_image,created_at) VALUES(?,?,?,?,?,?,?,?,?)',(data['name'],data['category_id'],data['subcategory_id'],data['work_no'],data['creation_time'],data['size'],data['description'],None,datetime.now().isoformat(timespec='seconds')))
        wid=cur.lastrowid
        for file in files:
            u=save_upload(file)
            if u: saved.append(u)
        for i,u in enumerate(saved): c.execute('INSERT INTO work_images(work_id,filename,is_main) VALUES(?,?,?)',(wid,u,1 if i==0 else 0))
        if saved: c.execute('UPDATE works SET main_image=? WHERE id=?',(saved[0],wid))
        c.commit(); write_log('新增作品',f'作品ID：{wid}，作品名称：{data["name"]}，上传图片：{len(saved)}张')
        return jsonify({'ok':True,'id':wid,'uploaded':len(saved)})
    except sqlite3.IntegrityError:
        c.rollback(); delete_saved_files(saved); return jsonify({'ok':False,'message':'作品编号已存在，请更换作品编号'}),400
    except Exception as e:
        c.rollback(); delete_saved_files(saved); return jsonify({'ok':False,'message':'作品保存失败：'+str(e)}),500
    finally: c.close()

@app.put('/api/admin/works/<int:wid>')
def update_work(wid):
    if (x:=need()): return x
    data,err=validate_work_fields(request.form if request.form else (request.get_json(silent=True) or {}))
    if err: return jsonify({'ok':False,'message':err}),400
    files=[x for x in request.files.getlist('images') if x and x.filename]
    c=db(); saved=[]
    try:
        row=c.execute('SELECT * FROM works WHERE id=?',(wid,)).fetchone()
        if not row: return jsonify({'ok':False,'message':'作品不存在'}),404
        existing=c.execute('SELECT COUNT(*) FROM work_images WHERE work_id=?',(wid,)).fetchone()[0]
        if existing+len(files)>20: return jsonify({'ok':False,'message':f'单件作品最多20张图片，当前已有{existing}张，最多还可上传{20-existing}张'}),400
        c.execute('UPDATE works SET name=?,category_id=?,subcategory_id=?,work_no=?,creation_time=?,size=?,description=? WHERE id=?',(data['name'],data['category_id'],data['subcategory_id'],data['work_no'],data['creation_time'],data['size'],data['description'],wid))
        for file in files:
            u=save_upload(file); saved.append(u) if u else None
        for u in saved: c.execute('INSERT INTO work_images(work_id,filename,is_main) VALUES(?,?,0)',(wid,u))
        if saved and not row['main_image']:
            c.execute('UPDATE work_images SET is_main=1 WHERE work_id=? AND filename=?',(wid,saved[0])); c.execute('UPDATE works SET main_image=? WHERE id=?',(saved[0],wid))
        c.commit(); write_log('编辑作品',f'作品ID：{wid}，作品名称：{data["name"]}，新增图片：{len(saved)}张')
        return jsonify({'ok':True,'id':wid,'uploaded':len(saved)})
    except sqlite3.IntegrityError:
        c.rollback(); delete_saved_files(saved); return jsonify({'ok':False,'message':'作品编号已存在，请更换作品编号'}),400
    except Exception as e:
        c.rollback(); delete_saved_files(saved); return jsonify({'ok':False,'message':'作品保存失败：'+str(e)}),500
    finally: c.close()

@app.post('/api/admin/works/<int:wid>/main-image')
def set_main_image(wid):
    if (x:=need()): return x
    image_id=(request.get_json() or {}).get('image_id'); c=db(); row=c.execute('SELECT filename FROM work_images WHERE id=? AND work_id=?',(image_id,wid)).fetchone()
    if not row: c.close(); return jsonify({'ok':False,'message':'图片不存在'}),404
    c.execute('UPDATE work_images SET is_main=0 WHERE work_id=?',(wid,)); c.execute('UPDATE work_images SET is_main=1 WHERE id=?',(image_id,)); c.execute('UPDATE works SET main_image=? WHERE id=?',(row['filename'],wid)); c.commit(); c.close(); write_log('设置主图',f'作品ID：{wid}，图片ID：{image_id}'); return jsonify({'ok':True})

@app.delete('/api/admin/works/<int:wid>/images/<int:image_id>')
def delete_work_image(wid,image_id):
    if (x:=need()): return x
    c=db(); row=c.execute('SELECT filename,is_main FROM work_images WHERE id=? AND work_id=?',(image_id,wid)).fetchone()
    if not row: c.close(); return jsonify({'ok':False,'message':'图片不存在'}),404
    count=c.execute('SELECT COUNT(*) FROM work_images WHERE work_id=?',(wid,)).fetchone()[0]
    if count<=1: c.close(); return jsonify({'ok':False,'message':'至少保留一张作品图片'}),400
    c.execute('DELETE FROM work_images WHERE id=?',(image_id,))
    if row['is_main']:
        nxt=c.execute('SELECT id,filename FROM work_images WHERE work_id=? ORDER BY id LIMIT 1',(wid,)).fetchone(); c.execute('UPDATE work_images SET is_main=1 WHERE id=?',(nxt['id'],)); c.execute('UPDATE works SET main_image=? WHERE id=?',(nxt['filename'],wid))
    c.commit(); c.close(); delete_saved_files([row['filename']]); write_log('删除作品图片',f'作品ID：{wid}，图片ID：{image_id}'); return jsonify({'ok':True})

@app.post('/api/admin/works/batch-delete')
def batch_delete_work():
    if (x:=need()): return x
    data=request.get_json(silent=True) or {}
    raw_ids=data.get('ids') or []
    try:
        ids=sorted({int(x) for x in raw_ids if str(x).strip()})
    except (TypeError,ValueError):
        return jsonify({'ok':False,'message':'作品编号无效'}),400
    if not ids: return jsonify({'ok':False,'message':'请先选择要删除的作品'}),400
    c=db(); rows=c.execute(f"SELECT id,name FROM works WHERE id IN ({','.join('?' for _ in ids)})",ids).fetchall()
    if not rows: c.close(); return jsonify({'ok':False,'message':'没有找到要删除的作品'}),404
    found=[r['id'] for r in rows]
    placeholders=','.join('?' for _ in found)
    imgs=c.execute(f'SELECT filename FROM work_images WHERE work_id IN ({placeholders})',found).fetchall()
    c.execute(f'DELETE FROM work_images WHERE work_id IN ({placeholders})',found)
    c.execute(f'DELETE FROM works WHERE id IN ({placeholders})',found)
    c.commit(); c.close()
    delete_saved_files([x['filename'] for x in imgs])
    write_log('批量删除作品',f'删除{len(found)}件作品：'+ '、'.join(str(r['name']) for r in rows[:20]))
    return jsonify({'ok':True,'deleted':len(found)})

@app.delete('/api/admin/works/<int:wid>')
def delete_work(wid):
    if (x:=need()): return x
    c=db(); imgs=c.execute('SELECT filename FROM work_images WHERE work_id=?',(wid,)).fetchall(); row=c.execute('SELECT name FROM works WHERE id=?',(wid,)).fetchone()
    c.execute('DELETE FROM work_images WHERE work_id=?',(wid,)); c.execute('DELETE FROM works WHERE id=?',(wid,)); c.commit(); c.close(); delete_saved_files([x['filename'] for x in imgs]); write_log('删除作品',f'作品ID：{wid}，作品名称：{row["name"] if row else ""}'); return jsonify({'ok':True})

@app.post('/api/admin/site')
def save_site():
    if (x:=need()): return x
    data=request.form; site_name=(data.get('site_name') or '').strip(); artist_name=(data.get('artist_name') or '').strip()
    if not site_name: return jsonify({'ok':False,'message':'站点名称不能为空'}),400
    if len(site_name)>20 or len(artist_name)>20: return jsonify({'ok':False,'message':'名称最多20个字'}),400
    c=db(); old=c.execute('SELECT logo,avatar FROM site_config WHERE id=1').fetchone(); uploaded=[]
    try:
        av=save_upload(request.files.get('avatar'),'site') if request.files.get('avatar') else (old['avatar'] if old else '')
        lg=save_upload(request.files.get('logo'),'site') if request.files.get('logo') else (old['logo'] if old else '')
        if av and av!=old['avatar']: uploaded.append(av)
        if lg and lg!=old['logo']: uploaded.append(lg)
        c.execute('UPDATE site_config SET site_name=?,logo=?,avatar=?,artist_name=?,artist_bio=?,social_links=? WHERE id=1',(site_name,lg or '',av or '',artist_name,data.get('artist_bio') or '',data.get('social_links','[]'))); c.commit(); write_log('站点配置',f'修改站点信息，新增图片：{len(uploaded)}张'); return jsonify({'ok':True,'logo':lg,'avatar':av})
    except Exception as e:
        c.rollback(); delete_saved_files(uploaded); return jsonify({'ok':False,'message':'站点信息保存失败：'+str(e)}),500
    finally: c.close()

@app.get('/api/admin/status')
def status():
    if (x:=need()): return x
    c=db(); counts={'works':c.execute('SELECT COUNT(*) FROM works').fetchone()[0],'categories':c.execute('SELECT COUNT(*) FROM categories').fetchone()[0],'images':c.execute('SELECT COUNT(*) FROM work_images').fetchone()[0]}; c.close(); return jsonify({'ok':True,'database':os.path.getsize(DB),'counts':counts,'python':os.sys.version.split()[0],'port':5022,'admin':current_admin(),'role':session.get('admin_role')})

@app.get('/api/admin/logs')
def logs():
    if (x:=need()): return x
    page=max(1,int(request.args.get('page',1))); size=20; c=db()
    if is_super():
        total=c.execute('SELECT COUNT(*) FROM operation_logs').fetchone()[0]
        rows=c.execute('SELECT * FROM operation_logs ORDER BY id DESC LIMIT ? OFFSET ?',(size,(page-1)*size)).fetchall()
    else:
        total=c.execute("SELECT COUNT(*) FROM operation_logs WHERE admin_id NOT IN (SELECT id FROM admins WHERE role='super')").fetchone()[0]
        rows=c.execute("SELECT * FROM operation_logs WHERE admin_id NOT IN (SELECT id FROM admins WHERE role='super') ORDER BY id DESC LIMIT ? OFFSET ?",(size,(page-1)*size)).fetchall()
    c.close(); return jsonify({'items':[dict(x) for x in rows],'total':total,'page':page,'pages':(total+size-1)//size})

@app.get('/api/admin/admins')
def admin_list():
    if (x:=need()): return x
    if not is_super(): return jsonify({'message':'只有超级管理员可以管理管理员'}),403
    c=db(); rows=c.execute('SELECT id,username,role,display_name,created_at,updated_at FROM admins ORDER BY id').fetchall(); c.close(); return jsonify([dict(x) for x in rows])

@app.get('/api/admin/admins/<int:aid>')
def admin_detail(aid):
    if (x:=need()): return x
    if not is_super(): return jsonify({'message':'只有超级管理员可以管理管理员'}),403
    c=db(); row=c.execute('SELECT id,username,role,display_name,created_at,updated_at FROM admins WHERE id=?',(aid,)).fetchone(); c.close()
    if not row: return jsonify({'message':'管理员不存在'}),404
    return jsonify(dict(row))

@app.post('/api/admin/admins')
def admin_create():
    if (x:=need()): return x
    if not is_super(): return jsonify({'message':'只有超级管理员可以管理管理员'}),403
    d=request.get_json() or {}; username=(d.get('username') or '').strip(); password=d.get('password') or ''; display=(d.get('display_name') or '').strip(); role=d.get('role') or 'admin'
    if not username or not password: return jsonify({'ok':False,'message':'账号和密码不能为空'}),400
    if len(username)>30 or len(password)<6: return jsonify({'ok':False,'message':'账号最多30字，密码至少6位'}),400
    if role not in ('admin','super'): role='admin'
    now=datetime.now().isoformat(timespec='seconds'); c=db()
    try:
        cur=c.execute('INSERT INTO admins(username,password_hash,role,display_name,created_at,updated_at) VALUES(?,?,?,?,?,?)',(username,generate_password_hash(password),role,display or username,now,now))
        aid=cur.lastrowid
        c.commit()
        write_log('新增管理员',f'管理员ID：{aid}，账号：{username}，权限：{"超级管理员" if role=="super" else "管理员"}')
        return jsonify({'ok':True,'id':aid})
    except sqlite3.IntegrityError:
        c.rollback(); return jsonify({'ok':False,'message':'账号已存在'}),400
    finally: c.close()

@app.put('/api/admin/admins/<int:aid>')
def admin_update(aid):
    if (x:=need()): return x
    if not is_super(): return jsonify({'message':'只有超级管理员可以管理管理员'}),403
    d=request.get_json() or {}; username=(d.get('username') or '').strip(); password=d.get('password') or ''; display=(d.get('display_name') or '').strip(); role=d.get('role') or 'admin'; c=db(); row=c.execute('SELECT * FROM admins WHERE id=?',(aid,)).fetchone()
    if not row: c.close(); return jsonify({'message':'管理员不存在'}),404
    if not username: c.close(); return jsonify({'message':'账号不能为空'}),400
    if len(username)>30 or (password and len(password)<6): c.close(); return jsonify({'message':'账号最多30字，密码至少6位'}),400
    if role not in ('admin','super'): c.close(); return jsonify({'message':'权限设置无效'}),400
    if row['username']=='admin':
        role='super'
        display='超级管理员'
    if aid==session.get('admin_id') and role!='super': c.close(); return jsonify({'message':'超级管理员不能取消自己的超级管理员权限'}),400
    try:
        if password: c.execute('UPDATE admins SET username=?,password_hash=?,role=?,display_name=?,updated_at=? WHERE id=?',(username,generate_password_hash(password),role,display or username,datetime.now().isoformat(timespec='seconds'),aid))
        else: c.execute('UPDATE admins SET username=?,role=?,display_name=?,updated_at=? WHERE id=?',(username,role,display or username,datetime.now().isoformat(timespec='seconds'),aid))
        c.commit(); write_log('编辑管理员',f'管理员ID：{aid}，账号：{username}'); return jsonify({'ok':True})
    except sqlite3.IntegrityError: c.rollback(); return jsonify({'ok':False,'message':'账号已存在'}),400
    finally: c.close()

@app.delete('/api/admin/admins/<int:aid>')
def admin_delete(aid):
    if (x:=need()): return x
    if not is_super(): return jsonify({'message':'只有超级管理员可以管理管理员'}),403
    if aid==session.get('admin_id'): return jsonify({'ok':False,'message':'不能删除当前登录管理员'}),400
    c=db(); row=c.execute('SELECT username,role FROM admins WHERE id=?',(aid,)).fetchone()
    if not row: c.close(); return jsonify({'ok':False,'message':'管理员不存在'}),404
    if row['role']=='super' and c.execute("SELECT COUNT(*) FROM admins WHERE role='super'").fetchone()[0]<=1: c.close(); return jsonify({'ok':False,'message':'至少保留一名超级管理员'}),400
    c.execute('DELETE FROM admins WHERE id=?',(aid,)); c.commit(); c.close(); write_log('删除管理员',f'管理员ID：{aid}，账号：{row["username"]}'); return jsonify({'ok':True})

@app.post('/api/admin/categories')
def add_cat():
    if (x:=need()): return x
    d=request.get_json() or {}; c=db(); c.execute('INSERT INTO categories(name) VALUES(?)',(d.get('name'),)); c.commit(); c.close(); write_log('新增一级分类',f'分类：{d.get("name")}'); return jsonify({'ok':True})
@app.post('/api/admin/subcategories')
def add_sub():
    if (x:=need()): return x
    d=request.get_json() or {}; c=db(); c.execute('INSERT INTO subcategories(category_id,name) VALUES(?,?)',(d.get('category_id'),d.get('name'))); c.commit(); c.close(); write_log('新增二级分类',f'分类ID：{d.get("category_id")}，名称：{d.get("name")}'); return jsonify({'ok':True})
@app.put('/api/admin/categories/<int:cid>')
def update_cat(cid):
    if (x:=need()): return x
    d=request.get_json() or {}; name=(d.get('name') or '').strip(); c=db()
    try: c.execute('UPDATE categories SET name=? WHERE id=?',(name,cid)); c.commit(); write_log('编辑一级分类',f'分类ID：{cid}，名称：{name}')
    except sqlite3.IntegrityError: c.close(); return jsonify({'ok':False,'message':'分类名称已存在'}),400
    c.close(); return jsonify({'ok':True})

@app.delete('/api/admin/categories/<int:cid>')
def delete_cat(cid):
    if (x:=need()): return x
    c=db(); sub=c.execute('SELECT COUNT(*) FROM subcategories WHERE category_id=?',(cid,)).fetchone()[0]; used=c.execute('SELECT COUNT(*) FROM works WHERE category_id=?',(cid,)).fetchone()[0]
    if sub or used: c.close(); return jsonify({'ok':False,'message':'该分类正在使用，不能删除'}),400
    c.execute('DELETE FROM categories WHERE id=?',(cid,)); c.commit(); c.close(); write_log('删除一级分类',f'分类ID：{cid}'); return jsonify({'ok':True})

@app.put('/api/admin/subcategories/<int:sid>')
def update_sub(sid):
    if (x:=need()): return x
    d=request.get_json() or {}; name=(d.get('name') or '').strip(); c=db()
    try: c.execute('UPDATE subcategories SET name=? WHERE id=?',(name,sid)); c.commit(); write_log('编辑二级分类',f'分类ID：{sid}，名称：{name}')
    except sqlite3.IntegrityError: c.close(); return jsonify({'ok':False,'message':'细分类名称已存在'}),400
    c.close(); return jsonify({'ok':True})

@app.delete('/api/admin/subcategories/<int:sid>')
def delete_sub(sid):
    if (x:=need()): return x
    c=db(); used=c.execute('SELECT COUNT(*) FROM works WHERE subcategory_id=?',(sid,)).fetchone()[0]
    if used: c.close(); return jsonify({'ok':False,'message':'该细分类正在使用，不能删除'}),400
    c.execute('DELETE FROM subcategories WHERE id=?',(sid,)); c.commit(); c.close(); write_log('删除二级分类',f'分类ID：{sid}'); return jsonify({'ok':True})

@app.post('/api/admin/periods')
def add_period():
    if (x:=need()): return x
    d=request.get_json() or {}; c=db(); c.execute('INSERT INTO periods(name) VALUES(?)',(d.get('name'),)); c.commit(); c.close(); write_log('新增创作时间',f'时间：{d.get("name")}'); return jsonify({'ok':True})

if __name__=='__main__': app.run(host='0.0.0.0',port=5033,debug=False)
