# Quant Research Portfolio

คลังโปรเจคสำหรับจำลองกลยุทธ์การลงทุนเชิงปริมาณ (Quantitative Trading)

## โปรเจคในคลัง
1. **Monte Carlo GBM Simulator** - จำลองราคาสินทรัพย์และคำนวณ Value at Risk (VaR)
2. **EWMA Crossover** - กลยุทธ์เทรนด์ พร้อม Grid Search Optimization
3. **Efficient Frontier Optimizer** - หาพอร์ตลงทุนที่เหมาะสมที่สุด
4. **Sharpe Ratio Dashboard** - Streamlit Web App

## การติดตั้ง
```bash
pip install -r requirements.txt

##การใช้งาน Dashboard
streamlit run projects/03_dashboard/app.py
