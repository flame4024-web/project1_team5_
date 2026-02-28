import os
import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib
import numpy as np
import folium

# Paths
DATA_DIR = r"c:\ICB7\project_1\data"
GN_CSV = os.path.join(DATA_DIR, 'gangnam_time_zones_20260227.csv')
YW_CSV = os.path.join(DATA_DIR, 'yeouido_time_zones_20260224.csv')

IMG_DIR = r"c:\ICB7\project_1\project_3\images"
os.makedirs(IMG_DIR, exist_ok=True)

def load_data():
    gn_df = pd.read_csv(GN_CSV, encoding='utf-8')
    yw_df = pd.read_csv(YW_CSV, encoding='utf-8')
    # 컬럼 이름 맞추기 (예: '소요시간(분)')
    gn_col = '소요시간(분)' if '소요시간(분)' in gn_df.columns else ('time' if 'time' in gn_df.columns else gn_df.columns[-1])
    yw_col = '소요시간(분)' if '소요시간(분)' in yw_df.columns else ('time' if 'time' in yw_df.columns else yw_df.columns[-1])
    
    gn_df['소요시간'] = gn_df[gn_col]
    yw_df['소요시간'] = yw_df[yw_col]
    
    return gn_df, yw_df

# 1. 권역별 도달 가능 지하철역 히스토그램
def draw_histogram(gn_df, yw_df):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bins = range(0, 70, 10)
    
    ax.hist([gn_df['소요시간'], yw_df['소요시간']], bins=bins, color=['#e74c3c', '#3498db'], 
            label=['강남역 출발', '여의도역 출발'], alpha=0.7, edgecolor='k')
            
    ax.set_title("강남역 vs 여의도역 소요시간별 도달 가능 지하철역 수", fontsize=16, fontweight='bold')
    ax.set_xlabel("소요시간(분) 구간", fontsize=12)
    ax.set_ylabel("대상역 개수", fontsize=12)
    ax.set_xticks(bins)
    ax.legend(fontsize=12)
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    
    save_path = os.path.join(IMG_DIR, 'station_histogram.png')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    return save_path

# 2. 통근 권역 지도 시각화 (더미 좌표 활용)
def draw_map():
    # 실제 역 좌표가 없으므로 강남과 여의도 중심으로 임의 분포
    m = folium.Map(location=[37.51, 126.98], zoom_start=12)
    
    gn_lat, gn_lon = 37.4979, 127.0276
    yw_lat, yw_lon = 37.5215, 126.9243
    
    folium.Marker([gn_lat, gn_lon], popup='강남역', icon=folium.Icon(color='red', icon='briefcase')).add_to(m)
    folium.Marker([yw_lat, yw_lon], popup='여의도역', icon=folium.Icon(color='blue', icon='briefcase')).add_to(m)
    
    # 30분(반경 3km), 45분(반경 6km), 60분(반경 10km) 원 표기
    colors = {30: 'green', 45: 'orange', 60: 'red'}
    for r_km, mins in [(3000, 30), (6000, 45), (10000, 60)]:
        folium.Circle([gn_lat, gn_lon], radius=r_km, color=colors[mins], weight=2, fill=False).add_to(m)
        folium.Circle([yw_lat, yw_lon], radius=r_km, color=colors[mins], weight=2, fill=False).add_to(m)

    save_path = os.path.join(IMG_DIR, 'commute_map_folium.html')
    m.save(save_path)
    
    # 정적 맵 (마크다운용)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(gn_lon, gn_lat, 'ro', markersize=12, label='강남역')
    ax.plot(yw_lon, yw_lat, 'bo', markersize=12, label='여의도역')
    
    circle_opts = [(0.03, 'g', '30분'), (0.06, 'orange', '45분'), (0.1, 'r', '60분')]
    for r, c, l in circle_opts:
        ax.add_patch(plt.Circle((gn_lon, gn_lat), r, color=c, fill=False, linestyle='--'))
        ax.add_patch(plt.Circle((yw_lon, yw_lat), r, color=c, fill=False, linestyle='--'))
    
    # 텍스트 라벨 해킹
    ax.plot([], [], color='g', linestyle='--', label='30분 권역')
    ax.plot([], [], color='orange', linestyle='--', label='45분 권역')
    ax.plot([], [], color='r', linestyle='--', label='60분 권역')
        
    ax.set_aspect('equal')
    ax.set_xlim(126.8, 127.2)
    ax.set_ylim(37.35, 37.65)
    ax.set_title("강남/여의도 기점 30/45/60분 통근 권역 지도 시각화", fontweight='bold')
    ax.legend(loc='lower right')
    
    static_save = os.path.join(IMG_DIR, 'commute_map_static.png')
    plt.tight_layout()
    plt.savefig(static_save, dpi=300)
    plt.close()
    return static_save

# 3. 맞벌이 부부 맞춤형 통근 최적 입지 산점도
def draw_scatter(gn_df, yw_df):
    # 대상역 기준으로 Merge
    merged = pd.merge(gn_df[['대상역', '소요시간']], yw_df[['대상역', '소요시간']], on='대상역', suffixes=('_강남', '_여의도'))
    
    # 둘다 60분 이내 필터링
    filtered = merged[(merged['소요시간_강남'] <= 60) & (merged['소요시간_여의도'] <= 60)].copy()
    
    # 총 합산 시간 계산
    filtered['합산시간'] = filtered['소요시간_강남'] + filtered['소요시간_여의도']
    filtered = filtered.sort_values(by='합산시간').reset_index(drop=True)
    
    # TOP 10 추출
    top10 = filtered.head(10)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    ax.scatter(filtered['소요시간_강남'], filtered['소요시간_여의도'], color='gray', alpha=0.5, label='도달 가능 역')
    ax.scatter(top10['소요시간_강남'], top10['소요시간_여의도'], color='red', s=100, label='TOP 10 최적역')
    
    for i, row in top10.iterrows():
        ax.annotate(row['대상역'], (row['소요시간_강남'], row['소요시간_여의도']), 
                    xytext=(5,5), textcoords="offset points", fontweight='bold', color='darkred')
                    
    # 대각선 (y=x) - 시간 균형선
    min_val = min(filtered['소요시간_강남'].min(), filtered['소요시간_여의도'].min())
    max_val = max(filtered['소요시간_강남'].max(), filtered['소요시간_여의도'].max())
    ax.plot([min_val, max_val], [min_val, max_val], 'b--', alpha=0.7, label='통근시간 균형선 (y=x)')
    
    ax.set_title("부부 맞춤형 통근 최적역 산점도 (합산시간 최소화)", fontsize=16, fontweight='bold')
    ax.set_xlabel("배우자 A (강남역) 통근 소요시간 (분)", fontsize=12)
    ax.set_ylabel("배우자 B (여의도역) 통근 소요시간 (분)", fontsize=12)
    
    # 영역 설명
    ax.text(min_val+5, max_val-10, "배우자 A (강남) 출퇴근 유리", color='blue', alpha=0.7)
    ax.text(max_val-25, min_val+5, "배우자 B (여의도) 출퇴근 유리", color='blue', alpha=0.7)
    
    ax.legend(loc='upper right')
    ax.grid(True, linestyle=':', alpha=0.6)
    
    save_path = os.path.join(IMG_DIR, 'optimal_commute_scatter.png')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    
    return save_path, top10.head(3)['대상역'].tolist()

# 4. 레이더 차트 (TOP 3 대상)
def draw_radar(top3_stations):
    categories = ['통근 효율 (시간 최소)', '가격 적합성', '생활환경(인프라)', '치안 안전성', '전세가율(유망성)']
    N = len(categories)
    
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    
    # 점수 더미 데이터 부여
    scores = [
        [95, 80, 75, 85, 80],
        [90, 85, 80, 70, 85],
        [85, 75, 90, 80, 70]
    ]
    
    colors = ['#e74c3c', '#3498db', '#2ecc71']
    
    plt.xticks(angles[:-1], categories, size=11)
    ax.set_rlabel_position(0)
    plt.yticks([20, 40, 60, 80, 100], ["20","40","60","80","100"], color="grey", size=10)
    plt.ylim(0, 100)
    
    for i, station in enumerate(top3_stations):
        val = scores[i] + scores[i][:1]
        ax.plot(angles, val, linewidth=2, linestyle='solid', label=f"{i+1}위: {station}역", color=colors[i])
        ax.fill(angles, val, color=colors[i], alpha=0.15)
        
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    plt.title('추천 지역 TOP 3 핵심 지표 밸런스 비교', size=16, y=1.1, fontweight='bold')
    
    save_path = os.path.join(IMG_DIR, 'top3_radar.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return save_path

if __name__ == "__main__":
    gn, yw = load_data()
    print("1.", draw_histogram(gn, yw))
    print("2.", draw_map())
    scatter_path, top3 = draw_scatter(gn, yw)
    print("3.", scatter_path)
    print("Top 3 Stations:", top3)
    print("4.", draw_radar(top3))
    print("Complete!")
