from pathlib import Path
import csv
import math
import numpy as np
import pandas as pd

RNG = np.random.default_rng(20260721)
OUT = Path("mlaas_test_datasets")
OUT.mkdir(exist_ok=True)
END = pd.Timestamp("2025-12-31")

CATS = ["Electronics", "Computers", "Home", "Kitchen", "Grocery", "Beauty", "Sports", "Books", "Toys", "Office", "Clothing", "Garden"]

def ids(prefix, n, width=6): return [f"{prefix}{i:0{width}d}" for i in range(1, n + 1)]
def money(x): return np.round(np.maximum(x, .01), 2)
def save(df, name):
    df.to_csv(OUT / name, index=False, encoding="utf-8", quoting=csv.QUOTE_MINIMAL, date_format="%Y-%m-%d %H:%M:%S")

def rfm():
    customers = ids("C", 1500)
    segments = RNG.choice(["loyal","new","risk","lost","potential"], len(customers), p=[.25,.15,.2,.15,.25])
    rows=[]; inv=1
    for c,s in zip(customers,segments):
        if s=="loyal": n,lo,hi,scale=RNG.integers(10,20),0,730,150
        elif s=="new": n,lo,hi,scale=1,0,45,80
        elif s=="risk": n,lo,hi,scale=RNG.integers(9,17),150,730,130
        elif s=="lost": n,lo,hi,scale=RNG.integers(2,5),380,730,70
        else: n,lo,hi,scale=RNG.integers(5,10),30,300,100
        days=RNG.integers(lo,hi+1,n)
        for d in days:
            rows.append((c,END-pd.Timedelta(days=int(d)),f"RFM{inv:08d}",round(float(RNG.lognormal(math.log(scale),.65)),2))); inv+=1
    save(pd.DataFrame(rows,columns=["customer_id","invoice_date","invoice_id","total_amount"]),"rfm_transactions.csv")

def basket():
    core=[("Coffee","Coffee Filters","Grocery"),("Laptop","Laptop Sleeve","Computers"),("Smartphone","Phone Case","Electronics"),("Printer","Printer Paper","Office"),("Shampoo","Conditioner","Beauty"),("Pasta","Pasta Sauce","Grocery"),("Gaming Console","Game Controller","Electronics")]
    special={x:z for a,b,z in core for x in (a,b)}
    products=list(special)+[f"{CATS[i%len(CATS)]} Product {i:03d}" for i in range(1,137)]
    rows=[]
    for i in range(1,8001):
        chosen=[]
        if RNG.random()<.55:
            a,b,_=core[int(RNG.integers(len(core)))]; chosen=[a,b]
            if RNG.random()<.35: chosen += list(core[int(RNG.integers(len(core)))][:2])
        target=int(RNG.integers(2,7))
        while len(set(chosen))<target: chosen.append(products[int(RNG.integers(len(products)))])
        for p in dict.fromkeys(chosen): rows.append((f"MBA{i:07d}",p,special.get(p,p.split(" Product")[0]),int(RNG.integers(1,5))))
    save(pd.DataFrame(rows,columns=["invoice_id","product_name","product_category","quantity"]),"market_basket_transactions.csv")

def churn():
    n=7000; cid=ids("CH",n); churned=RNG.binomial(1,.28,n); edge=RNG.random(n)<.13
    days=np.where(churned==1,RNG.integers(100,600,n),RNG.integers(0,150,n)); days=np.where(edge,RNG.integers(25,350,n),days)
    tenure=days+RNG.integers(60,1400,n); count=np.maximum(1,(tenure/90+RNG.normal(0,3,n)-(churned*2)).astype(int))
    aov=money(RNG.lognormal(4.5,.55,n)); returns=np.maximum(0,RNG.poisson(.4+churned*.9,n)); tickets=np.maximum(0,RNG.poisson(.8+churned*1.6,n))
    engage=np.clip(RNG.beta(3-churned*1.3,3+churned*2,n)+(edge*(churned*2-1)*.18),0,1)
    df=pd.DataFrame({"customer_id":cid,"last_purchase_date":END-pd.to_timedelta(days,unit="D"),"first_purchase_date":END-pd.to_timedelta(tenure,unit="D"),"purchase_count":count,"total_spend":money(count*aov*RNG.normal(1,.06,n)),"average_order_value":aov,"days_since_last_purchase":days,"support_ticket_count":tickets,"returned_order_count":returns,"email_engagement_rate":np.round(engage,4),"churned":churned})
    save(df,"customer_churn.csv")

def clv():
    rows=[]; inv=1
    for i,c in enumerate(ids("CLV",2200)):
        typ=RNG.choice(["high","one","seasonal","recent","growth","decline"],p=[.18,.2,.15,.15,.16,.16])
        n={"high":RNG.integers(12,24),"one":1,"seasonal":RNG.integers(4,9),"recent":RNG.integers(2,6),"growth":RNG.integers(7,14),"decline":RNG.integers(7,14)}[typ]
        if typ=="recent": days=np.sort(RNG.integers(0,120,n))[::-1]
        elif typ=="seasonal": days=RNG.choice(np.r_[0:60,330:430,680:730],n,replace=True)
        else: days=np.sort(RNG.integers(0,730,n))[::-1]
        base={"high":260,"one":65,"seasonal":120,"recent":90,"growth":80,"decline":180}[typ]
        for j,d in enumerate(days):
            trend=(1+j/(max(n-1,1))*.8) if typ=="growth" else ((1.5-j/(max(n-1,1))*.7) if typ=="decline" else 1)
            rows.append((c,f"CLV{inv:08d}",END-pd.Timedelta(days=int(d)),round(float(RNG.lognormal(math.log(base*trend),.45)),2),RNG.choice(CATS),RNG.choice(["Organic Search","Paid Search","Social","Email","Referral","Marketplace"],p=[.25,.18,.18,.16,.13,.10]))); inv+=1
    save(pd.DataFrame(rows,columns=["customer_id","invoice_id","invoice_date","total_amount","product_category","acquisition_channel"]),"customer_lifetime_value.csv")

def product_share():
    nprod=180; pids=ids("P",nprod,4); ranks=np.arange(1,nprod+1); weights=1/ranks**1.05; weights/=weights.sum()
    base=RNG.lognormal(3.5,.7,nprod); rows=[]
    for i in range(28000):
        p=int(RNG.choice(nprod,p=weights)); date=END-pd.Timedelta(days=int(RNG.integers(0,730))); cat=CATS[p%len(CATS)]
        season=1.5 if (cat in ["Toys","Electronics"] and date.month in [11,12]) or (cat=="Garden" and date.month in [3,4,5]) else 1
        qty=int(np.clip(RNG.poisson(1.3*season)+1,1,12)); price=round(float(base[p]*RNG.normal(1,.04)),2)
        rows.append((f"PS{i+1:08d}",date,pids[p],f"{cat} Item {p+1:03d}",cat,qty,price,round(qty*price,2)))
    save(pd.DataFrame(rows,columns=["invoice_id","invoice_date","product_id","product_name","product_category","quantity","unit_price","total_amount"]),"product_share.csv")

def propensity():
    rows=[]; inv=1
    for c in ids("PP",2500):
        typ=RNG.choice(["regular","once","increase","inactive"],p=[.42,.12,.23,.23]); n={"regular":RNG.integers(7,14),"once":1,"increase":RNG.integers(5,11),"inactive":RNG.integers(5,11)}[typ]
        if typ=="inactive": days=RNG.integers(180,730,n)
        elif typ=="increase": days=(RNG.random(n)**2*730).astype(int)
        elif typ=="once": days=np.array([RNG.integers(150,650)])
        else: days=RNG.integers(0,730,n)
        for d in days: rows.append((c,END-pd.Timedelta(days=int(d)),round(float(RNG.lognormal(4.5,.75)),2))); inv+=1
    save(pd.DataFrame(rows,columns=["customer_id","invoice_date","invoice_amount"]),"purchase_propensity.csv")

def anomalies():
    n=12000; dates=pd.to_datetime(RNG.integers(pd.Timestamp("2024-01-01").value//10**9,(END+pd.Timedelta(days=1)).value//10**9,n),unit="s")
    qty=RNG.integers(1,7,n); amt=money(RNG.lognormal(4.6,.55,n)*qty); invoice=np.array(ids("AN",n,8),dtype=object)
    k=240; ix=RNG.choice(n,k,replace=False); groups=np.array_split(ix,6)
    amt[groups[0]]=money(RNG.uniform(10000,50000,len(groups[0]))); amt[groups[1]]=RNG.choice([-99.0,-20.0,.01,.10],len(groups[1])); qty[groups[2]]=RNG.integers(60,300,len(groups[2])); amt[groups[2]]=money(RNG.uniform(5,80,len(groups[2])))
    dates=pd.Series(dates); dates.iloc[groups[3]]=dates.iloc[groups[3]].dt.normalize()+pd.to_timedelta(RNG.integers(0,4,len(groups[3])),unit="h")
    burst=pd.Timestamp("2025-09-17 14:00:00")+pd.to_timedelta(RNG.integers(0,900,len(groups[4])),unit="s"); dates.iloc[groups[4]]=burst; amt[groups[4]]=money(RNG.uniform(6000,18000,len(groups[4])))
    invoice[groups[5]]=invoice[groups[5]-1]
    df=pd.DataFrame({"invoice_id":invoice,"invoice_date":dates,"total_amount":amt,"customer_id":RNG.choice(ids("C",3000),n),"product_category":RNG.choice(CATS,n),"quantity":qty,"sales_channel":RNG.choice(["Web","Mobile","Store","Marketplace"],n,p=[.45,.3,.15,.1])})
    save(df,"sales_anomalies.csv")

def demand():
    products=60; dates=pd.date_range("2024-01-01","2025-12-31"); rows=[]; holidays={(1,1),(11,29),(12,24),(12,25)}
    for p in range(products):
        cat=CATS[p%len(CATS)]; base=RNG.uniform(4,35); price=RNG.uniform(8,250); trend=RNG.uniform(-.0005,.001)
        inv=int(RNG.integers(80,350))
        for t,d in enumerate(dates):
            promo=int(RNG.random()<.06); hol=int((d.month,d.day) in holidays); weekly=1.22 if d.dayofweek in [4,5] else .9 if d.dayofweek==0 else 1
            monthly=1+.18*math.sin(2*math.pi*(d.month-1)/12+p%4); seasonal=1.5 if (cat in ["Toys","Electronics"] and d.month in [11,12]) else 1
            demand=max(0,RNG.poisson(max(.2,base*weekly*monthly*seasonal*(1+trend*t)*(1+.45*promo+.55*hol))))
            stockout=int(inv<=0 or RNG.random()<.012); sold=0 if stockout else min(demand,inv); inv=max(0,inv-sold)
            if d.day==1 or inv<20: inv+=int(RNG.integers(80,260))
            rows.append((d,f"DP{p+1:04d}",f"{cat} Demand Item {p+1:03d}",cat,sold,round(price*(.9 if promo else 1),2),inv,promo,hol,stockout))
    save(pd.DataFrame(rows,columns=["date","product_id","product_name","product_category","units_sold","unit_price","inventory_level","promotion_active","holiday","stockout"]),"demand_forecast.csv")

def recommendations():
    nc,npd,n=6000,700,60000; pids=ids("RP",npd,5); popularity=np.r_[np.repeat(8,30),np.repeat(2,470),np.repeat(.25,200)]; popularity=popularity/popularity.sum(); rows=[]
    for i in range(n):
        c=int(RNG.integers(nc)); pref=c%len(CATS)
        if RNG.random()<.62:
            candidates=np.arange(pref,npd,len(CATS)); p=int(RNG.choice(candidates))
        else: p=int(RNG.choice(npd,p=popularity))
        typ=RNG.choice(["view","cart","purchase"],p=[.72,.18,.10]); rating=int(RNG.integers(1,6)) if typ=="purchase" and RNG.random()<.72 else np.nan
        rows.append((f"RC{c+1:06d}",pids[p],f"{CATS[p%len(CATS)]} Recommendation Item {p+1:04d}",CATS[p%len(CATS)],typ,END-pd.Timedelta(days=int(RNG.integers(0,550)),hours=int(RNG.integers(24))),int(RNG.integers(1,5)) if typ=="purchase" else 1,rating))
    save(pd.DataFrame(rows,columns=["customer_id","product_id","product_name","product_category","interaction_type","interaction_date","quantity","rating"]),"product_recommendations.csv")

def price_opt():
    dates=pd.date_range("2025-01-01","2025-12-31"); rows=[]
    for p in range(100):
        cat=CATS[p%len(CATS)]; cost=RNG.uniform(5,140); margin=RNG.uniform(1.08,2.3); base=cost*margin; sensitivity=RNG.uniform(.8,2.5); normal=RNG.uniform(5,55)
        for d in dates:
            promo=int(RNG.random()<.08); price=base*RNG.uniform(.88,1.14)*(.86 if promo else 1); comp=base*RNG.uniform(.85,1.18)
            seasonal=1+.22*math.sin(2*math.pi*(d.dayofyear/365)+(p%6)); demand=normal*seasonal*math.exp(-sensitivity*(price/base-1))*(1+.38*promo)*(1+.5*(comp/price-1))
            units=max(0,int(RNG.poisson(max(.2,demand)))); inventory=int(max(units,RNG.normal(220,75)))
            rows.append((d,f"OP{p+1:04d}",f"{cat} Price Item {p+1:03d}",cat,round(price,2),units,round(cost,2),round(comp,2),promo,inventory))
    save(pd.DataFrame(rows,columns=["date","product_id","product_name","product_category","unit_price","units_sold","unit_cost","competitor_price","promotion_active","inventory_level"]),"price_optimization.csv")

for fn in [rfm,basket,churn,clv,product_share,propensity,anomalies,demand,recommendations,price_opt]: fn()
