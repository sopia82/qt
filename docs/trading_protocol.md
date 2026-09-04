# [Q-TAP v2.0] Quantum-grade Trading Analysis Protocol
### 미국 S&P 500 및 한국 KOSPI 100 듀얼-호라이즌 자동 분석 명세서

---

## 1. 개요 (Architecture Overview)
본 프로토콜은 거시경제·정치적 리스크(Gate 0)부터 시장 전체 추세(Gate 1), 듀얼-호라이즌 종목 스코어링(Gate 2), 기술적 타이밍 트리거(Gate 3), 동적 리스크 관리(Gate 4)까지 유기적으로 연결된 5단계 게이트키퍼 모델입니다.

```
[데이터 파이프라인]
  ├─ Macro (VIX, 10Y Yield, DXY, USDKRW, WTI, FRED)
  ├─ US S&P 500 (OHLCV, Volume, Valuation, Quality)
  ├─ KR KOSPI 100 (OHLCV, Foreigner/Institutional Flow)
  └─ News & Calendar (FOMC/CPI Blackout, Sentiment)
          │
          ▼
[Gate 0] 정치·거시 리스크 & 이벤트 블랙아웃 판정 (EPU, GPR, Surprise)
          │  Pass
          ▼
[Gate 1] 시장 레짐 필터 (S&P 500 / KOSPI 200일선 & VIX 밴드)
          │  Pass
          ▼
[Gate 2] 듀얼-호라이즌 스코어링
  ├─ [중장기 3M~1Y]: Quality(30%) + Value(20%) + Growth(25%) + Revision(25%)
  └─ [단기 1D~2W]: 거래대금 2.5배 폭증 + 외인/기관 쌍끌이 + 변동성 스퀴즈
          │
          ▼
[Gate 3] 정밀 진입 타이밍 산출
  ├─ [중장기]: 주봉 지지선(20주선) 지지 + 눌림목 반등
  └─ [단기]: 일중 VWAP 상향 돌파 + 체결강도 130%+ + RSI(14) 50 돌파
          │
          ▼
[Gate 4] 동적 리스크 관리 및 포지션 사이징
  ├─ [중장기]: Max 15% 비중, 손절 -7~8%, 트레일링 스탑
  └─ [단기]: Max 5% 비중, 손절 -2.5~3.5%, 5일 타임스탑
          │
          ▼
[출력/알림] 텔레그램 스마트폰 실시간 전송 & 콘솔 종합 리포트
```

---

## 2. 세부 게이트 규약 (Gate Specifications)

### Gate 0: 정치·거시 리스크 및 이벤트 블랙아웃
1. **Tier 1 경제지표 블랙아웃 (FOMC, US CPI, NFP)**:
   - 발표 전 24시간 ~ 발표 후 30분 동안 모든 단기 신규 매수 금지.
2. **거시 변동성 임계치**:
   - VIX > 28 또는 VKOSPI > 25: 신규 롱 진입 전면 중단 (현금 보유).
   - 미국 10년물 국채 금리 급등(주간 +15bps 이상): 기술 성장주 진입 제한.
   - 원/달러 환율 급등(주간 +2% 이상): KOSPI 100 외국인 이탈 경보 발동.

### Gate 1: 시장 국면 필터 (Market Regime)
- **S&P 500 (미국)**: 현재 종가 > 200일 단순이동평균(SMA) & 50일 SMA > 200일 SMA.
- **KOSPI (한국)**: 현재 종가 > 120일 단순이동평균(SMA) & 20일 거래대금 유지.
- 국면이 '하락장(Bear)'으로 분류되면 포트폴리오 현금 비중 70% 이상 강제.

### Gate 2: 듀얼-호라이즌 스코어링 (Screening)
- **중장기(Strategic)**:
  - ROE > 12%, 부채비율 < 120%, 영업현금흐름 > 0 (Quality)
  - Forward PER/PBR 과거 3개년 하위 40% (Value)
  - 분기 매출 YoY > 8% (Growth)
- **단기(Tactical)**:
  - 당일 거래대금 > 20일 평균 거래대금의 250%
  - 한국: 외국인 + 기관 순매수 대금 동시 유입 (쌍끌이)
  - 볼린저 밴드(20, 2) 대역폭이 최근 60일 최저치 근방 수축 후 팽창

### Gate 3: 정밀 진입 타이밍 (Timing Trigger)
- **단기**: 당일 주가 > VWAP(거래량 가중평균가) AND RSI(14) 50~65 구간 AND 직전 30분봉 고점 돌파.
- **중장기**: 주봉 20선 지지 또는 52주 고점 대비 -10%~-18% 건강한 조정 구간에서 수급 반등 포착.

### Gate 4: 리스크 관리 & 포지션 사이징
- **Kelly Criterion / Volatility Parity** 적용:
  $$\text{포지션 크기} = \frac{\text{목표 변동성(10\%)}}{\text{종목 ATR(14) 변동성}} \times \text{계좌 총자산}$$
- 단기 종목 최대 4개 (종목당 5%), 중장기 종목 최대 8개 (종목당 10~15%).
