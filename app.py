import os
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder='.')

SERVICE_KEY = "ETKBOKF9xHFHhXsGyF%2BgHEn5Rwh9SnHb5Eb7TYSCRQR7c8umeNTz9W8LP0U1IMXM6EwNPs3G51s8ruEGTRzigw%3D%3D"
DATA_FILE = "bid_records.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    records = load_data()
    return jsonify({"ok": True, "records": records})

@app.route('/api/fetch', methods=['POST'])
def fetch_g2b():
    req = request.get_json() or {}
    days = int(req.get('days', 30))
    if days > 30: days = 30
    
    end_date = datetime.now().strftime("%Y%m%d2359")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d0000")
    
    all_parsed = []
    
    for page in range(1, 6):
        url = (
            f"https://apis.data.go.kr/1230000/ad/BidPublicInfoService/getBidPblancListInfoServc"
            f"?serviceKey={SERVICE_KEY}"
            f"&numOfRows=100"
            f"&pageNo={page}"
            f"&inqryDiv=1"
            f"&inqryBgnDt={start_date}"
            f"&inqryEndDt={end_date}"
            f"&type=json"
        )
        
        try:
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
            if res.status_code != 200:
                break
                
            items = []
            try:
                res_json = res.json()
                body = res_json.get('response', {}).get('body', {})
                items_raw = body.get('items', [])
                if isinstance(items_raw, dict) and 'item' in items_raw:
                    items_raw = items_raw['item']
                items = items_raw if isinstance(items_raw, list) else ([items_raw] if isinstance(items_raw, dict) else [])
            except:
                root = ET.fromstring(res.text)
                items = root.findall('.//item')
                
            if not items:
                break
                
            for it in items:
                if isinstance(it, dict):
                    title = it.get('bidNtceNm', '')
                    org = it.get('ntceInsttNm') or '기관 미확인'
                    demand = it.get('dminsttNm', '')
                    bid_no = it.get('bidNtceNo', '')
                    bid_ord = str(it.get('bidNtceOrd', '00')).zfill(2)
                    notice_dt = it.get('bidNtceDt', '')
                    deadline = it.get('bidClseDt', '')
                    amt_raw = it.get('bdgtAmt') or it.get('presmptPrce') or 0
                    method = it.get('cntrctCnclsMthdNm', '')
                    api_url = it.get('bidNtceDtlUrl', '')
                else:
                    title = item.findtext('bidNtceNm', '')
                    org = item.findtext('ntceInsttNm', '') or '기관 미확인'
                    demand = item.findtext('dminsttNm', '')
                    bid_no = item.findtext('bidNtceNo', '')
                    bid_ord = str(item.findtext('bidNtceOrd', '00')).zfill(2)
                    notice_dt = item.findtext('bidNtceDt', '')
                    deadline = item.findtext('bidClseDt', '')
                    amt_raw = item.findtext('bdgtAmt') or item.findtext('presmptPrce') or '0'
                    method = item.findtext('cntrctCnclsMthdNm', '')
                    api_url = item.findtext('bidNtceDtlUrl', '')

                try: amt = int(float(amt_raw or 0))
                except: amt = 0
                
                # 나라장터 직링 주소 생성 (공고번호 + 차수 기반)
                if bid_no:
                    direct_url = f"https://www.g2b.go.kr:8081/ep/invitation/publish/bidInfoDtl.do?bidno={bid_no}&bidseq={bid_ord}"
                else:
                    direct_url = api_url or '#'

                full_text = f"{org} {demand} {title}"
                region = "OTHER"
                if any(k in full_text for k in ["서울", "강남", "종로", "마포", "영등포", "송파", "서초", "동작", "중구"]): region = "SEOUL"
                elif any(k in full_text for k in ["경기", "수원", "성남", "용인", "고양", "화성", "부천", "안양"]): region = "GYEONGGI"
                elif any(k in full_text for k in ["인천", "송도", "부평"]): region = "INCHEON"
                
                all_parsed.append({
                    "bidNo": f"{bid_no}-{bid_ord}" if bid_no else '',
                    "pureBidNo": bid_no,
                    "title": title,
                    "noticeDate": notice_dt,
                    "deadline": deadline,
                    "org": org,
                    "demandAgency": demand,
                    "amount": amt,
                    "contractMethod": method,
                    "region": region,
                    "url": direct_url
                })
        except Exception as e:
            print(f"[오류] {str(e)}")
            break

    unique_bids = list({x['bidNo']: x for x in all_parsed if x['bidNo']}.values())
    save_data(unique_bids)
    
    return jsonify({
        "ok": True, 
        "message": f"나라장터 공고 총 {len(unique_bids)}건 수집 완료!", 
        "count": len(unique_bids)
    })

if __name__ == '__main__':
    print("Server running on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
