# You can write code above the if-main block.

if __name__ == "__main__":
    # You should not modify this part.
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--training", default="training_data.csv", help="input training data file name")
    parser.add_argument("--testing", default="testing_data.csv", help="input testing data file name")
    parser.add_argument("--output", default="output.csv", help="output file name")
    args = parser.parse_args()

    # The following part is an example.
    # You can modify it at will.

    import numpy as np
    import pandas as pd
    from prophet import Prophet
    import csv
    from datetime import datetime, date, timedelta
    import warnings
    warnings.filterwarnings('ignore')

    #使用Pandas.read_csv()功能由助教指定的args.training args.testing從CLI(Command Line Interface)讀入training_data.csv與testing_data.csv
    training_source = pd.read_csv(args.training, header=None)
    testing_source = pd.read_csv(args.testing, header=None)

    #針對training data進行資料處理，只使用自動生成時間序列與收市價格與兩個欄位進行預測
    training_temp = training_source[[3]]
    training_temp.reset_index(inplace=True)
    training_temp['index'] = pd.to_datetime(training_temp['index'], unit='D')
    training_temp=training_temp.rename(columns={"index": "ds", 3 : "y"})

    #針對testomg data進行資料處理只保留收市價格於預測時使用
    testing_temp = testing_source[[3]].rename(columns={3 : "y"})

    training_data = training_temp
    testing_data = testing_temp

    #使用act_state儲存act行為(1,0,-1)
    act_state = 0
    act = 0

    for i in range(len(testing_data.index)-1):
        #新增今日收市資料作為訓練資料
        training_data.loc[len(training_data.index)] = [(training_data.loc[len(training_data.index)-1][0]) + timedelta(days=1) ,testing_data.iloc[i]['y']]
        #模型訓練
        m = Prophet()
        m.fit(training_data)
        
        #預測
        future = m.make_future_dataframe(periods=1)
        forecast = m.predict(future)

        #決策
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

        with open(args.output, 'a', newline='') as file:
            writer = csv.writer(file)
            data = [act]
            writer.writerow(data)

        print("第", i+1, "日決策輸出")
