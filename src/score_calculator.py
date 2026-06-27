import pandas as pd
import numpy as np

def calculate_scores(df):
    """
    输入：包含 bortle, aqi, cloud_cover, elevation 的 DataFrame
    输出：添加了各项得分和总评分的 DataFrame（按总分从高到低排序）
    """
    # 复制一份，避免修改原数据
    result = df.copy()
    
    # ----- 1. 光污染得分 (Bortle 1级=100分, 9级=0分) -----
    result['light_score'] = ((9 - result['bortle']) / 8) * 100
    
    # ----- 2. 空气质量得分 (AQI 0=100分, 300=0分, 超过300算0) -----
    result['aqi_score'] = np.clip((1 - result['aqi'] / 300) * 100, 0, 100)
    
    # ----- 3. 云量得分 (云量0%=100分, 100%=0分) -----
    result['cloud_score'] = (1 - result['cloud_cover'] / 100) * 100
    
    # ----- 4. 海拔得分 (海拔2000米以上得100分, 0米得0分) -----
    result['elevation_score'] = np.clip((result['elevation'] / 2000) * 100, 0, 100)
    
    # ----- 5. 加权计算总分 (权重: 光污染35%, 云量25%, AQI 20%, 海拔20%) -----
    weights = {
        'light_score': 0.35,
        'cloud_score': 0.25,
        'aqi_score': 0.20,
        'elevation_score': 0.20
    }
    
    result['total_score'] = (
        result['light_score'] * weights['light_score'] +
        result['cloud_score'] * weights['cloud_score'] +
        result['aqi_score'] * weights['aqi_score'] +
        result['elevation_score'] * weights['elevation_score']
    )
    
    # ----- 6. 评级 (五星制) -----
    def rate_star(score):
        if score >= 85:   return '★★★★★'
        elif score >= 70: return '★★★★☆'
        elif score >= 55: return '★★★☆☆'
        elif score >= 40: return '★★☆☆☆'
        else:             return '★☆☆☆☆'
    
    result['rating'] = result['total_score'].apply(rate_star)
    
    # 按总分从高到低排序
    result = result.sort_values('total_score', ascending=False).reset_index(drop=True)
    
    return result


# 测试一下（如果直接运行这个文件）
if __name__ == '__main__':
    # 为了测试，我们临时调用 data_fetcher 获取数据
    from data_fetcher import fetch_city_data
    raw_df = fetch_city_data(use_mock=True)
    scored_df = calculate_scores(raw_df)
    
    print("✅ 评分计算成功！按总分排名如下：")
    print(scored_df[['city', 'total_score', 'rating', 'light_score', 'cloud_score', 'aqi_score', 'elevation_score']])