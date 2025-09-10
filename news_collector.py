import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from datetime import datetime, timedelta
import urllib.parse
import time
import os

class NewsCollector:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.keywords = [
            "외국인 아르바이트",
            "외국인 알바", 
            "외국인 채용",
            "외국인 구인",
            "외국인 근로자 채용",
            "외국인 직원 모집"
        ]
    
    def search_naver_news(self, query, days_back=7):
        """네이버 뉴스를 검색하여 결과를 반환"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        encoded_query = urllib.parse.quote(query)
        url = f"https://search.naver.com/search.naver?where=news&query={encoded_query}&sort=1"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            news_list = []
            
            # 뉴스 아이템 찾기
            news_items = soup.find_all('div', class_='news_area')
            
            for item in news_items:
                try:
                    # 제목과 링크
                    title_elem = item.find('a', class_='news_tit')
                    if not title_elem:
                        continue
                        
                    title = title_elem.text.strip()
                    link = title_elem['href']
                    
                    # 요약
                    summary_elem = item.find('div', class_='news_dsc')
                    summary = summary_elem.text.strip() if summary_elem else ""
                    
                    # 언론사
                    press_elem = item.find('a', class_='info press')
                    press = press_elem.text.strip() if press_elem else ""
                    
                    # 날짜
                    date_elem = item.find('span', class_='info')
                    date_str = date_elem.text.strip() if date_elem else ""
                    
                    # 날짜 파싱 및 필터링
                    article_date = self.parse_date(date_str)
                    
                    if article_date and article_date >= start_date:
                        news_list.append({
                            'title': title,
                            'summary': summary,
                            'press': press,
                            'date': date_str,
                            'link': link,
                            'parsed_date': article_date.isoformat(),
                            'keyword': query,
                            'collected_at': datetime.now().isoformat()
                        })
                
                except Exception as e:
                    print(f"아이템 파싱 오류: {e}")
                    continue
            
            print(f"'{query}' 검색 완료: {len(news_list)}개 뉴스 수집")
            return news_list
        
        except Exception as e:
            print(f"'{query}' 검색 중 오류: {e}")
            return []
    
    def parse_date(self, date_str):
        """날짜 문자열을 datetime 객체로 변환"""
        try:
            now = datetime.now()
            
            if "시간 전" in date_str:
                hours = int(date_str.split("시간")[0]) if date_str.split("시간")[0].isdigit() else 0
                return now - timedelta(hours=hours)
            elif "분 전" in date_str:
                return now
            elif "일 전" in date_str:
                days = int(date_str.split("일")[0]) if date_str.split("일")[0].isdigit() else 0
                return now - timedelta(days=days)
            elif "." in date_str:
                # 2024.01.01 형태
                date_parts = date_str.split(".")
                if len(date_parts) >= 3:
                    year = int(date_parts[0])
                    month = int(date_parts[1])
                    day = int(date_parts[2])
                    return datetime(year, month, day)
            
            return now
        except:
            return datetime.now()
    
    def collect_all_news(self, days_back=7):
        """모든 키워드로 뉴스 수집"""
        all_news = []
        
        print("뉴스 수집 시작...")
        for i, keyword in enumerate(self.keywords):
            print(f"진행률: {i+1}/{len(self.keywords)} - '{keyword}' 검색 중...")
            
            news_results = self.search_naver_news(keyword, days_back)
            all_news.extend(news_results)
            
            # API 호출 제한을 위한 대기
            time.sleep(2)
        
        # 중복 제거 (제목 기준)
        seen_titles = set()
        unique_news = []
        for news in all_news:
            if news['title'] not in seen_titles:
                seen_titles.add(news['title'])
                unique_news.append(news)
        
        print(f"총 {len(unique_news)}개의 고유 뉴스 수집 완료")
        return unique_news
    
    def save_news(self, news_data, filename='news_data.json'):
        """뉴스 데이터를 JSON 파일로 저장"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(news_data, f, ensure_ascii=False, indent=2)
            print(f"뉴스 데이터를 {filename}에 저장했습니다.")
        except Exception as e:
            print(f"데이터 저장 오류: {e}")
    
    def load_news(self, filename='news_data.json'):
        """저장된 뉴스 데이터 로드"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"데이터 로드 오류: {e}")
            return []

def main():
    collector = NewsCollector()
    
    # 뉴스 수집 (최근 7일)
    news_data = collector.collect_all_news(days_back=7)
    
    # 데이터 저장
    collector.save_news(news_data)
    
    print(f"\n=== 수집 완료 ===")
    print(f"총 뉴스 수: {len(news_data)}")
    
    # 키워드별 통계
    keyword_stats = {}
    for news in news_data:
        keyword = news['keyword']
        keyword_stats[keyword] = keyword_stats.get(keyword, 0) + 1
    
    print("\n키워드별 뉴스 수:")
    for keyword, count in keyword_stats.items():
        print(f"  {keyword}: {count}개")

if __name__ == "__main__":
    main()