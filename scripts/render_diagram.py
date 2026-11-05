"""Render matching SVG and PNG architecture artifacts; no network required."""
from pathlib import Path
from html import escape
from math import atan2, cos, sin, pi, hypot
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs' / 'diagrams'
W, H = 1920, 1280
BG, INK, BLUE, GREEN, GREY = '#f5f7fb', '#17243b', '#3458be', '#168275', '#637086'
img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="{BG}"/>']
font_candidates = ['/System/Library/Fonts/Supplemental/Arial.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 'C:/Windows/Fonts/arial.ttf']
font_path = next((p for p in font_candidates if Path(p).exists()), None)
if not font_path:
    raise SystemExit('Install Arial or DejaVu Sans and add its path to font_candidates.')

def text(x, y, value, size=24, color=INK, center=False):
    font = ImageFont.truetype(font_path, size)
    anchor = 'mt' if center else 'lt'
    d.text((x, y), value, font=font, fill=color, anchor=anchor)
    svg.append(f'<text x="{x}" y="{y + size * .85}" font-family="Arial,DejaVu Sans,sans-serif" font-size="{size}" fill="{color}" text-anchor="{"middle" if center else "start"}">{escape(value)}</text>')

def box(x, y, w, h, title, lines=(), fill='white', border=BLUE):
    d.rounded_rectangle((x,y,x+w,y+h), radius=16, fill=fill, outline=border, width=2)
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{fill}" stroke="{border}" stroke-width="2"/>')
    text(x+w/2, y+20, title, 27, center=True)
    for i,line in enumerate(lines): text(x+w/2, y+62+i*27, line, 21, GREY, True)

def line(points, color=BLUE, dashed=False, arrow=True):
    if dashed:
        for a,b in zip(points,points[1:]):
            length=hypot(b[0]-a[0],b[1]-a[1])
            for t in range(0,int(length),18):
                u,v=t/length,min(t+10,length)/length
                d.line([(a[0]+(b[0]-a[0])*u,a[1]+(b[1]-a[1])*u),(a[0]+(b[0]-a[0])*v,a[1]+(b[1]-a[1])*v)],fill=color,width=3)
    else: d.line(points,fill=color,width=3)
    svg.append(f'<polyline points="{" ".join(f"{x},{y}" for x,y in points)}" fill="none" stroke="{color}" stroke-width="3"'+(' stroke-dasharray="10 8"' if dashed else '')+'/>')
    if arrow:
        a,b=points[-2:]; angle=atan2(b[1]-a[1],b[0]-a[0]); pts=[b]+[(b[0]-14*cos(angle+s*pi/7),b[1]-14*sin(angle+s*pi/7)) for s in (-1,1)]
        d.polygon(pts,fill=color)
        svg.append(f'<polygon points="{" ".join(f"{x},{y}" for x,y in pts)}" fill="{color}"/>')

d.rounded_rectangle((40,275,1875,1175),radius=24,outline=GREY,width=2)
svg.append(f'<rect x="40" y="275" width="1835" height="900" rx="24" fill="none" stroke="{GREY}" stroke-width="2"/>')
text(75,300,'Minikube / namespace rewear',24,GREY)
text(75,340,'или Docker Compose',22,GREY)
text(70,40,'ReWear / Микросервисная архитектура',44)
text(70,102,'4 бизнес-сервиса · PostgreSQL + RabbitMQ + Redis · Compose / Kubernetes (Minikube)',25,GREY)
box(650,160,620,90,'Покупатель / веб-интерфейс',(),border=GREY)
box(650,295,620,90,'Nginx / API Gateway',(),fill='#eaf0ff')
line([(960,250),(960,295)]); text(980,259,'HTTP',20)
xs=[90,530,970,1410]
for x,route in zip(xs,['каталог','корзина','заказы','уведомления']):
    line([(960,385),(960,405),(x+180,405),(x+180,430)])
    text(x+180,392,'HTTP: '+route,18,center=True)
services=[('Catalog Service',['Товары и цены','Уникальные остатки, резервы']),('Cart Service',['Выбранные вещи','Корзина без резерва']),('Order Service',['Заказ и тестовая оплата','Outbox и восстановление']),('Notification Service',['Уведомления в приложении','Дедупликация event_id'])]
for x,(title,ls),db in zip(xs,services,['catalog_db','cart_db','order_db','notification_db']):
    box(x,430,360,145,title,ls)
    line([(x+210,575),(x+210,630)],GREY); text(x+230,594,'SQL',20,GREY)
    box(x+70,630,280,92,db,['PostgreSQL'],fill='#eef5f4',border=GREEN)
# Internal HTTP paths run outside DB boxes.
line([(550,575),(550,800),(475,800),(475,505),(450,505)])
text(585,775,'Cart → Catalog: HTTP / batch products',24)
line([(990,575),(990,865),(510,865),(510,530),(530,530)])
text(550,835,'Order → Cart: HTTP / read, remove-items',22)
line([(1010,575),(1010,930),(60,930),(60,505),(90,505)])
text(140,945,'Order → Catalog: HTTP / reserve, read, complete, release',24)
box(160,1045,460,112,'Redis / кеш Catalog',['TTL 60 с · без остатков'],fill='#eaf0ff')
line([(110,575),(110,1000),(385,1000),(385,1045)])
text(145,1008,'RESP: кеш чтения',22)
box(1330,1045,460,112,'RabbitMQ',['orders.events → notifications.orders'],fill='#e8f6f2',border=GREEN)
line([(1330,550),(1340,550),(1340,1015),(1295,1015),(1295,1101),(1330,1101)],GREEN,True)
text(760,1040,'AMQP: OrderConfirmed',24,GREEN)
text(760,1074,'или OrderCancelled',24,GREEN)
line([(1790,1101),(1840,1101),(1840,505),(1770,505)],GREEN,True)
text(1410,986,'AMQP: события → Notification',23,GREEN)
line([(75,1205),(155,1205)],BLUE); text(175,1192,'Синхронно (HTTP / SQL)',23)
line([(660,1205),(740,1205)],GREEN,True); text(760,1192,'Асинхронно (AMQP)',23)
text(1300,1192,'Redis: кеш, PostgreSQL: данные',23,GREY)
OUT.mkdir(parents=True, exist_ok=True)
svg.append('</svg>')
(OUT/'architecture.svg').write_text('\n'.join(svg),encoding='utf-8')
img.save(OUT/'architecture.png')
print(f'Generated {OUT}/architecture.svg and architecture.png ({W}x{H})')
