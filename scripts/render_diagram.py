"""Render the same architecture to SVG and PNG, without network access."""
from pathlib import Path
from html import escape
from math import atan2, cos, sin, pi, hypot
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs' / 'diagrams'
W, H = 2600, 1900
BG, INK, BLUE, GREEN, GREY, PURPLE = '#f5f7fb', '#17243b', '#3458be', '#168275', '#637086', '#8542ac'
img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="{BG}"/>']
font_candidates = ['/System/Library/Fonts/Supplemental/Arial.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 'C:/Windows/Fonts/arial.ttf']
font_path = next((p for p in font_candidates if Path(p).exists()), None)
if not font_path:
    raise SystemExit('Install Arial or DejaVu Sans and add its path to font_candidates.')

def text(x, y, value, size=24, color=INK, center=False):
    font = ImageFont.truetype(font_path, size)
    d.text((x, y), value, font=font, fill=color, anchor='mt' if center else 'lt')
    svg.append(f'<text x="{x}" y="{y + size * .85}" font-family="Arial,DejaVu Sans,sans-serif" font-size="{size}" fill="{color}" text-anchor="{"middle" if center else "start"}">{escape(value)}</text>')

def rect(x, y, w, h, fill='white', border=BLUE, radius=16):
    d.rounded_rectangle((x,y,x+w,y+h),radius=radius,fill=fill,outline=border,width=2)
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{border}" stroke-width="2"/>')

def box(x, y, w, h, title, lines=(), fill='white', border=BLUE):
    rect(x,y,w,h,fill,border)
    text(x+w/2,y+20,title,27,center=True)
    for i, value in enumerate(lines):
        text(x+w/2,y+62+i*29,value,21,GREY,True)

def line(points, color=BLUE, dashed=False, arrow=True):
    if dashed:
        for a,b in zip(points,points[1:]):
            length=hypot(b[0]-a[0],b[1]-a[1])
            if not length:
                continue
            for t in range(0,int(length),18):
                u,v=t/length,min(t+10,length)/length
                d.line([(a[0]+(b[0]-a[0])*u,a[1]+(b[1]-a[1])*u),(a[0]+(b[0]-a[0])*v,a[1]+(b[1]-a[1])*v)],fill=color,width=3)
    else:
        d.line(points,fill=color,width=3)
    svg.append(f'<polyline points="{" ".join(f"{x},{y}" for x,y in points)}" fill="none" stroke="{color}" stroke-width="3"'+(' stroke-dasharray="10 8"' if dashed else '')+'/>')
    if arrow:
        a,b=points[-2:]
        angle=atan2(b[1]-a[1],b[0]-a[0])
        pts=[b]+[(b[0]-14*cos(angle+s*pi/7),b[1]-14*sin(angle+s*pi/7)) for s in (-1,1)]
        d.polygon(pts,fill=color)
        svg.append(f'<polygon points="{" ".join(f"{x},{y}" for x,y in pts)}" fill="{color}"/>')

text(70,40,'ReWear / Микросервисная архитектура',46)
text(70,105,'6 сервисов · admin / customer · резерв при оформлении · WebSocket без polling',28,GREY)
box(930,160,620,110,'Браузер покупателя / admin',['Главная, страницы, пресеты, корзина'],border=GREY)
text(1820,185,'Изображения: браузер → Nginx → Image → S3',25,GREY)
text(1820,230,'Локальный кеш, без распределённого CDN',23,GREY)
rect(30,320,2550,1440,BG,GREY,24)
text(70,350,'Docker Compose / Minikube',28,GREY)
text(70,395,'namespace rewear · 6 отдельных PostgreSQL',23,GREY)
box(930,355,620,100,'Nginx / API Gateway',['HTTP, WebSocket Upgrade, /media cache'],fill='#eaf0ff')
line([(1240,270),(1240,355)]); text(1260,300,'HTTP / JWT',22)
line([(1460,355),(1460,270)],PURPLE); text(1490,295,'WS push',22,PURPLE)
xs=[70,490,910,1330,1750,2170]
for x,label in zip(xs,['каталог / admin','корзина','заказы','уведомления','вход / роли','изображения']):
    line([(1240,455),(1240,500),(x+180,500),(x+180,550)])
    text(x+180,480,label,20,center=True)
services=[
 ('Catalog Service',['Товары, остатки и пресеты','CatalogPage / page_id','Availability events + outbox']),
 ('Cart Service',['До 10 вещей, без резерва','Consumer доступности','Персональные события']),
 ('Order Service',['Оркестратор саги','Тестовая оплата','Резерв и итог → RabbitMQ']),
 ('Notification Service',['Кому / что / когда отправили','SignalR: WebSocket only','ACK после commit · event_id']),
 ('Auth Service',['Регистрация / вход','JWT: admin / customer','Хеши паролей']),
 ('Image Service',['Загрузка admin / GET по ID','Metadata + S3-файлы','JSON товара содержит URL']),
]
for x,(title,ls),db in zip(xs,services,['catalog_db','cart_db','order_db','notification_db','auth_db','image_db']):
    box(x,550,360,175,title,ls)
    line([(x+180,725),(x+180,805)],GREY); text(x+200,755,'SQL',21,GREY)
    box(x+55,805,260,90,db,['PostgreSQL'],fill='#eef5f4',border=GREEN)
line([(1510,550),(1510,475),(1490,475),(1490,455)],PURPLE)
text(1560,435,'WS: персональный push',22,PURPLE)
# Telemetry from every service, including Image.
for x in xs: line([(x+330,725),(x+330,940)],GREY,True,False)
line([(400,940),(2570,940),(2570,1500),(2530,1500)],GREY,True)
text(1020,955,'OTLP: логи, метрики, трейсы всех 6 сервисов',22,GREY)
# Short Cart read and the Order commands.
line([(490,620),(430,620)]); text(125,985,'Cart → Catalog: HTTP / товары',21)
line([(930,725),(930,1080),(450,1080),(450,680),(490,680)])
text(530,1095,'Order → Cart: read / очистка',22)
line([(950,725),(950,1130),(50,1130),(50,620),(70,620)])
text(120,1148,'Order → Catalog: reserve / complete / release',22)
# Catalog verifies image metadata; Nginx retrieves bytes via Image.
line([(430,650),(460,650),(460,1190),(2120,1190),(2120,650),(2170,650)])
text(2170,990,'Catalog → Image: metadata по ID',20)
line([(1550,400),(2570,400),(2570,680),(2530,680)])
text(2180,430,'/media → Image GET /images/{id}',21)
box(2170,1060,360,180,'S3 / SeaweedFS',[
 'Файлы на volume','Читает и пишет только Image','Ключи S3 не в браузере',
],fill='#eef5f4',border=GREEN)
line([(2530,630),(2550,630),(2550,1140),(2530,1140)])
text(2190,1260,'JWT API: подпись, sub, role, exp',20,GREY)
box(70,1340,370,220,'Redis / page=1',[
 'Без фильтров · TTL 60 с','DEL после правок каталога','Наличие — PostgreSQL','Redis down → БД',
],fill='#eaf0ff')
line([(110,725),(110,1280),(250,1280),(250,1340)])
text(125,1300,'RESP: cache-aside',21)
# Separate queues are essential: Cart and Notification need their own deliveries.
box(550,1270,1450,430,'RabbitMQ / Exchange: shop.events',fill='#e8f6f2',border=GREEN)
rect(590,1330,1370,100,'white',GREEN)
text(1275,1350,'Catalog: catalog.availability_changed',25,GREEN,True)
text(1275,1392,'Cart: cart.item_added / item_availability_changed · Order: reserved / confirmed / cancelled',23,GREEN,True)
rect(590,1490,650,80,'white',GREEN); text(915,1515,'Queue: cart.availability',27,center=True)
rect(1310,1490,650,80,'white',GREEN); text(1635,1515,'Queue: notifications.events',27,center=True)
line([(915,1430),(915,1490)],GREEN,True)
line([(1635,1430),(1635,1490)],GREEN,True)
text(1275,1600,'Catalog / Cart / Order: outbox + LISTEN/NOTIFY, без polling',24,GREEN,True)
text(1275,1644,'Cart: version/dedup → свои user_id · Notification: commit → ACK → WebSocket',22,GREEN,True)
line([(90,725),(90,1230),(800,1230),(800,1330)],GREEN,True)
text(130,1200,'ProductAvailabilityChanged',21,GREEN)
line([(850,680),(870,680),(870,1250),(1100,1250),(1100,1330)],GREEN,True)
text(880,1210,'Cart: добавление / доступность',21,GREEN)
line([(1270,680),(1290,680),(1290,1220),(1400,1220),(1400,1330)],GREEN,True)
text(1430,1220,'Order: резерв / итог',21,GREEN)
line([(590,1530),(470,1530),(470,650),(490,650)],GREEN,True)
line([(1960,1530),(2010,1530),(2010,1220),(1710,1220),(1710,680),(1690,680)],GREEN,True)
box(2170,1340,360,360,'Observability',[
 'OpenTelemetry Collector','Loki — логи','Grafana — просмотр','Tempo — трейсы','Mimir — метрики',
],fill='#f0edf8',border=GREY)
text(2350,1630,'Локальный LGTM',23,GREY,True)
line([(75,1820),(155,1820)],BLUE); text(175,1807,'HTTP / SQL / RESP / S3',24)
line([(780,1820),(860,1820)],GREEN,True); text(880,1807,'AMQP: события',24)
line([(1410,1820),(1490,1820)],PURPLE); text(1510,1807,'WebSocket push',24)
line([(2020,1820),(2100,1820)],GREY,True); text(2120,1807,'OTLP: телеметрия',24)
text(75,1860,'В исходном ТЗ 3–5 сервисов: выбранные 6 требуют согласования. Инфраструктура не считается бизнес-микросервисами.',23,GREY)
OUT.mkdir(parents=True,exist_ok=True)
svg.append('</svg>')
(OUT/'architecture.svg').write_text('\n'.join(svg),encoding='utf-8')
img.save(OUT/'architecture.png')
print(f'Generated architecture.svg and architecture.png ({W}x{H})')
