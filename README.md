# Quant Research Portfolio

คลังโปรเจคสำหรับจำลองกลยุทธ์การลงทุนเชิงปริมาณ (Quantitative Trading) ที่พร้อมนำไปใช้งานจริง

โปรเจคนี้ประกอบไปด้วยกลยุทธ์และเครื่องมือทางการเงินเชิงปริมาณ 5 ตัว ที่ครอบคลุมตั้งแต่การจำลองความเสี่ยง การเทรดตามเทรนด์ การจัดพอร์ตการลงทุน ไปจนถึงการทำ Statistical Arbitrage

## โปรเจคในคลัง

1. Monte Carlo GBM Simulator - จำลองราคาสินทรัพย์ด้วย Geometric Brownian Motion และคำนวณ Value at Risk (VaR)
2. EWMA Crossover - กลยุทธ์ใช้ Exponential Moving Average 2 เส้น พร้อม Grid Search เพื่อหาค่าที่เหมาะสมที่สุด
3. Efficient Frontier Optimizer - สร้างเส้นเขตประสิทธิภาพและหาน้ำหนักพอร์ตที่ให้ Sharpe Ratio สูงสุด
4. Sharpe Ratio Dashboard - Web App แบบโต้ตอบสำหรับแสดงผล Efficient Frontier และ Performance Metrics
5. Mean Reversion Pairs Bot - กลยุทธ์ Statistical Arbitrage โดยใช้ Cointegration และ Z-score

## โครงสร้างโปรเจค

quant-research/
├── README.md                 # เอกสารอธิบายโปรเจคหลัก
├── requirements.txt          # รายการ Libraries ที่ต้องติดตั้ง
├── src/                      # โมดูลหลักที่นำกลับมาใช้ใหม่ได้
│   ├── data_fetcher.py       # ดึงข้อมูลจาก Yahoo Finance พร้อมระบบ Cache
│   └── portfolio_optimizer.py # คำนวณ Efficient Frontier และ Portfolio Optimization
└── projects/                 # โปรเจคย่อยตามประเภท
    ├── 01_monte_carlo/
    │   └── simulator.py      # จำลอง GBM และคำนวณ VaR
    ├── 02_ewma_crossover/
    │   ├── strategy.py       # กลยุทธ์หลัก EWMA Crossover
    │   └── grid_search.py    # ค้นหาค่า Span ที่ดีที่สุด
    ├── 03_dashboard/
    │   └── app.py            # Streamlit Dashboard
    └── 04_pairs_bot/
        └── bot.py            # Pairs Trading Bot แบบ Mean Reversion

## การติดตั้ง

1. โคลนโปรเจค:
   git clone https://github.com/nakhareid99-dot/quant-research.git
   cd quant-research

2. ติดตั้ง Libraries:
   pip install -r requirements.txt

## วิธีการใช้งาน

1. เปิดใช้งาน Dashboard (Web App):
   streamlit run projects/03_dashboard/app.py

2. ทดสอบกลยุทธ์ EWMA (บน Colab หรือ Jupyter):
   from projects.02_ewma_crossover.strategy import generate_signals, backtest
   from src.data_fetcher import DataFetcher
   df = DataFetcher.get_stock_data('AAPL')
   df_signal = generate_signals(df, fast_span=10, slow_span=30)
   result = backtest(df_signal)
   print(result['sharpe_ratio'])

3. จำลอง Monte Carlo:
   from projects.01_monte_carlo.simulator import run_simulation
   df_paths = run_simulation(S0=100, n_sims=10000)
   print(f"ราคาเฉลี่ยปลายปี: {df_paths.iloc[-1].mean():.2f}")

4. รัน Pairs Trading Bot:
   from projects.04_pairs_bot.bot import run_pairs_bot
   result = run_pairs_bot(ticker1='AAPL', ticker2='MSFT', start='2020-01-01')

## การพัฒนาในอนาคต

- เพิ่มระบบ Backtesting แบบเต็มรูปแบบ (Transaction Cost, Slippage)
- รองรับการเทรด Cryptocurrency และหุ้นต่างประเทศ
- เพิ่ม Machine Learning (LSTM, XGBoost) สำหรับทำนายราคา
- สร้างระบบแจ้งเตือน Signal ผ่าน Telegram/Line
