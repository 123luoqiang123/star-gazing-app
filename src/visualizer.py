import plotly.express as px
import plotly.graph_objects as go

def create_map(df):
    fig = px.scatter_geo(
        df,
        lat='lat',
        lon='lon',
        color='total_score',
        size='total_score',
        hover_name='city',
        color_continuous_scale='RdYlGn_r',
        title='🌌 中国观星地点推荐地图',
        projection='equirectangular',
        size_max=40
    )
    fig.update_geos(
        lonaxis_range=[70, 135],
        lataxis_range=[15, 55],
        showland=True,
        landcolor='#1a1f2e',
        showcountries=True,
        countrycolor='#3a3f5a',
        showocean=True,
        oceancolor='#0a0e18',
        showframe=False
    )
    fig.update_traces(
        marker=dict(line=dict(width=0))
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f0f4ff', size=13),
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        height=650,
        title_font=dict(color='#f0f4ff')
    )
    fig.update_coloraxes(colorbar=dict(
        title_font=dict(color='#f0f4ff'),
        tickfont=dict(color='#f0f4ff')
    ))
    return fig

def create_bar_chart(df):
    fig = px.bar(
        df,
        x='total_score',
        y='city',
        color='rating',
        text='total_score',
        orientation='h',
        title='🌟 观星适宜性综合评分排行榜',
        color_discrete_map={
            '★★★★★': '#2ECC40',
            '★★★★☆': '#39D2C0',
            '★★★☆☆': '#FFDC00',
            '★★☆☆☆': '#FF851B',
            '★☆☆☆☆': '#FF4136'
        }
    )
    fig.update_traces(
        texttemplate='%{text:.1f}分',
        textposition='outside',
        textfont=dict(color='#f0f4ff', size=13)
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f0f4ff'),
        xaxis_title='综合得分',
        yaxis_title='城市',
        height=500,
        xaxis_range=[0, 105],
        xaxis=dict(gridcolor='rgba(255,255,255,0.08)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.08)'),
        title_font=dict(color='#f0f4ff')
    )
    return fig

def create_radar_chart(df, top_n=5):
    top_df = df.head(top_n)
    categories = ['光污染', '空气质量', '云量', '海拔']
    
    colors = [
        'rgba(255, 107, 107, 0.5)',
        'rgba(78, 205, 196, 0.5)',
        'rgba(255, 230, 109, 0.5)',
        'rgba(168, 230, 207, 0.5)',
        'rgba(255, 138, 92, 0.5)'
    ]
    line_colors = ['#FF6B6B', '#4ECDC4', '#FFE66D', '#A8E6CF', '#FF8A5C']
    
    fig = go.Figure()
    for idx, (_, row) in enumerate(top_df.iterrows()):
        fig.add_trace(go.Scatterpolar(
            r=[row['light_score'], row['aqi_score'], row['cloud_score'], row['elevation_score']],
            theta=categories,
            fill='toself',
            name=row['city'],
            line=dict(color=line_colors[idx % len(line_colors)], width=2),
            fillcolor=colors[idx % len(colors)]
        ))
    
    fig.add_trace(go.Scatterpolar(
        r=[100, 100, 100, 100],
        theta=categories,
        fill=None,
        name='满分参考线',
        line=dict(color='rgba(180,180,200,0.3)', width=2, dash='dash')
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f0f4ff'),
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor='rgba(255,255,255,0.1)',
                tickfont=dict(color='#f0f4ff')
            ),
            angularaxis=dict(
                tickfont=dict(color='#f0f4ff', size=14),
                gridcolor='rgba(255,255,255,0.1)'
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        title=f'🏅 TOP{top_n} 城市观星条件雷达对比',
        height=520,
        title_font=dict(color='#f0f4ff'),
        legend=dict(
            font=dict(color='#f0f4ff', size=11),
            orientation='h',
            yanchor='top',
            y=-0.08,
            xanchor='center',
            x=0.5
        )
    )
    return fig

# ===== 以下为新增的四个指标分析图表 =====

def create_bortle_chart(df):
    """光污染等级分布图（Bortle 1~9，越低越好）"""
    sorted_df = df.sort_values('bortle', ascending=True)
    
    fig = px.bar(
        sorted_df,
        x='bortle',
        y='city',
        orientation='h',
        text='bortle',
        title='🌙 光污染等级分布（Bortle 1~9，数值越低越好）',
        color='bortle',
        color_continuous_scale='Viridis_r',
        range_color=[1, 9]
    )
    fig.update_traces(
        texttemplate='%{text}级',
        textposition='outside',
        textfont=dict(color='#f0f4ff', size=12)
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f0f4ff'),
        xaxis_title='Bortle等级（1=最暗，9=最亮）',
        yaxis_title='城市',
        height=350,
        xaxis=dict(
            range=[0.5, 9.5],
            tickvals=list(range(1, 10)),
            gridcolor='rgba(255,255,255,0.08)'
        ),
        yaxis=dict(gridcolor='rgba(255,255,255,0.08)'),
        title_font=dict(color='#f0f4ff'),
        coloraxis_showscale=False
    )
    return fig

def create_aqi_chart(df):
    """空气质量分布图（AQI，越低越好）"""
    sorted_df = df.sort_values('aqi', ascending=True)
    
    fig = px.bar(
        sorted_df,
        x='aqi',
        y='city',
        orientation='h',
        text='aqi',
        title='💨 空气质量分布（AQI，数值越低越好）',
        color='aqi',
        color_continuous_scale='Blues_r',
        range_color=[0, 200]
    )
    fig.update_traces(
        texttemplate='%{text}',
        textposition='outside',
        textfont=dict(color='#f0f4ff', size=12)
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f0f4ff'),
        xaxis_title='空气质量指数（AQI）',
        yaxis_title='城市',
        height=350,
        xaxis=dict(gridcolor='rgba(255,255,255,0.08)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.08)'),
        title_font=dict(color='#f0f4ff'),
        coloraxis_showscale=False
    )
    return fig

def create_cloud_chart(df):
    """云量分布图（%，越低越好）"""
    sorted_df = df.sort_values('cloud_cover', ascending=True)
    
    fig = px.bar(
        sorted_df,
        x='cloud_cover',
        y='city',
        orientation='h',
        text='cloud_cover',
        title='☁️ 云量分布（%，数值越低越好）',
        color='cloud_cover',
        color_continuous_scale='Blues_r',
        range_color=[0, 100]
    )
    fig.update_traces(
        texttemplate='%{text}%',
        textposition='outside',
        textfont=dict(color='#f0f4ff', size=12)
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f0f4ff'),
        xaxis_title='云量（%）',
        yaxis_title='城市',
        height=350,
        xaxis=dict(gridcolor='rgba(255,255,255,0.08)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.08)'),
        title_font=dict(color='#f0f4ff'),
        coloraxis_showscale=False
    )
    return fig

def create_elevation_chart(df):
    """海拔分布图（米，越高越好）"""
    sorted_df = df.sort_values('elevation', ascending=True)
    
    fig = px.bar(
        sorted_df,
        x='elevation',
        y='city',
        orientation='h',
        text='elevation',
        title='🏔️ 海拔分布（米，数值越高越好）',
        color='elevation',
        color_continuous_scale='YlOrRd',
        range_color=[0, 4000]
    )
    fig.update_traces(
        texttemplate='%{text}m',
        textposition='outside',
        textfont=dict(color='#f0f4ff', size=12)
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f0f4ff'),
        xaxis_title='海拔（米）',
        yaxis_title='城市',
        height=350,
        xaxis=dict(gridcolor='rgba(255,255,255,0.08)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.08)'),
        title_font=dict(color='#f0f4ff'),
        coloraxis_showscale=False
    )
    return fig