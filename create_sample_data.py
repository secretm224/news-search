import json
from datetime import datetime, timedelta
import random

def create_sample_news_data():
    """샘플 뉴스 데이터 생성"""
    
    keywords = [
        "외국인 아르바이트",
        "외국인 알바", 
        "외국인 채용",
        "외국인 구인",
        "외국인 근로자 채용",
        "외국인 직원 모집"
    ]
    
    press_list = [
        "연합뉴스", "KBS", "MBC", "SBS", "조선일보", "중앙일보", "동아일보",
        "한겨레", "경향신문", "서울경제", "매일경제", "한국경제", "아시아경제",
        "뉴시스", "뉴스1", "이데일리", "헤럴드경제", "파이낸셜뉴스"
    ]
    
    sample_titles = [
        "외국인 근로자 대량 채용... 인력난 해소 기대",
        "편의점·카페 외국인 알바생 급증, 최저임금 논란",
        "외국인 아르바이트 비자 발급 간소화 추진",
        "서울시, 외국인 구인구직 지원센터 확대 운영",
        "외국인 근로자 채용 박람회 성황... 300개 기업 참가",
        "코로나 이후 외국인 알바 시장 회복세",
        "외국인 학생 아르바이트 시간 제한 완화 검토",
        "음식점 사장들 '외국인 직원 없으면 운영 어려워'",
        "외국인 근로자 불법고용 단속 강화",
        "대학가 외국인 알바생 비중 30% 넘어서",
        "외국인 계절근로자 모집 확대... 농가 인력난 해소",
        "외국인 배달 라이더 증가세... 플랫폼 업체 적극 채용",
        "제조업체 외국인 근로자 의존도 심화",
        "외국인 직원 한국어 교육 지원 프로그램 확산",
        "건설현장 외국인 근로자 안전교육 의무화"
    ]
    
    sample_summaries = [
        "인력난에 시달리는 국내 기업들이 외국인 근로자 채용을 확대하고 있다. 특히 서비스업과 제조업 분야에서 외국인 근로자에 대한 수요가 급증하고 있으며, 정부도 관련 제도 개선을 검토하고 있다.",
        "최근 편의점과 카페 등 소상공인 업체에서 외국인 아르바이트생 채용이 늘고 있다. 한국인 구직자가 기피하는 야간 근무나 주말 근무를 외국인들이 담당하는 경우가 많아졌다.",
        "코로나19로 위축되었던 외국인 근로자 시장이 회복세를 보이고 있다. 정부는 외국인 근로자 비자 발급 절차를 간소화하고 채용 절차를 개선하는 방안을 추진하고 있다.",
        "외국인 근로자들의 불법고용 문제가 지속되면서 정부가 단속을 강화하고 있다. 사업주들에게는 합법적인 채용 절차 준수를 당부하고 있다.",
        "대학가 주변 아르바이트 시장에서 외국인 학생들의 비중이 급속히 늘고 있다. 특히 어학연수생과 교환학생들의 아르바이트 참여가 활발하다."
    ]
    
    sample_news = []
    
    # 최근 7일 데이터 생성
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        
        # 하루에 3-8개 뉴스 생성
        daily_news_count = random.randint(3, 8)
        
        for j in range(daily_news_count):
            keyword = random.choice(keywords)
            title = random.choice(sample_titles)
            summary = random.choice(sample_summaries)
            press = random.choice(press_list)
            
            # 시간 랜덤화
            random_hour = random.randint(0, 23)
            random_minute = random.randint(0, 59)
            article_date = date.replace(hour=random_hour, minute=random_minute, second=0, microsecond=0)
            
            news_item = {
                'title': title,
                'summary': summary,
                'press': press,
                'date': f"{i}일 전" if i > 0 else f"{random_hour}시간 전",
                'link': f"https://news.naver.com/sample/{random.randint(1000, 9999)}",
                'parsed_date': article_date.isoformat(),
                'keyword': keyword,
                'collected_at': datetime.now().isoformat()
            }
            
            sample_news.append(news_item)
    
    return sample_news

def save_sample_data():
    """샘플 데이터를 파일로 저장"""
    sample_news = create_sample_news_data()
    
    with open('news_data.json', 'w', encoding='utf-8') as f:
        json.dump(sample_news, f, ensure_ascii=False, indent=2)
    
    print(f"샘플 뉴스 데이터 {len(sample_news)}개를 생성했습니다.")
    
    # 일별 통계
    from collections import defaultdict
    daily_counts = defaultdict(int)
    for news in sample_news:
        try:
            parsed_date = datetime.fromisoformat(news['parsed_date'])
            date_str = parsed_date.strftime('%Y-%m-%d')
            daily_counts[date_str] += 1
        except:
            continue
    
    print("\n일별 뉴스 수:")
    for date, count in sorted(daily_counts.items(), reverse=True):
        print(f"  {date}: {count}개")

if __name__ == "__main__":
    save_sample_data()