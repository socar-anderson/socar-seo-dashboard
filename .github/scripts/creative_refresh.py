"""
컨텐츠 특공대 소재 성과 대시보드 — BigQuery 데이터 갱신 스크립트
실행: GitHub Actions (매일 10:03 KST)
출력: dashboard/creative-data.js
"""

import json
import os
from datetime import date
from google.cloud import bigquery
from google.oauth2 import service_account

# ── 인증 (Service Account Key — GCP_SA_KEY Secret) ────────────────────
sa_info = json.loads(os.environ["GCP_SA_KEY"])
credentials = service_account.Credentials.from_service_account_info(
    sa_info,
    scopes=["https://www.googleapis.com/auth/bigquery.readonly"],
)
client = bigquery.Client(credentials=credentials, project="socar-data")

TODAY = date.today().strftime("%Y-%m-%d")
QUERY_START = "2026-05-01"

print(f"[creative-refresh] 기준일: {TODAY}")

# ── CASE WHEN: paid_da_raw (name 컬럼) ───────────────────────────────
CASE_COST = """
    CASE
      WHEN REGEXP_CONTAINS(name, r'stressfree-2605') THEN 'stressfree'
      WHEN REGEXP_CONTAINS(name, r'diorama-2605_z2z_car_camping') THEN 'diorama-camping'
      WHEN REGEXP_CONTAINS(name, r'diorama-2605_z2z_car_jejuterminal') THEN 'diorama-jejuterminal'
      WHEN REGEXP_CONTAINS(name, r'diorama-2605_z2z_car_mart') THEN 'diorama-mart'
      WHEN REGEXP_CONTAINS(name, r'diorama-2605_z2z_car_season') THEN 'diorama-season'
      WHEN REGEXP_CONTAINS(name, r'blacklabel-2605') AND REGEXP_CONTAINS(name, r'palace') THEN 'blacklabel-palace'
      WHEN REGEXP_CONTAINS(name, r'blacklabel-2605') AND REGEXP_CONTAINS(name, r'parkinglot') THEN 'blacklabel-parkinglot'
      WHEN REGEXP_CONTAINS(name, r'blacklabel-2605') AND REGEXP_CONTAINS(name, r'pinlight') THEN 'blacklabel-pinlight'
      WHEN REGEXP_CONTAINS(name, r'blacklabel-2605') AND REGEXP_CONTAINS(name, r'drive') THEN 'blacklabel-drive'
      WHEN REGEXP_CONTAINS(name, r'sharing_al_blacklabel-2606_z2z_keyvisual_video_TF-carseat') THEN 'tf-blacklabel-kv'
      WHEN REGEXP_CONTAINS(name, r'sharing_al_nationwide-2606_z2z_car_video_TF-car') THEN 'tf-car-olive'
      WHEN REGEXP_CONTAINS(name, r'sharing_al_blacklabel-2606_z2z_car_video_TF-blacklabel') THEN 'tf-blacklabel-car'
      WHEN REGEXP_CONTAINS(name, r'sharing_al_delivery-2606_d2d_car_video_TF-delivery') THEN 'tf-delivery'
      WHEN REGEXP_CONTAINS(name, r'sharing_al_blacklabel-2606-movie_z2z_car_TF-Sketch') THEN 'tf-movie-sketch'
      WHEN REGEXP_CONTAINS(name, r'sharing_al_blacklabel-2606-movie_z2z_car_TF-Toy') THEN 'tf-movie-toy'
      WHEN REGEXP_CONTAINS(name, r'sharing_al_blacklabel-2606-movie_z2z_car_TF-bladerunner') THEN 'tf-movie-bladerunner'
      WHEN REGEXP_CONTAINS(name, r'sharing_al_blacklabel-2606-movie_z2z_car_TF-Minor') THEN 'tf-movie-minor'
      WHEN REGEXP_CONTAINS(name, r'sharing_al_blacklabel-2606-movie_z2z_car_TF-Gatsby') THEN 'tf-movie-gatsby'
    END
"""

# ── CASE WHEN: airbridge.app (Ad_Creative 컬럼) ───────────────────────
CASE_REV = """
    CASE
      WHEN REGEXP_CONTAINS(Ad_Creative, r'stressfree-2605') THEN 'stressfree'
      WHEN REGEXP_CONTAINS(Ad_Creative, r'diorama-2605_z2z_car_camping') THEN 'diorama-camping'
      WHEN REGEXP_CONTAINS(Ad_Creative, r'diorama-2605_z2z_car_jejuterminal') THEN 'diorama-jejuterminal'
      WHEN REGEXP_CONTAINS(Ad_Creative, r'diorama-2605_z2z_car_mart') THEN 'diorama-mart'
      WHEN REGEXP_CONTAINS(Ad_Creative, r'diorama-2605_z2z_car_season') THEN 'diorama-season'
      WHEN REGEXP_CONTAINS(Ad_Creative, r'blacklabel-2605') AND REGEXP_CONTAINS(Ad_Creative, r'palace') THEN 'blacklabel-palace'
      WHEN REGEXP_CONTAINS(Ad_Creative, r'blacklabel-2605') AND REGEXP_CONTAINS(Ad_Creative, r'parkinglot') THEN 'blacklabel-parkinglot'
      WHEN REGEXP_CONTAINS(Ad_Creative, r'blacklabel-2605') AND REGEXP_CONTAINS(Ad_Creative, r'pinlight') THEN 'blacklabel-pinlight'
      WHEN REGEXP_CONTAINS(Ad_Creative, r'blacklabel-2605') AND REGEXP_CONTAINS(Ad_Creative, r'drive') THEN 'blacklabel-drive'
      WHEN REGEXP_CONTAINS(Ad_Creative, r'sharing_al_blacklabel-2606_z2z_keyvisual_video_TF-carseat') THEN 'tf-blacklabel-kv'
      WHEN REGEXP_CONTAINS(Ad_Creative, r'sharing_al_nationwide-2606_z2z_car_video_TF-car') THEN 'tf-car-olive'
      WHEN REGEXP_CONTAINS(Ad_Creative, r'sharing_al_blacklabel-2606_z2z_car_video_TF-blacklabel') THEN 'tf-blacklabel-car'
      WHEN REGEXP_CONTAINS(Ad_Creative, r'sharing_al_delivery-2606_d2d_car_video_TF-delivery') THEN 'tf-delivery'
      WHEN REGEXP_CONTAINS(Ad_Creative, r'sharing_al_blacklabel-2606-movie_z2z_car_TF-Sketch') THEN 'tf-movie-sketch'
      WHEN REGEXP_CONTAINS(Ad_Creative, r'sharing_al_blacklabel-2606-movie_z2z_car_TF-Toy') THEN 'tf-movie-toy'
      WHEN REGEXP_CONTAINS(Ad_Creative, r'sharing_al_blacklabel-2606-movie_z2z_car_TF-bladerunner') THEN 'tf-movie-bladerunner'
      WHEN REGEXP_CONTAINS(Ad_Creative, r'sharing_al_blacklabel-2606-movie_z2z_car_TF-Minor') THEN 'tf-movie-minor'
      WHEN REGEXP_CONTAINS(Ad_Creative, r'sharing_al_blacklabel-2606-movie_z2z_car_TF-Gatsby') THEN 'tf-movie-gatsby'
    END
"""

FILTER_COST = r"REGEXP_CONTAINS(name, r'stressfree-2605|diorama-2605_z2z_car|blacklabel-2605.*(palace|parkinglot|pinlight|drive)|sharing_al_blacklabel-2606_z2z_keyvisual_video_TF-carseat|sharing_al_nationwide-2606_z2z_car_video_TF-car|sharing_al_blacklabel-2606_z2z_car_video_TF-blacklabel|sharing_al_delivery-2606_d2d_car_video_TF-delivery|sharing_al_blacklabel-2606-movie_z2z_car_TF-(Sketch|Toy|bladerunner|Minor|Gatsby)')"
FILTER_REV  = r"REGEXP_CONTAINS(Ad_Creative, r'stressfree-2605|diorama-2605_z2z_car|blacklabel-2605.*(palace|parkinglot|pinlight|drive)|sharing_al_blacklabel-2606_z2z_keyvisual_video_TF-carseat|sharing_al_nationwide-2606_z2z_car_video_TF-car|sharing_al_blacklabel-2606_z2z_car_video_TF-blacklabel|sharing_al_delivery-2606_d2d_car_video_TF-delivery|sharing_al_blacklabel-2606-movie_z2z_car_TF-(Sketch|Toy|bladerunner|Minor|Gatsby)')"

# ── Query A: 소재별 ROAS·매출·비용·건수 ────────────────────────────────
QUERY_A = f"""
WITH daily_cost AS (
  SELECT date,
    {CASE_COST} AS creative,
    SUM(cost) AS cost
  FROM `socar-data.temp_team_smkt.paid_da_raw`
  WHERE date BETWEEN '{QUERY_START}' AND '{TODAY}'
    AND {FILTER_COST}
  GROUP BY date, creative
),
daily_rev AS (
  SELECT Date AS date,
    {CASE_REV} AS creative,
    SUM(Event_Value) AS mmp_value,
    COUNT(*) AS mmp_cnt
  FROM `socar-data.airbridge.app`
  WHERE Date BETWEEN '{QUERY_START}' AND '{TODAY}'
    AND {FILTER_REV}
    AND REGEXP_CONTAINS(Event_Name, r'completed_.+reservation_s')
    AND Event_Value IS NOT NULL
  GROUP BY date, creative
)
SELECT
  c.creative,
  FORMAT_DATE('%Y-%m-%d', MIN(c.date))  AS first_date,
  FORMAT_DATE('%Y-%m-%d', MAX(c.date))  AS last_date,
  DATE_DIFF(MAX(c.date), MIN(c.date), DAY) + 1 AS days,
  ROUND(SUM(c.cost) / 10000, 1)                  AS cost_man,
  COALESCE(SUM(r.mmp_cnt), 0)                     AS mmp_cnt,
  ROUND(COALESCE(SUM(r.mmp_value), 0) / 10000, 0) AS mmp_value_man,
  ROUND(SAFE_DIVIDE(SUM(r.mmp_value), SUM(c.cost)) * 100, 0) AS roas_pct,
  ROUND(SAFE_DIVIDE(SUM(r.mmp_value), SUM(r.mmp_cnt)), 0)    AS value_per_cnt
FROM daily_cost c
LEFT JOIN daily_rev r ON c.date = r.date AND c.creative = r.creative
WHERE c.creative IS NOT NULL
GROUP BY c.creative
ORDER BY roas_pct DESC
"""

# ── Query B: 소재별 매체 비중 (CTE로 윈도우 함수 오류 방지) ──────────────
QUERY_B = f"""
WITH base AS (
  SELECT
    {CASE_COST} AS creative,
    ad_partner,
    SUM(cost) AS cost
  FROM `socar-data.temp_team_smkt.paid_da_raw`
  WHERE date BETWEEN '{QUERY_START}' AND '{TODAY}'
    AND {FILTER_COST}
  GROUP BY creative, ad_partner
  HAVING creative IS NOT NULL
)
SELECT
  creative,
  ad_partner,
  ROUND(cost / SUM(cost) OVER (PARTITION BY creative) * 100, 0) AS cost_pct
FROM base
ORDER BY creative, cost_pct DESC
"""

# ── BQ 실행 ───────────────────────────────────────────────────────────
print("[creative-refresh] Query A 실행 중...")
rows_a = list(client.query(QUERY_A).result())
print(f"  → {len(rows_a)}개 소재")

print("[creative-refresh] Query B 실행 중...")
rows_b = list(client.query(QUERY_B).result())
print(f"  → {len(rows_b)}개 행")

# ── 결과 파싱 ─────────────────────────────────────────────────────────
metrics = {r.creative: dict(r) for r in rows_a}

PARTNER_MAP = {
    "tiktok": ("TikTok", "tt"),
    "facebook": ("Facebook", "fb"),
    "meta": ("Facebook", "fb"),
    "moloco": ("Moloco", ""),
}
media_map = {}
for r in rows_b:
    cid = r.creative
    if cid not in media_map:
        media_map[cid] = []
    partner_lower = (r.ad_partner or "").lower()
    name, cls = next(
        ((n, c) for k, (n, c) in PARTNER_MAP.items() if k in partner_lower),
        (r.ad_partner, ""),
    )
    pct = int(r.cost_pct or 0)
    if pct > 0:
        media_map[cid].append({"name": name, "cls": cls, "pct": pct})

# ── 소재 메타 정의 ────────────────────────────────────────────────────
GROUPS_ORDER = ["diorama-2605", "blacklabel-2605", "stressfree-2605", "tf-2606"]

CREATIVE_ORDER = [
    "diorama-jejuterminal", "diorama-mart", "diorama-season", "diorama-camping",
    "blacklabel-palace", "blacklabel-drive", "blacklabel-pinlight", "blacklabel-parkinglot",
    "stressfree",
    "tf-blacklabel-kv", "tf-car-olive", "tf-blacklabel-car", "tf-delivery",
    "tf-movie-gatsby", "tf-movie-toy", "tf-movie-sketch", "tf-movie-bladerunner", "tf-movie-minor",
]

GROUP_OF = {
    "diorama-jejuterminal": "diorama-2605",
    "diorama-mart": "diorama-2605",
    "diorama-season": "diorama-2605",
    "diorama-camping": "diorama-2605",
    "blacklabel-palace": "blacklabel-2605",
    "blacklabel-drive": "blacklabel-2605",
    "blacklabel-pinlight": "blacklabel-2605",
    "blacklabel-parkinglot": "blacklabel-2605",
    "stressfree": "stressfree-2605",
    "tf-blacklabel-kv": "tf-2606",
    "tf-car-olive": "tf-2606",
    "tf-blacklabel-car": "tf-2606",
    "tf-delivery": "tf-2606",
    "tf-movie-gatsby": "tf-2606",
    "tf-movie-toy": "tf-2606",
    "tf-movie-sketch": "tf-2606",
    "tf-movie-bladerunner": "tf-2606",
    "tf-movie-minor": "tf-2606",
}

NAME_OF = {
    "diorama-jejuterminal": "jejuterminal",
    "diorama-mart": "mart",
    "diorama-season": "season",
    "diorama-camping": "camping",
    "blacklabel-palace": "palace",
    "blacklabel-drive": "drive",
    "blacklabel-pinlight": "pinlight",
    "blacklabel-parkinglot": "parkinglot",
    "stressfree": "stressfree",
    "tf-blacklabel-kv": "blacklabel_kv",
    "tf-car-olive": "car_olive",
    "tf-blacklabel-car": "blacklabel_car",
    "tf-delivery": "delivery",
    "tf-movie-gatsby": "movie_gatsby",
    "tf-movie-toy": "movie_toy",
    "tf-movie-sketch": "movie_sketch",
    "tf-movie-bladerunner": "movie_bladerunner",
    "tf-movie-minor": "movie_minor",
}

BADGE_DEFAULTS = {
    "diorama-jejuterminal": "최고 효율",
    "diorama-mart": "양호",
    "diorama-season": "양호",
    "diorama-camping": "모니터링",
    "blacklabel-palace": "모니터링",
    "blacklabel-drive": "볼륨 1위",
    "blacklabel-pinlight": "모니터링",
    "blacklabel-parkinglot": "중단 · 참고용",
    "stressfree": "양호",
    "tf-blacklabel-kv": "양호",
    "tf-car-olive": "모니터링",
    "tf-blacklabel-car": "모니터링",
    "tf-delivery": "모니터링",
    "tf-movie-gatsby": "양호",
    "tf-movie-toy": "양호",
    "tf-movie-sketch": "모니터링",
    "tf-movie-bladerunner": "모니터링",
    "tf-movie-minor": "양호",
}

MEDIA_NOTES = {"stressfree": "(TT 5/27 중단)"}

# ── summary 계산 ──────────────────────────────────────────────────────
total_cost = sum(v.get("cost_man", 0) for v in metrics.values())
total_rev  = sum(v.get("mmp_value_man", 0) for v in metrics.values())
total_cnt  = sum(v.get("mmp_cnt", 0) for v in metrics.values())
blend_roas = round(total_rev / total_cost * 100) if total_cost else 0

# ── creative-data.js 생성 ──────────────────────────────────────────────
creatives_js = []
for cid in CREATIVE_ORDER:
    m = metrics.get(cid, {})
    entry = {
        "id": cid,
        "name": NAME_OF.get(cid, cid),
        "group": GROUP_OF.get(cid, ""),
        "badge": BADGE_DEFAULTS.get(cid, ""),
        "roas": int(m.get("roas_pct") or 0),
        "revenueMan": int(m.get("mmp_value_man") or 0),
        "costMan": float(m.get("cost_man") or 0),
        "cnt": int(m.get("mmp_cnt") or 0),
        "valuePerCnt": int(m.get("value_per_cnt") or 0),
        "firstDate": m.get("first_date", ""),
        "lastDate": m.get("last_date", ""),
        "days": int(m.get("days") or 0),
        "media": media_map.get(cid, []),
    }
    if cid in MEDIA_NOTES:
        entry["mediaNote"] = MEDIA_NOTES[cid]
    creatives_js.append(entry)

data = {
    "meta": {
        "lastUpdated": TODAY,
        "queryStart": QUERY_START,
        "queryEnd": TODAY,
    },
    "summary": {
        "totalCostMan": round(total_cost, 1),
        "totalRevenueMan": int(total_rev),
        "blendRoas": blend_roas,
        "totalCnt": int(total_cnt),
    },
    "groups": GROUPS_ORDER,
    "creatives": creatives_js,
}

script_dir = os.path.dirname(os.path.abspath(__file__))
data_js_path = os.path.normpath(os.path.join(script_dir, "..", "..", "dashboard", "creative-data.js"))

js_content = (
    f"// auto-generated by creative refresh\n"
    f"// last_updated: {TODAY}\n\n"
    f"const CREATIVE_DATA = {json.dumps(data, ensure_ascii=False, indent=2)};\n"
)

with open(data_js_path, "w", encoding="utf-8") as f:
    f.write(js_content)

print(f"[creative-refresh] creative-data.js 업데이트 완료 ({data_js_path})")
print(f"  총 집행금액: {total_cost:,.1f}만원 | 총 매출: {total_rev:,.0f}만원 | ROAS: {blend_roas:,}%")
