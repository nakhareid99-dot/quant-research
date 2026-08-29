# Mean Reversion Pairs Trading Bot

กลยุทธ์เทรดแบบ Statistical Arbitrage ที่อาศัยแนวคิดราคาจะกลับสู่ค่าเฉลี่ย (Mean Reversion)

## ทฤษฎีเบื้องหลัง

- Cointegration: หาคู่หุ้นที่มีความสัมพันธ์กันในระยะยาว แม้ราคาจะแกว่ง แต่ Spread จะนิ่ง
- Hedge Ratio: คำนวณด้วย OLS (Ordinary Least Squares) เพื่อกำหนดอัตราส่วนในการซื้อขาย
- Z-score: ใช้เป็นสัญญาณเข้า/ออก เมื่อ Z-score > 2 (Over-spread) => ขาย, Z-score < -2 (Under-spread) => ซื้อ

## วิธีการเรียกใช้งาน

from bot import run_pairs_bot

ทดสอบคู่ AAPL กับ MSFT
result = run_pairs_bot(ticker1='AAPL', ticker2='MSFT', start='2021-01-01')

ปรับ Lookback Period (ค่าเริ่มต้นคือ 60 วัน)
result = run_pairs_bot(ticker1='AAPL', ticker2='MSFT', lookback=90)

## ตัวอย่าง Output

Hedge Ratio: 0.4523
Cointegration p-value: 0.0234

ผลลัพธ์ Pairs Trading Bot
========================================
Total Return: 12.34%
Sharpe Ratio: 1.85
Max Drawdown: -8.21%
Win Rate: 55.67%
Final Capital: $112,340.00

## คำเตือน

ค่า p-value ที่ต่ำกว่า 0.05 แสดงว่าคู่หุ้นนี้เหมาะกับกลยุทธ์นี้ แต่ควรทดสอบกับข้อมูล Out-of-sample ก่อนนำไปใช้งานจริง
