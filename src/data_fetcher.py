import pandas as pd
import random
import pathlib
import requests
import time

BASE_DIR = pathlib.Path(__file__).parent.parent


def fetch_city_data(use_mock=True):
    """
    获取城市观星相关数据
    use_mock=True: 模拟数据（光污染使用真实值，其他随机）
    use_mock=False: 真实数据（光污染从CSV读，云量从7Timer获取，AQI模拟）
    """
    file_path = BASE_DIR / 'data' / 'cities.csv'
    df = pd.read_csv(file_path)
    
    if use_mock:
        # ========== 模拟数据模式 ==========
        mock_data = []
        for _, row in df.iterrows():
            city = row['city']
            elev = row['elevation']
            
            # 光污染直接从 CSV 读取（真实值）
            bortle = row['bortle']
            
            # AQI 模拟
            if city in ['北京', '上海']:
                aqi = random.randint(80, 180)
            elif city in ['拉萨', '敦煌', '呼伦贝尔']:
                aqi = random.randint(20, 60)
            else:
                aqi = random.randint(40, 100)
            
            # 云量模拟
            if city in ['敦煌', '拉萨', '呼伦贝尔']:
                cloud = random.randint(10, 40)
            elif city in ['杭州', '广州', '成都']:
                cloud = random.randint(50, 80)
            else:
                cloud = random.randint(30, 60)
            
            mock_data.append({
                'city': city,
                'lat': row['lat'],
                'lon': row['lon'],
                'elevation': elev,
                'bortle': bortle,
                'aqi': aqi,
                'cloud_cover': cloud
            })
        return pd.DataFrame(mock_data)
    
    else:
        # ========== 真实 API 数据模式 ==========
        real_data = []
        
        for _, row in df.iterrows():
            city = row['city']
            lat = row['lat']
            lon = row['lon']
            elev = row['elevation']
            
            # ----- 1. 光污染直接从 CSV 读取（真实值）-----
            bortle = row['bortle']
            
            # ----- 2. 获取云量（7Timer - 完全免费，无需 API Key）-----
            try:
                weather_url = f"https://www.7timer.info/bin/api.pl?lon={lon}&lat={lat}&product=astro&output=json"
                response = requests.get(weather_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    # 7Timer 云量是 0-8 级，0=晴天，8=阴天
                    # 某些情况下可能返回 9（表示数据缺失）
                    cloud_okta = data.get('dataseries', [{}])[0].get('cloudcover', 0)
                    
                    if cloud_okta == 9:
                        # 数据缺失，使用默认值 50%
                        cloud = 50
                        print(f"⚠️ {city} 7Timer 数据缺失，使用默认值 50%")
                    else:
                        # 正常转换 0-8 为 0%-100%
                        cloud = (cloud_okta / 8) * 100
                        print(f"✅ {city} 云量获取成功: {cloud:.1f}%")
                else:
                    print(f"⚠️ {city} 7Timer 请求失败 (HTTP {response.status_code})，使用默认值 50%")
                    cloud = 50
            except requests.exceptions.Timeout:
                print(f"❌ {city} 7Timer 请求超时，使用默认值 50%")
                cloud = 50
            except Exception as e:
                print(f"❌ {city} 获取云量失败: {e}，使用默认值 50%")
                cloud = 50
            
            # ----- 3. AQI 暂时保留模拟 -----
            if city in ['北京', '上海']:
                aqi = random.randint(80, 180)
            elif city in ['拉萨', '敦煌', '呼伦贝尔']:
                aqi = random.randint(20, 60)
            else:
                aqi = random.randint(40, 100)
            
            real_data.append({
                'city': city,
                'lat': lat,
                'lon': lon,
                'elevation': elev,
                'bortle': bortle,
                'aqi': aqi,
                'cloud_cover': round(cloud, 1)  # 保留一位小数
            })
            
            time.sleep(0.5)  # 避免请求过快
        
        return pd.DataFrame(real_data)


if __name__ == '__main__':
    # 测试真实数据模式
    print("=" * 50)
    print("测试真实 API 数据模式...")
    print("=" * 50)
    df = fetch_city_data(use_mock=False)
    print("\n✅ 数据获取完成！预览：")
    print(df[['city', 'bortle', 'cloud_cover', 'aqi']].to_string(index=False))