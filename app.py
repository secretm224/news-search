import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from news_collector import NewsCollector

st.set_page_config(
    page_title="외국인 아르바이트 채용공고 뉴스",
    page_icon="📰",
    layout="wide"
)

@st.cache_data(ttl=3600)  # 1시간 캐시
def load_news_data():
    """뉴스 데이터 로드"""
    collector = NewsCollector()
    return collector.load_news()

def filter_news_by_date(news_data, days_back):
    """날짜로 뉴스 필터링"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    filtered_news = []
    for news in news_data:
        try:
            parsed_date = datetime.fromisoformat(news['parsed_date'].replace('Z', '+00:00'))
            if parsed_date.replace(tzinfo=None) >= start_date:
                filtered_news.append(news)
        except:
            # 날짜 파싱 실패시 포함
            filtered_news.append(news)
    
    return filtered_news

def get_daily_stats(news_data):
    """일별 뉴스 통계 생성"""
    daily_counts = defaultdict(int)
    daily_news = defaultdict(list)
    
    for news in news_data:
        try:
            parsed_date = datetime.fromisoformat(news['parsed_date'].replace('Z', '+00:00'))
            date_str = parsed_date.strftime('%Y-%m-%d')
            daily_counts[date_str] += 1
            daily_news[date_str].append(news)
        except:
            continue
    
    return daily_counts, daily_news

def estimate_popularity_score(news):
    """뉴스 인기도 점수 추정 (제목 길이, 요약 길이, 언론사 등 고려)"""
    score = 0
    
    # 제목에 중요 키워드가 포함된 경우 점수 추가
    important_keywords = ['채용', '모집', '구인', '급구', '대량', '상시']
    for keyword in important_keywords:
        if keyword in news['title']:
            score += 10
    
    # 요약이 충실한 경우 점수 추가
    if news['summary'] and len(news['summary']) > 50:
        score += 5
    
    # 주요 언론사인 경우 점수 추가
    major_press = ['연합뉴스', 'KBS', 'MBC', 'SBS', '조선일보', '중앙일보', '동아일보']
    if any(press in news['press'] for press in major_press):
        score += 15
    
    # 최신 뉴스에 가산점
    try:
        parsed_date = datetime.fromisoformat(news['parsed_date'].replace('Z', '+00:00'))
        hours_ago = (datetime.now() - parsed_date.replace(tzinfo=None)).total_seconds() / 3600
        if hours_ago < 24:
            score += 10
        elif hours_ago < 48:
            score += 5
    except:
        pass
    
    return score

def get_top_news_by_day(daily_news, top_n=3):
    """일별 인기 뉴스 top N 추출"""
    top_news_by_day = {}
    
    for date, news_list in daily_news.items():
        # 인기도 점수로 정렬
        scored_news = []
        for news in news_list:
            score = estimate_popularity_score(news)
            scored_news.append((score, news))
        
        # 점수 순으로 정렬해서 상위 N개 선택
        scored_news.sort(key=lambda x: x[0], reverse=True)
        top_news_by_day[date] = [news for score, news in scored_news[:top_n]]
    
    return top_news_by_day

def main():
    st.title("📰 외국인 아르바이트 채용공고 뉴스")
    st.markdown("---")
    
    # 탭 생성
    tab1, tab2 = st.tabs(["📊 대시보드", "📰 전체 뉴스"])
    
    # 사이드바 설정
    st.sidebar.header("필터 설정")
    
    # 날짜 범위 설정
    date_range = st.sidebar.selectbox(
        "보기 기간",
        ["1일", "3일", "1주일"],
        index=2
    )
    
    days_map = {"1일": 1, "3일": 3, "1주일": 7}
    days_back = days_map[date_range]
    
    # 뉴스 데이터 로드
    with st.spinner("뉴스 데이터 로딩 중..."):
        news_data = load_news_data()
    
    if not news_data:
        st.error("저장된 뉴스 데이터가 없습니다. 먼저 `python news_collector.py`를 실행해서 데이터를 수집해주세요.")
        
        # 데이터 수집 버튼
        if st.button("지금 뉴스 데이터 수집하기", type="primary"):
            with st.spinner("뉴스 수집 중... (약 1-2분 소요)"):
                collector = NewsCollector()
                fresh_news = collector.collect_all_news(days_back=7)
                collector.save_news(fresh_news)
                st.success("뉴스 데이터 수집 완료!")
                st.rerun()
        return
    
    # 날짜 필터링
    filtered_news = filter_news_by_date(news_data, days_back)
    
    if not filtered_news:
        st.info("선택한 기간에 해당하는 뉴스가 없습니다.")
        return
    
    # 키워드 필터
    available_keywords = list(set([news['keyword'] for news in filtered_news]))
    selected_keywords = st.sidebar.multiselect(
        "키워드 필터",
        available_keywords,
        default=available_keywords
    )
    
    # 키워드로 필터링
    if selected_keywords:
        filtered_news = [news for news in filtered_news if news['keyword'] in selected_keywords]
    
    # 날짜순 정렬
    filtered_news.sort(key=lambda x: datetime.fromisoformat(x['parsed_date'].replace('Z', '+00:00')), reverse=True)
    
    # 일별 통계 및 인기 뉴스 생성
    daily_counts, daily_news = get_daily_stats(filtered_news)
    top_news_by_day = get_top_news_by_day(daily_news)
    
    # 대시보드 탭
    with tab1:
        st.header("📊 뉴스 통계 대시보드")
        
        # 기본 통계
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 뉴스 수", len(filtered_news))
        with col2:
            if filtered_news:
                latest_date = max([datetime.fromisoformat(news['parsed_date'].replace('Z', '+00:00')) for news in filtered_news])
                st.metric("최신 뉴스", latest_date.strftime('%Y-%m-%d'))
        with col3:
            unique_press = len(set([news['press'] for news in filtered_news if news['press']]))
            st.metric("언론사 수", unique_press)
        
        st.markdown("---")
        
        # 일별 뉴스 수 차트
        if daily_counts:
            st.subheader("📈 일별 뉴스 수")
            
            # 데이터 준비
            dates = sorted(daily_counts.keys())
            counts = [daily_counts[date] for date in dates]
            
            # 차트 생성
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=dates,
                y=counts,
                text=counts,
                textposition='auto',
                marker_color='lightblue'
            ))
            fig.update_layout(
                title=f"최근 {date_range} 일별 뉴스 수",
                xaxis_title="날짜",
                yaxis_title="뉴스 수",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # 키워드별 차트
            keyword_counts = Counter([news['keyword'] for news in filtered_news])
            if len(keyword_counts) > 1:
                st.subheader("🏷️ 키워드별 뉴스 분포")
                
                fig2 = px.pie(
                    values=list(keyword_counts.values()),
                    names=list(keyword_counts.keys()),
                    title="키워드별 뉴스 비율"
                )
                st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("---")
        
        # 일별 인기 뉴스 TOP 3
        if top_news_by_day:
            st.subheader("🔥 일별 인기 뉴스 TOP 3")
            
            for date in sorted(top_news_by_day.keys(), reverse=True):
                with st.expander(f"📅 {date} ({len(daily_news[date])}개 뉴스)"):
                    top_news = top_news_by_day[date]
                    
                    for i, news in enumerate(top_news, 1):
                        st.markdown(f"**{i}. [{news['title']}]({news['link']})**")
                        st.write(f"📰 {news['press']} | 🏷️ {news['keyword']}")
                        if news['summary']:
                            st.write(f"💬 {news['summary'][:100]}...")
                        st.markdown("---")
    
    # 전체 뉴스 탭
    with tab2:
        st.header("📰 전체 뉴스 목록")
        
        # 뉴스 표시
        for i, news in enumerate(filtered_news):
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"### [{news['title']}]({news['link']})")
                    if news['summary']:
                        st.write(news['summary'])
                    st.caption(f"키워드: {news['keyword']}")
                
                with col2:
                    st.write(f"**언론사:** {news['press']}")
                    st.write(f"**날짜:** {news['date']}")
                
                st.markdown("---")
        
        # 데이터 다운로드
        if filtered_news:
            df = pd.DataFrame(filtered_news)
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSV로 다운로드",
                data=csv,
                file_name=f"외국인_아르바이트_뉴스_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    # 데이터 갱신 버튼
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 뉴스 데이터 갱신", type="secondary"):
        with st.spinner("새로운 뉴스 수집 중... (약 1-2분 소요)"):
            collector = NewsCollector()
            fresh_news = collector.collect_all_news(days_back=7)
            collector.save_news(fresh_news)
            st.sidebar.success("데이터 갱신 완료!")
            st.rerun()
    
    # 사용법 안내
    with st.expander("💡 사용법 안내"):
        st.markdown("""
        ### 이 앱의 기능
        - **미리 수집된 뉴스 표시**: 외국인 아르바이트 관련 뉴스를 미리 수집해서 빠르게 보여줍니다
        - **날짜 필터링**: 1일, 3일, 1주일 단위로 뉴스를 필터링할 수 있습니다
        - **키워드 필터링**: 특정 키워드만 골라서 볼 수 있습니다
        - **실시간 갱신**: 뉴스 데이터 갱신 버튼으로 최신 뉴스를 수집할 수 있습니다
        
        ### 데이터 수집 키워드
        - 외국인 아르바이트
        - 외국인 알바
        - 외국인 채용
        - 외국인 구인
        - 외국인 근로자 채용
        - 외국인 직원 모집
        
        ### 수동 데이터 수집
        터미널에서 `python news_collector.py`를 실행하면 최신 뉴스를 수집할 수 있습니다.
        """)

if __name__ == "__main__":
    main()