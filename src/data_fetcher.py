import pandas as pd
import random
import pathlib

# 获取项目根目录的路径（因为我们在 src/ 文件夹里，所以要往上一级）
BASE_DIR = pathlib.Path(__file__).parent.parent

def fetch_city_data(use_mock=True):
    """
    获取城市观星相关数据
    use_mock=True 表示使用模拟数据（先跑通流程）
    """
    # 读取之前创建的 cities.csv 文件
    file_path = BASE_DIR / 'data' / 'cities.csv'
    df = pd.read_csv(file_path)
    
    # 用来存放生成的数据
    mock_data = []
    
    # 逐行处理每个城市
    for _, row in df.iterrows():
        city = row['city']
        elev = row['elevation']
        
        # ---------- 模拟光污染 (Bortle等级 1~9, 1最暗 9最亮) ----------
        # 海拔越高，光污染越小；大城市光污染严重
        if elev > 3000:          # 比如 拉萨
            bortle = random.randint(1, 3)
        elif elev > 1000:        # 比如 大理、敦煌
            bortle = random.randint(2, 4)
        elif city in ['北京', '上海', '广州', '深圳']:  # 超大城市
            bortle = random.randint(7, 9)
        else:                    # 其他城市（杭州、成都等）
            bortle = random.randint(4, 6)
        
        # ---------- 模拟空气质量 AQI (数值越小空气越好) ----------
        if city in ['北京', '上海']:
            aqi = random.randint(80, 180)
        elif city in ['拉萨', '敦煌', '呼伦贝尔']:
            aqi = random.randint(20, 60)
        else:
            aqi = random.randint(40, 100)
        
        # ---------- 模拟云量 (0~100%, 数值越小天空越晴朗) ----------
        if city in ['敦煌', '拉萨', '呼伦贝尔']:   # 西北/北方干燥少云
            cloud = random.randint(10, 40)
        elif city in ['杭州', '广州', '成都']:      # 南方多云
            cloud = random.randint(50, 80)
        else:
            cloud = random.randint(30, 60)
        
        # 把生成的数据存起来
        mock_data.append({
            'city': city,
            'lat': row['lat'],
            'lon': row['lon'],
            'elevation': elev,
            'bortle': bortle,        # 光污染等级
            'aqi': aqi,              # 空气质量指数
            'cloud_cover': cloud     # 云量百分比
        })
    
    return pd.DataFrame(mock_data)


# 测试一下（如果直接运行这个文件）
if __name__ == '__main__':
    df = fetch_city_data(use_mock=True)
    print("✅ 数据获取成功！预览前5行：")
    print(df.head())