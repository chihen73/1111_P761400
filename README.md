# 程式簡介
* 因作業繳交時間較短與對Python語言掌握度不高緣故，採用現行已成熟之預訓練模型[Prophet](https://facebook.github.io/prophet/)依照作業給定之條件實作
* 依循助教建議使用`Poetry`進行環境與套件管理
* 依循助教提供之作業樣板進行分支編輯
* 依循助教提供之code trace args進行整合
* 依循助教提供之[StockProfitCalculator](https://github.com/NCKU-CCS/StockProfitCalculator)進行獲利計算
---
# 策略說明
* 考慮到模型本身預測價格已經過鈍化(對每日價格的波動敏感度小)所以就順著每天預測隔日的價格來做趨勢判斷
* 由於模型無法對黑天鵝事件或其他經濟崩盤事件進行反應，所以策略專注在波段獲利(約抓一個月)，若碰巧抓到該波段就獲利，若無至少鈍化後的指標可以在後續進行止損(只要最終賺的比賠的多就夠了)
* 雖然抓一個月的波段不利於本作業績效最佳化，但考慮到指標太敏感、動作過於頻繁在作業限制條件下其實佔不到便宜(雖然不用買賣成本與手續費很棒但基數固定為1且每日只能一次動作無法進行超短線獲利)
* 結論就是以上策略都不管用，最終還是回歸`一切都是命`(好像真的不用靠模型寫寫IF判斷獲利應該最好，不過還是盡力而為寫寫程式、玩玩模型當作一種有趣的經驗也很好)
---
# 程式邏輯說明([trader.py](https://github.com/chihen73/1111_P761400_HW1/blob/main/trader.py))
* 使用Pandas.read_csv()功能由助教指定的`args.training` `args.testing`從**CLI**(Command Line Interface)讀入`training_data.csv`與`testing_data.csv`
```python
  training_source = pd.read_csv(args.training, header=None)
  testing_source = pd.read_csv(args.testing, header=None)
```
* 針對training data進行資料處理，只使用自動生成時間序列與收市價格與兩個欄位進行預測
```python
  training_temp = training_source[[3]]
  training_temp.reset_index(inplace=True)
  training_temp['index'] = pd.to_datetime(training_temp['index'], unit='D')
  training_temp=training_temp.rename(columns={"index": "ds", 3 : "y"})
```
* 針對testing data進行資料處理只保留收市價格於預測時使用
```python
  testing_temp = testing_source[[3]].rename(columns={3 : "y"})
```
* 使用act_state儲存act行為(1,0,-1)
* 將當日收市資料新增至training data後進行訓練(以testing data長度-1進行迭代，以符合看一天預測一天的條件)
```python
  for i in range(len(testing_data.index)-1):
    training_data.loc[len(training_data.index)] = [(training_data.loc[len(training_data.index)-1][0]) + timedelta(days=1) ,testing_data.iloc[i]['y']]
```
* 投資決策條件是比對明日預測市值是否大於今日市值，若是歸類為上升趨勢進行動作寫入，反之則歸類為下降趨勢進行動作寫入
```python
if  forecast.iloc[len(forecast.index) - 1]['yhat'] >= forecast.iloc[len(forecast.index) - 2]['yhat'] :
  #趨勢向上的決策
  if act_state == 1:
    act = 0
  elif act_state == 0:
    act = 1
    act_state = 1
  elif act_state == -1:
    act = 1
    act_state = 0 
  else:
    print('狀態異常')
    break
else: 
  #趨勢向下的決策
  if act_state == 1:
    act = -1
    act_state = 0
  elif act_state == 0:
    act = -1
    act_state = -1
  elif act_state == -1:
    act = 0
  else:
    print('狀態異常')
    break
```
* 每日預測後隨即輸出動作以符合作業要求
```python
with open(args.output, 'a', newline='') as file:
  writer = csv.writer(file)
  data = [act]
  writer.writerow(data)

  print("第", i+1, "日決策輸出")
```
---
# 測試過程
* Ubuntu Server 22.04.1 LTS (AMD64)  
`Prophet因版本相容性因素無法於ARM架構下執行(實測Apple M1會出現問題)`    
![OS-version](https://github.com/chihen73/1111_P761400_HW1/blob/main/contents/OS_version.png)
* 使用Poertry Shell虛擬環境
* Python 3.10.6
![python-version](https://github.com/chihen73/1111_P761400_HW1/blob/main/contents/python_version.png)
* 依循作業規定使用CLI執行
![traderpy-run](https://github.com/chihen73/1111_P761400_HW1/blob/main/contents/traderpy_run.png)
* 依循作業規定每日寫入Act並以output.csv輸出
![output-res](https://github.com/chihen73/1111_P761400_HW1/blob/main/contents/output_res.png)
* 依循建議使用StockProfitCalculator計算獲利
![profit-calculator](https://github.com/chihen73/1111_P761400_HW1/blob/main/contents/profit_calculator.png)

