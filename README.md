[![🔗 대시보드 바로가기](https://img.shields.io/badge/%F0%9F%94%97-%EB%8C%80%EC%8B%9C%EB%B3%B4%EB%93%9C_%EB%B0%94%EB%A1%9C%EA%B0%80%EA%B8%B0-149e95?style=for-the-badge)](https://hsc-class01.github.io/KTH-inbody/)

# 인바디 DART Financial Agent

인바디(041830)의 DART 사업보고서, 반기보고서, 분기보고서에서 2010년부터 가능한 재무자료를 수집·분석하고 GitHub Pages에서 시각화합니다.

## 최초 설치
1. [OpenDART](https://opendart.fss.or.kr/)에서 API 인증키 발급.
2. GitHub 저장소 **Settings → Secrets and variables → Actions → New repository secret** 에서 이름 `DART_API_KEY`, 값은 발급받은 키를 등록. API 키를 소스코드에 적지 마세요.
3. Settings → Actions → General에서 워크플로우의 저장소 쓰기 권한(Contents: write)을 허용합니다.
4. Actions → **Update InBody DART financials** → **Run workflow**로 최초 수집.
5. Settings → Pages → Deploy from a branch → `main` / `docs` → Save.
6. 저장소 우측 About → 톱니바퀴 → Website에 `https://hsc-class01.github.io/KTH-inbody/` 입력.

## 업데이트
GitHub Actions는 매일 UTC 15:17에 호출되지만 한국시간 매월 **1일 00:17**에만 수집합니다. 최초 수동 실행은 날짜 조건을 건너뜁니다. 예약 작업은 GitHub 사정으로 지연될 수 있습니다.

## 수치와 결측
- Annual: 사업보고서, Half-year: 반기 누적, Quarterly: Q1 원본 / Q2·Q3·Q4 누적 실적 차감.
- 재무상태표는 분기말 시점 금액이고 손익/현금흐름은 기간 실적입니다. 연결(CFS) 우선, 없으면 별도(OFS) 사용. 연결·별도 간 차감은 하지 않습니다.
- 지표: 매출, 영업이익, 순이익, 자산, 부채, 자본, 유동자산, 유동부채, 현금, 영업현금흐름, 영업/순이익률, 부채/유동비율, ROA/ROE.
- DART 전체 재무제표 API는 과거 2010~2014년 자료를 제공하지 않을 수 있습니다. 없는 자료를 추정하지 않습니다. ROA/ROE는 기말 잔액을 사용한 간이 비율입니다.
- 실제 수집에 실패한 경우 기존 대시보드 데이터를 덮어쓰지 않습니다.

## 국내 Peer Firms (참고)
| 회사 | 종목코드 | 사업 유사성 | 차이 |
|---|---|---|---|
| 셀바스헬스케어 | 208370 | 건강측정·의료기기 | 제품 포트폴리오 상이 |
| 비스토스 | 419540 | 생체신호 측정기기 | 체성분 중심 아님 |
| 휴비츠 | 065510 | 측정·진단 의료기기 | 안과 중심 |

Peer 업체의 재무정보 자동 수집은 본 버전에 포함되지 않았습니다.

## 구성
`agent.py`: DART 재무데이터 수집 · `docs/index.html`: 대시보드 · `docs/data.json`: 수집 결과 · `.github/workflows/update.yml`: 정기 실행.
