# 6월 여행 캠페인 대시보드 업데이트

## 실행 전 필수: 프로세스 문서 로드

업데이트를 시작하기 **전에** 반드시 아래 파일을 Read 도구로 읽는다.
이 문서에는 데이터 소스별 트랩, 쿼리, 검증 방법이 모두 담겨 있다.

```
/Users/anderson/Documents/Claude/Projects/유입 프로젝트/june_campaign_대시보드_업데이트_프로세스.md
```

읽은 후 "프로세스 문서 확인 완료 — [주요 주의사항 2~3줄 요약]" 형태로 짧게 보고하고 다음 단계로 넘어간다.

---

## 업데이트 대상 파일

```
/Users/anderson/Documents/GitHub/socar-seo-dashboard/campaign/index.html
```

---

## Step 0: 현재 대시보드 상태 파악

index.html에서 아래 항목을 확인한다 (Read 도구):
1. 헤더에 표시된 현재 D{N} 날짜
2. sec-label에 표시된 데이터 범위
3. 각 KR 카드의 현재 수치
4. 예약 테이블 마지막 행 날짜

"현재 D{N}까지 반영됨, D{목표}로 업데이트 예정" 형태로 보고한다.

---

## Step 1: 업데이트 가능 여부 사전 확인

아래 4개를 병렬로 확인한다.

### 1-1. 광고비 테이블 (native_w##) 존재 여부
```sql
SELECT table_name
FROM `socar-data.temp_team_smkt.INFORMATION_SCHEMA.TABLES`
WHERE table_name LIKE 'paid_daily_report_final_native_w%'
ORDER BY table_name DESC LIMIT 5;
```
→ 최신 w##이 target 주차를 커버하면 광고비/ROAS 차트 업데이트 가능, 없으면 "집계 대기" 유지

### 1-2. soda_store 커버리지 확인 (target 날짜로 치환)
```sql
SELECT
  COUNT(DISTINCT v.reservation_id) AS soda_cnt,
  COUNT(DISTINCT r.id) AS tianjin_cnt,
  ROUND(COUNT(DISTINCT v.reservation_id) / COUNT(DISTINCT r.id) * 100, 1) AS coverage_pct
FROM `socar-data.tianjin_replica.reservation_info` r
LEFT JOIN `socar-data.soda_store.reservation_v2` v
  ON r.id = v.reservation_id
  AND v.date BETWEEN '{target_date}' AND DATE_ADD('{target_date}', INTERVAL 7 DAY)
WHERE DATE(r.created_at, 'Asia/Seoul') = '{target_date}'
  AND r.state NOT IN (7, 8)
  AND r.member_imaginary IN (0, 9);
```
→ 60% 이상이면 세그 테이블 업데이트 가능, 미만이면 합계만 업데이트

### 1-3. KR1 DLUV (target 날짜로 치환)
```sql
SELECT DATE(event_timestamp, 'Asia/Seoul') AS dt, COUNT(DISTINCT member_id) AS dluv
FROM `socar-data.socar_app.app_logs`
WHERE DATE(event_timestamp, 'Asia/Seoul') = '{target_date}'
  AND member_id IS NOT NULL AND member_id != 0
GROUP BY 1;
```

### 1-4. KR3 예약 생성 (target 날짜로 치환)
```sql
SELECT
  DATE(created_at, 'Asia/Seoul') AS dt,
  COUNT(*) AS created_cnt,
  ROUND(COUNT(*) * 0.87) AS completed_est
FROM `socar-data.tianjin_replica.reservation_info`
WHERE DATE(created_at, 'Asia/Seoul') = '{target_date}'
  AND state NOT IN (7, 8)
  AND member_imaginary IN (0, 9)
GROUP BY 1;
```

4개 결과를 표로 정리해 보고하고 "업데이트 가능 항목 / 대기 항목" 구분을 명확히 한다.

---

## Step 2: 섹션별 데이터 수집

사용자가 별도로 범위를 지정하지 않으면 **업데이트 가능한 모든 섹션**을 업데이트한다.

### 2-A. DA 소재 CTR
```sql
SELECT
  CASE
    WHEN LOWER(name) LIKE '%freedrive%' OR (LOWER(name) LIKE '%ev%' AND LOWER(name) NOT LIKE '%blacklabel%') THEN 'EV주행무료'
    WHEN LOWER(name) LIKE '%blacklabel%' AND LOWER(name) LIKE '%kv%' THEN 'KV 블랙라벨'
    WHEN LOWER(name) LIKE '%blacklabel%' THEN '블랙라벨'
    WHEN LOWER(name) LIKE '%coupon%' OR LOWER(name) LIKE '%raffle%' OR LOWER(name) LIKE '%rafl%' THEN '쿠폰/래플'
    WHEN LOWER(name) LIKE '%uniform%' OR LOWER(name) LIKE '%균일%' THEN '균일가'
    WHEN LOWER(name) LIKE '%oneway%' OR LOWER(name) LIKE '%편도%' THEN '편도'
    WHEN LOWER(name) LIKE '%kv%' THEN 'KV 전국'
    WHEN LOWER(name) LIKE '%default%' OR name IS NULL THEN '일반/default'
    ELSE '기타'
  END AS theme,
  SUM(impressions) AS imp,
  SUM(clicks) AS clk,
  ROUND(SAFE_DIVIDE(SUM(clicks), SUM(impressions)) * 100, 2) AS ctr_pct
FROM `socar-data.temp_team_smkt.paid_da_raw`
WHERE date BETWEEN '2026-06-16' AND '{target_date}'
  AND campaign_name LIKE '%6월여행%'
GROUP BY 1 HAVING imp > 10000
ORDER BY ctr_pct DESC;
```

### 2-B. CRM 인앱 CTR (CTAS — jobComplete:false가 반환되어도 기다렸다가 SELECT로 확인)
```sql
CREATE OR REPLACE TABLE `socar-data.temp_team_smkt.crm_trip2606_ctr` AS
WITH imp AS (
  SELECT campaign_name, COUNT(*) impressions
  FROM `socar-data.braze_currents.users_messages_inappmessage_impression`
  WHERE date BETWEEN '2026-06-17' AND '{target_date}'
    AND campaign_name LIKE '%6월여행캠페인%'
  GROUP BY 1
),
clk AS (
  SELECT campaign_name, COUNT(*) clicks
  FROM `socar-data.braze_currents.users_messages_inappmessage_click`
  WHERE date BETWEEN '2026-06-17' AND '{target_date}'
    AND campaign_name LIKE '%6월여행캠페인%'
  GROUP BY 1
)
SELECT i.campaign_name, i.impressions, COALESCE(c.clicks,0) clicks,
  ROUND(SAFE_DIVIDE(COALESCE(c.clicks,0),i.impressions)*100,1) ctr_pct
FROM imp i LEFT JOIN clk c USING(campaign_name);
```

CTAS 실행 후 (30초~2분 대기):
```sql
SELECT * FROM `socar-data.temp_team_smkt.crm_trip2606_ctr` ORDER BY impressions DESC;
```

### 2-C. 버티컬 매체
```sql
SELECT
  ad_partner,
  ROUND(SUM(cost)/10000, 0) AS cost_man,
  SUM(clicks) AS clk,
  SUM(install) AS install,
  SUM(signup) AS signup,
  SUM(reservation) AS resv
FROM `socar-data.temp_team_smkt.paid_da_raw`
WHERE date BETWEEN '2026-06-17' AND '{target_date}'
  AND ad_partner IN ('kakao_pay', 'myrealtrip', 'korail', 'triple', 'blind', 'wanted')
GROUP BY 1 ORDER BY cost_man DESC;
```

### 2-D. OOH 존클릭 (주 1회, 새 주차 완성 시만)
```sql
SELECT
  zone_name,
  EXTRACT(ISOWEEK FROM DATE(event_timestamp, 'Asia/Seoul')) AS iso_week,
  COUNT(DISTINCT member_id) AS uv
FROM `socar-data.socar_server_2.get_car_classes`
WHERE DATE(event_timestamp, 'Asia/Seoul') BETWEEN '2026-06-02' AND '{target_date}'
  AND zone_name IN ('부산역', '서울역', '강남고속터미널', '제주공항', '대구반월당', '부산지하철', '용산', '동대구역', '김포공항')
GROUP BY 1, 2 ORDER BY 1, 2;
```

### 2-E. DLUV 세그별 (target 날짜로 치환)
```sql
SELECT
  DATE(event_timestamp, 'Asia/Seoul') AS dt,
  seg,
  COUNT(DISTINCT al.member_id) AS dluv
FROM `socar-data.socar_app.app_logs` al
LEFT JOIN (
  SELECT DISTINCT member_id,
    CASE
      WHEN accumulate_used_count = 1 THEN '0회차'
      WHEN accumulate_used_count BETWEEN 2 AND 4 THEN '1-3회차'
      WHEN accumulate_used_count BETWEEN 5 AND 11 THEN '4-10회차'
      WHEN accumulate_used_count >= 12 THEN '11+회차'
    END AS seg
  FROM `socar-data.soda_store.reservation_v2`
  WHERE date >= '2026-01-01'
) seg_map USING(member_id)
WHERE DATE(event_timestamp, 'Asia/Seoul') = '{target_date}'
  AND al.member_id IS NOT NULL AND al.member_id != 0
GROUP BY 1, 2;
```

---

## Step 3: index.html 업데이트

수집한 데이터로 아래 순서대로 HTML을 수정한다.

1. 헤더 날짜: `{D(N-1)} 완료` → `{DN} 완료`
2. KR1 카드: DLUV, D8~D{N} avg, D1~D{N} avg, 달성률
3. KR3 카드: 완료추산건, 달성률
4. DLUV 테이블: 새 날짜 행 추가, avg/목표대비 행 재계산
5. 예약 테이블: 새 날짜 행 추가 (세그: soda_store ≥60%이면 표기, 미만이면 "—"), avg 행 업데이트
6. 소재 CTR 바 차트: 수치 및 날짜 범위 업데이트
7. CRM CTR 바 차트: 수치 및 날짜 범위 업데이트
8. 버티컬 테이블: 수치 및 날짜 범위 업데이트
9. OOH 바 차트: 새 주차 완성 시 W 비교 기준 업데이트
10. 브랜드검색: 새 주차 데이터 추가 (이상값 시 muted 처리)
11. SOV 각주: 최신 날짜로 업데이트
12. **모든 sec-label D{N-1} → D{N}** 동기화
13. 광고비/ROAS 차트: native_w## 있으면 업데이트, 없으면 "D{N} 광고 집계 대기" 유지

---

## Step 4: 최종 검증 (수정 후 필수)

아래 항목을 index.html에서 직접 확인한다.

```
[ ] KR1 D8~D{N} avg = DLUV 테이블 D8~D{N} avg 합계 (실데이터 Σ÷일수로 수동 계산 대조)
[ ] DLUV 테이블 D1~D{N} avg 합계 = KR1 카드 (BQ 직접값 우선)
[ ] 예약 테이블 sec-label "D1~D{N}" = DLUV 테이블 sec-label 일치
[ ] 액션플랜 sec-label "D{N} 기준" 동기화
[ ] CRM/소재/버티컬 날짜 범위 일치
```

불일치 발견 시 수정 후 재확인한다.

---

## Step 5: Git commit & push

```bash
cd /Users/anderson/Documents/GitHub/socar-seo-dashboard
git add campaign/index.html
git commit -m "chore(campaign): D{N}({날짜}) 대시보드 업데이트

[업데이트 항목 목록]

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
git pull --rebase && git push
```

완료 후 아래 형식으로 보고한다:

```
✅ D{N} 업데이트 완료
업데이트: [항목 목록]
대기: [집계 대기 항목 및 이유]
다음 업데이트 시 주의: [이번에 파악한 특이사항]
```
