import os,json,time,io,zipfile,datetime,xml.etree.ElementTree as ET
from pathlib import Path
from zoneinfo import ZoneInfo
import requests
ROOT=Path(__file__).resolve().parent
API="https://opendart.fss.or.kr/api/"
KEY=os.environ.get("DART_API_KEY")
FIELDS={"매출액":"revenue","수익(매출액)":"revenue","영업이익":"operating_profit","영업이익(손실)":"operating_profit","영업손실":"operating_profit","당기순이익":"net_income","당기순이익(손실)":"net_income","당기순손실":"net_income","당기순손익":"net_income","자산총계":"assets","부채총계":"liabilities","자본총계":"equity","유동자산":"current_assets","유동부채":"current_liabilities","현금및현금성자산":"cash","영업활동현금흐름":"operating_cash_flow","영업활동으로인한현금흐름":"operating_cash_flow"}
def api(name,**params):
 for n in range(4):
  try:
   r=requests.get(API+name,params={"crtfc_key":KEY,**params},timeout=60);r.raise_for_status()
   if name.endswith(".json"):
    data=r.json()
    if data.get("status")=="013":return {}
    if data.get("status")!="000":raise ValueError(str(data))
    return data
   return r.content
  except (requests.RequestException,ValueError):
   if n==3:raise
   time.sleep(2**n)
def corp_code():
 with zipfile.ZipFile(io.BytesIO(api("corpCode.xml"))) as z:
  root=ET.fromstring(z.read(z.namelist()[0]))
 for row in root.findall("list"):
  if row.findtext("stock_code","").strip()=="041830":return row.findtext("corp_code")
 raise RuntimeError("InBody corp code not found")
def val(s):
 try:return int(str(s).replace(",",""))
 except (TypeError,ValueError):return None
def ratio(a,b):
 return round(a/b*100,2) if a is not None and b not in (None,0) else None
def collect(code,year,corp):
 for basis in ("CFS","OFS"):
  raw=api("fnlttSinglAcntAll.json",corp_code=corp,bsns_year=year,reprt_code=code,fs_div=basis)
  if not raw.get("list"):continue
  values={}
  for row in raw["list"]:
   name=row.get("account_nm","").replace(" ","")
   field=FIELDS.get(name)
   if not field:continue
   sj=row.get("sj_div")
   if field in ("revenue","operating_profit","net_income") and sj not in ("IS","CIS"):continue
   if field in ("assets","liabilities","equity","current_assets","current_liabilities","cash") and sj!="BS":continue
   if field=="operating_cash_flow" and sj!="CF":continue
   if row.get("account_detail") not in ("-","",None):continue
   number=val(row.get("thstrm_amount"))
   if number is not None and (field not in values or row.get("account_id","").startswith(("ifrs","ifrs-full"))):values[field]=number
  if values:return {"year":year,"report_code":code,"basis":basis,**values}
 return None
def enrich(row,annual=False):
 row["operating_margin"]=ratio(row.get("operating_profit"),row.get("revenue"))
 row["net_margin"]=ratio(row.get("net_income"),row.get("revenue"))
 row["debt_ratio"]=ratio(row.get("liabilities"),row.get("equity"))
 row["current_ratio"]=ratio(row.get("current_assets"),row.get("current_liabilities"))
 row["roa"]=ratio(row.get("net_income"),row.get("assets")) if annual else None
 row["roe"]=ratio(row.get("net_income"),row.get("equity")) if annual else None
 return row
def main():
 if not KEY:raise SystemExit("Missing DART_API_KEY secret")
 corp=corp_code();year_now=datetime.datetime.now(ZoneInfo("Asia/Seoul")).year
 by={}
 for year in range(2010,year_now+1):
  for period,code in (("Q1","11013"),("H1","11012"),("Q3","11014"),("FY","11011")):
   try:
    row=collect(code,year,corp)
    if row:by[year,period]=row
   except Exception as exc:print("Warning",year,period,exc,flush=True)
   time.sleep(.1)
 if not by:raise RuntimeError("No financial data retrieved; existing dashboard preserved")
 annual=[];half=[];quarter=[]
 flows=("revenue","operating_profit","net_income","operating_cash_flow")
 for (year,period),row in sorted(by.items()):
  r=enrich(dict(row,period=period),period=="FY")
  if period=="FY":annual.append(r)
  if period=="H1":half.append(r)
  prev={"Q1":None,"H1":"Q1","Q3":"H1","FY":"Q3"}[period]
  q=dict(row,period={"Q1":"Q1","H1":"Q2","Q3":"Q3","FY":"Q4"}[period])
  earlier=by.get((year,prev)) if prev else None
  if prev:
   for k in flows:
    q[k]=row[k]-earlier[k] if earlier and row.get(k) is not None and earlier.get(k) is not None and row["basis"]==earlier["basis"] else None
  quarter.append(enrich(q))
 out={"company":"인바디","stock_code":"041830","updated_at":datetime.datetime.now(ZoneInfo("Asia/Seoul")).isoformat(),"annual":annual,"half_year":half,"quarterly":quarter}
 target=ROOT/"docs"/"data.json";target.parent.mkdir(exist_ok=True)
 target.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
 print("Saved",len(annual),"annual",len(half),"half-year",len(quarter),"quarter")
if __name__=="__main__":main()
