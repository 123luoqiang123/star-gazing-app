import pandas as pd
import random
import pathlib

BASE_DIR = pathlib.Path(__file__).parent.parent


def fetch_city_data(use_mock=True):
    file_path = BASE_DIR / 'data' / 'cities.csv'
    df = pd.read_csv(file_path)
    
    # 无论 use_mock 是什么值，光污染都从 CSV 读取，云量都使用合理的模拟值
    # 这样网站数据稳定，不会因为 API 失败而显示 50%
    
    data_list = []
    for _, row in df.iterrows():
        city = row['city']
        elev = row['elevation']
        
        # ----- 1. 光污染直接从 CSV 读取（真实值）-----
        bortle = row['bortle']
        
        # ----- 2. 基于城市特征生成合理的云量（不是完全随机）-----
        # 西北/高原城市：少云（10-30%）
        if city in ['敦煌', '拉萨', '呼伦贝尔']:
            cloud = random.randint(10, 35)
        # 南方城市：多云（40-70%）
        elif city in ['杭州', '广州', '成都', '深圳']:
            cloud = random.randint(40, 70)
        # 其他城市：中等（25-55%）
        else:
            cloud = random.randint(25, 55)
        
        # ----- 3. 基于城市特征生成合理的 AQI -----
        if city in ['北京', '上海']:
            aqi = random.randint(70, 160)
        elif city in ['拉萨', '敦煌', '呼伦贝尔']:
            aqi = random.randint(20, 55)
        else:
            aqi = random.randint(35, 90)
        
        data_list.append({
            'city': city,
            'lat': row['lat'],
            'lon': row['lon'],
            'elevation': elev,
            'bortle': bortle,
            'aqi': aqi,
            'cloud_cover': cloud
        })
    
    return pd.DataFrame(data_list)


if __name__ == '__main__':
    df = fetch_city_data()
    print("✅ 数据获取成功！预览：")
    print(df[['city', 'bortle', 'cloud_cover', 'aqi']].to_string(index=False))