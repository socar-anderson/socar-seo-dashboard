# 컨텐츠 특공대 소재 성과 대시보드 자동 갱신

## 목적
매일 BigQuery에서 최신 소재 성과 데이터를 조회하고
`/Users/anderson/Documents/GitHub/socar-seo-dashboard/dashboard/creative-data.js`를 업데이트한 뒤
GitHub에 푸시한다.

---

## Step 1: BigQuery 쿼리 실행

아래 두 쿼리를 BigQuery MCP (`mcp__claude_ai_socar-data-bigquery-mcp__execute_sql_readonly`)로 실행한다.
`TODAY`는 오늘 날짜(YYYY-MM-DD)로 치환한다.

### Query A — 소재별 ROAS·매출·비용·건수

```sql
WITH daily_cost AS (
  SELECT date,
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
    END AS creative,
    SUM(cost) AS cost
  FROM `socar-data.temp_team_smkt.paid_da_raw`
  WHERE date BETWEEN '2026-05-01' AND 'TODAY'
    AND REGEXP_CONTAINS(name, r'stressfree-2605|diorama-2605_z2z_car|blacklabel-2605.*(palace|parkinglot|pinlight|drive)|sharing_al_blacklabel-2606_z2z_keyvisual_video_TF-carseat|sharing_al_nationwide-2606_z2z_car_video_TF-car|sharing_al_blacklabel-2606_z2z_car_video_TF-blacklabel|sharing_al_delivery-2606_d2d_car_video_TF-delivery')
  GROUP BY date, creative
),
daily_rev AS (
  SELECT Date AS date,
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
    END AS creative,
    SUM(Event_Value) AS mmp_value,
    COUNT(*) AS mmp_cnt
  FROM `socar-data.airbridge.app`
  WHERE Date BETWEEN '2026-05-01' AND 'TODAY'
    AND REGEXP_CONTAINS(Ad_Creative, r'stressfree-2605|diorama-2605_z2z_car|blacklabel-2605.*(palace|parkinglot|pinlight|drive)|sharing_al_blacklabel-2606_z2z_keyvisual_video_TF-carseat|sharing_al_nationwide-2606_z2z_car_video_TF-car|sharing_al_blacklabel-2606_z2z_car_video_TF-blacklabel|sharing_al_delivery-2606_d2d_car_video_TF-delivery')
    AND REGEXP_CONTAINS(Event_Name, r'completed_.+reservation_s')
    AND Event_Value IS NOT NULL
  GROUP BY date, creative
)
SELECT
  c.creative,
  MIN(c.date) AS first_date,
  MAX(c.date) AS last_date,
  DATE_DIFF(MAX(c.date), MIN(c.date), DAY) + 1 AS days,
  ROUND(SUM(c.cost) / 10000, 1) AS cost_man,
  COALESCE(SUM(r.mmp_cnt), 0) AS mmp_cnt,
  ROUND(COALESCE(SUM(r.mmp_value), 0) / 10000, 0) AS mmp_value_man,
  ROUND(SAFE_DIVIDE(SUM(r.mmp_value), SUM(c.cost)) * 100, 0) AS roas_pct,
  ROUND(SAFE_DIVIDE(SUM(r.mmp_value), SUM(r.mmp_cnt)), 0) AS value_per_cnt
FROM daily_cost c
LEFT JOIN daily_rev r ON c.date = r.date AND c.creative = r.creative
WHERE c.creative IS NOT NULL
GROUP BY c.creative
ORDER BY roas_pct DESC
```

### Query B — 소재별 매체 비중

```sql
SELECT
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
  END AS creative,
  ad_partner,
  ROUND(SUM(cost) / SUM(SUM(cost)) OVER (PARTITION BY
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
    END
  ) * 100, 0) AS cost_pct
FROM `socar-data.temp_team_smkt.paid_da_raw`
WHERE date BETWEEN '2026-05-01' AND 'TODAY'
  AND REGEXP_CONTAINS(name, r'stressfree-2605|diorama-2605_z2z_car|blacklabel-2605.*(palace|parkinglot|pinlight|drive)|sharing_al_blacklabel-2606_z2z_keyvisual_video_TF-carseat|sharing_al_nationwide-2606_z2z_car_video_TF-car|sharing_al_blacklabel-2606_z2z_car_video_TF-blacklabel|sharing_al_delivery-2606_d2d_car_video_TF-delivery')
GROUP BY creative, ad_partner
HAVING creative IS NOT NULL
ORDER BY creative, cost_pct DESC
```

---

## Step 2: creative-data.js 업데이트

쿼리 결과를 바탕으로 아래 파일을 덮어쓴다.

파일 경로: `/Users/anderson/Documents/GitHub/socar-seo-dashboard/dashboard/creative-data.js`

- `meta.lastUpdated` → 오늘 날짜
- `meta.queryEnd` → 오늘 날짜
- 각 소재의 `roas`, `revenueMan`, `costMan`, `cnt`, `valuePerCnt`, `firstDate`, `lastDate`, `days` → Query A 결과
- 각 소재의 `media` 배열 → Query B 결과 (ad_partner → cls 매핑: 틱톡→`tt`, 페이스북→`fb`)
- `summary` 전체 합산: `totalCostMan`, `totalRevenueMan`, `blendRoas`, `totalCnt` → Query A 전체 합 계산

badge는 기존 값 유지 (수정 금지).
mediaNote는 기존 값 유지.
groups 배열 순서 유지: `["diorama-2605", "blacklabel-2605", "stressfree-2605", "tf-2606"]`.

소재 ID → creative-data.js 매핑:
- `diorama-jejuterminal`, `diorama-mart`, `diorama-season`, `diorama-camping` → group: diorama-2605
- `blacklabel-palace`, `blacklabel-drive`, `blacklabel-pinlight`, `blacklabel-parkinglot` → group: blacklabel-2605
- `stressfree` → group: stressfree-2605
- `tf-blacklabel-kv` (name: blacklabel_kv) → group: tf-2606, 집계 시작: 2026-06-16
- `tf-car-olive` (name: car_olive) → group: tf-2606, 집계 시작: 2026-06-23
- `tf-blacklabel-car` (name: blacklabel_car) → group: tf-2606, 집계 시작: 2026-07-01
- `tf-delivery` (name: delivery) → group: tf-2606, 집계 시작: 2026-07-01

---

## Step 3: Git commit & push

```bash
cd /Users/anderson/Documents/GitHub/socar-seo-dashboard
git add dashboard/creative-data.js
git commit -m "auto: creative dashboard refresh $(date +%Y-%m-%d)"
git push origin main
```

완료 후 "컨텐츠 특공대 대시보드 갱신 완료 — [날짜]" 메시지를 출력한다.
