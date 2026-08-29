"""
projects/04_pairs_bot/bot.py
Mean Reversion Pairs Trading Bot
ใช้ Cointegration และ Z-score เพื่อหาโอกาสซื้อ/ขาย
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from src.data_fetcher import DataFetcher


def find_cointegrated_pairs(df_prices, significance=0.05):
    """
    ค้นหาคู่หุ้นที่มีความสัมพันธ์กันในระยะยาว (Cointegration)
    
    Args:
        df_prices: DataFrame ของราคาหุ้นหลายตัว (columns = tickers)
        significance: ระดับนัยสำคัญ (ค่า p-value ต่ำกว่า = มี Cointegration)
    
    Returns:
        dict: คู่หุ้นที่มี p-value ต่ำที่สุด
    """
    tickers = df_prices.columns
    best_pair = None
    best_p_value = 1.0
    
    for i in range(len(tickers)):
        for j in range(i+1, len(tickers)):
            y = df_prices.iloc[:, i]
            x = df_prices.iloc[:, j]
            
            # หา Hedge Ratio (OLS)
            model = sm.OLS(y, sm.add_constant(x)).fit()
            hedge_ratio = model.params.iloc[1]
            
            # คำนวณ Spread
            spread = y - hedge_ratio * x
            
            # ทดสอบ Cointegration (ADF Test)
            result = adfuller(spread)
            p_value = result[1]
            
            if p_value < significance and p_value < best_p_value:
                best_p_value = p_value
                best_pair = {
                    'ticker1': tickers[i],
                    'ticker2': tickers[j],
                    'hedge_ratio': hedge_ratio,
                    'p_value': p_value,
                    'spread': spread
                }
    
    return best_pair


def generate_pairs_signals(df_prices, ticker1, ticker2, hedge_ratio, lookback=60, entry_z=2.0, exit_z=0.5):
    """
    สร้างสัญญาณซื้อ/ขายจาก Z-score ของ Spread
    
    Args:
        df_prices: DataFrame ของราคา
        ticker1: หุ้นตัวที่ 1
        ticker2: หุ้นตัวที่ 2
        hedge_ratio: อัตราส่วนที่ใช้ถ่วงน้ำหนัก
        lookback: ระยะเวลาย้อนหลังในการคำนวณ Z-score
        entry_z: ค่า Z-score ที่เข้า Trade (เช่น 2.0 = ขายเมื่อ Spread สูงกว่าค่าเฉลี่ย 2 ส่วนเบี่ยงเบน)
        exit_z: ค่า Z-score ที่ปิด Trade (เช่น 0.5)
    
    Returns:
        pd.DataFrame: ตารางที่มีสัญญาณ
    """
    df = pd.DataFrame(index=df_prices.index)
    df['price1'] = df_prices[ticker1]
    df['price2'] = df_prices[ticker2]
    
    # คำนวณ Spread
    df['spread'] = df['price1'] - hedge_ratio * df['price2']
    
    # คำนวณ Z-score (ใช้ Rolling Mean/Std)
    df['spread_mean'] = df['spread'].rolling(lookback).mean()
    df['spread_std'] = df['spread'].rolling(lookback).std()
    df['z_score'] = (df['spread'] - df['spread_mean']) / df['spread_std']
    
    # สร้างสัญญาณ
    # 1 = ซื้อ (Long spread, คาดว่า spread จะกลับขึ้นไป) -> ซื้อ ticker1, ขาย ticker2
    # -1 = ขาย (Short spread, คาดว่า spread จะกลับลงมา) -> ขาย ticker1, ซื้อ ticker2
    # 0 = ไม่ถือ
    df['signal'] = 0
    
    # เข้า Trade (Long spread เมื่อ z-score ต่ำกว่า -entry_z)
    df.loc[df['z_score'] < -entry_z, 'signal'] = 1
    # เข้า Trade (Short spread เมื่อ z-score สูงกว่า +entry_z)
    df.loc[df['z_score'] > entry_z, 'signal'] = -1
    
    # ปิด Trade (เมื่อ z-score กลับมาที่ exit_z)
    df.loc[(df['z_score'] < exit_z) & (df['z_score'] > -exit_z), 'signal'] = 0
    
    # ป้องกัน Look-ahead bias: ใช้สัญญาณของวันก่อนหน้า
    df['position'] = df['signal'].shift(1)
    df['position'] = df['position'].fillna(0)
    
    # คำนวณผลตอบแทน (Long spread)
    df['return1'] = df['price1'].pct_change()
    df['return2'] = df['price2'].pct_change()
    df['strategy_return'] = df['position'] * (df['return1'] - hedge_ratio * df['return2'])
    
    return df


def backtest_pairs(df_signals, initial_capital=100000, transaction_cost=0.001):
    """
    คำนวณ Performance ของกลยุทธ์ Pairs Trading
    
    Returns:
        dict: ผลลัพธ์
    """
    df = df_signals.copy()
    
    # Cumulative Return
    df['cumulative_return'] = (1 + df['strategy_return']).cumprod() * initial_capital
    
    # Drawdown
    rolling_max = df['cumulative_return'].expanding().max()
    df['drawdown'] = (df['cumulative_return'] - rolling_max) / rolling_max
    
    # Metrics
    total_return = (df['cumulative_return'].iloc[-1] / initial_capital) - 1
    sharpe = (df['strategy_return'].mean() / df['strategy_return'].std()) * np.sqrt(252) if df['strategy_return'].std() != 0 else 0
    max_drawdown = df['drawdown'].min()
    
    # Win Rate
    winning_trades = df[df['strategy_return'] > 0]
    win_rate = len(winning_trades) / len(df[df['strategy_return'] != 0]) if len(df[df['strategy_return'] != 0]) > 0 else 0
    
    return {
        'total_return': total_return,
        'sharpe_ratio': sharpe,
        'max_drawdown': max_drawdown,
        'win_rate': win_rate,
        'final_capital': df['cumulative_return'].iloc[-1],
        'df': df
    }


def run_pairs_bot(ticker1='AAPL', ticker2='MSFT', start='2020-01-01', lookback=60):
    """
    ฟังก์ชันหลักสำหรับรัน Pairs Trading Bot
    """
    # 1. ดึงข้อมูล
    df_prices = DataFetcher.get_multiple_stocks([ticker1, ticker2], start=start)
    
    # 2. หา Hedge Ratio (ถ้ายังไม่รู้)
    # ในตัวอย่างนี้เราจะใช้ OLS ในการหา Hedge Ratio
    y = df_prices[ticker1]
    x = df_prices[ticker2]
    model = sm.OLS(y, sm.add_constant(x)).fit()
    hedge_ratio = model.params.iloc[1]
    
    print(f" Hedge Ratio: {hedge_ratio:.4f}")
    
    # 3. ทดสอบ Cointegration
    spread = y - hedge_ratio * x
    result = adfuller(spread)
    print(f" Cointegration p-value: {result[1]:.4f}")
    
    if result[1] > 0.05:
        print(" คำเตือน: คู่หุ้นนี้ไม่มี Cointegration ที่นัยสำคัญ (p-value > 0.05)")
    
    # 4. สร้างสัญญาณ
    df_signals = generate_pairs_signals(df_prices, ticker1, ticker2, hedge_ratio, lookback=lookback)
    
    # 5. Backtest
    result = backtest_pairs(df_signals, initial_capital=100000)
    
    # 6. แสดงผล
    print("\n ผลลัพธ์ Pairs Trading Bot")
    print("=" * 40)
    print(f"Total Return: {result['total_return']:.2%}")
    print(f"Sharpe Ratio: {result['sharpe_ratio']:.2f}")
    print(f"Max Drawdown: {result['max_drawdown']:.2%}")
    print(f"Win Rate: {result['win_rate']:.2%}")
    print(f"Final Capital: ${result['final_capital']:,.2f}")
    
    return result
