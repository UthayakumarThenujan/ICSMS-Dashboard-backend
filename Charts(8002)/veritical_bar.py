import json
from datetime import datetime
from collections import defaultdict

def bar_chart_extract(sources, cache_data, selected_date_range=None, specific_date=None):
    datasets = []
    all_data = defaultdict(lambda: {'count': 0, 'positive': 0, 'negative': 0, 'neutral': 0})

    def parse_date(date_str):
        # List of possible date formats
        date_formats = ['%Y-%m-%d', '%a %b %d %Y']
        for date_format in date_formats:
            try:
                return datetime.strptime(date_str, date_format)
            except ValueError:
                continue
        raise ValueError(f"time data '{date_str}' does not match any known format")

    def is_date_in_range(date_str, selected_date_range, specific_date):
        date = parse_date(date_str)
        if selected_date_range and len(selected_date_range) == 2:
            start_date = parse_date(selected_date_range[0])
            end_date = parse_date(selected_date_range[1])
            return start_date <= date <= end_date
        elif specific_date:
            current_date = parse_date(specific_date)
            return current_date.date() == date.date()
        return True

    def aggregate_word_cloud_data(all_count):
        total = 0
        category_map_positive = defaultdict(int)
        category_map_negative = defaultdict(int)
        category_map_neutral = defaultdict(int)

        for item in all_count:
            for category in item.get('positive', []):
                if category:
                    total += 1
                    category_map_positive[category] += 1

        for item in all_count:
            for category in item.get('negative', []):
                if category:
                    total += 1
                    category_map_negative[category] += 1

        for item in all_count:
            for category in item.get('neutral', []):
                category_map_neutral[category] += 1

        return [
            [{'category': key, 'percentage': round((value / total) * 100, 2)}
             for key, value in category_map_positive.items()],
            [{'category': key, 'percentage': round((value / total) * 100, 2)}
             for key, value in category_map_negative.items()],
            [{'category': key, 'percentage': round((value / total) * 100, 2)}
             for key, value in category_map_neutral.items()]
        ]

    def transform_data(data):
        categories = ['Product', 'Service', 'Pricing', 'Issues', 'Website']
        transformed_data = []

        for category in categories:
            category_entry = next((entry for entry in data if entry['category'] == category), None)
            if category_entry:
                transformed_data.append({'category': category_entry['category'], 'percentage': category_entry['percentage']})

        return transformed_data

    def update_all_data(all_data, source_data, sentiment):
        for entry in source_data:
            category = entry['category']
            all_data[category][sentiment] += entry['percentage']
            all_data[category]['count'] += 1

    def create_datasets(all_data):
        sentiments = ['positive', 'negative', 'neutral']
        colors = {
            'positive': 'rgba(255, 205, 86, 0.6)',
            'negative': 'rgba(54, 162, 235, 0.6)',
            'neutral': 'rgba(75, 192, 192, 0.6)'
        }

        for sentiment in sentiments:
            data = []
            for category in ['Product', 'Service', 'Pricing', 'Issues', 'Website']:
                if all_data[category][sentiment] > 0:
                    data.append(all_data[category][sentiment] / all_data[category]['count'])
                else:
                    data.append(0)

            datasets.append({
                'label': sentiment.capitalize(),
                'backgroundColor': colors[sentiment],
                'data': data
            })

    for source in sources:
        source_data = []
        try:
            if source == 'call':
                call_count = [item['Categories'] for item in cache_data['call'] if is_date_in_range(item['Date'], selected_date_range, specific_date)]
                source_data = aggregate_word_cloud_data(call_count)
            elif source == 'email':
                email_count = [item['Categories'] for item in cache_data['email'] if is_date_in_range(item['Date'], selected_date_range, specific_date)]
                source_data = aggregate_word_cloud_data(email_count)
            elif source == 'social':
                social_count = [item['Categories'] for item in cache_data['social'] if is_date_in_range(item['Date'], selected_date_range, specific_date)]
                source_data = aggregate_word_cloud_data(social_count)
        except KeyError as e:
            print(f"Data for source '{source}' not found in cache_data: {e}")
            continue

        update_all_data(all_data, transform_data(source_data[0]), 'positive')
        update_all_data(all_data, transform_data(source_data[1]), 'negative')
        update_all_data(all_data, transform_data(source_data[2]), 'neutral')

    create_datasets(all_data)
    return datasets

# Example usage
cache_data = {
    "call": [
        {"Date": "2024-05-28", "Categories": {"positive": ["Product", "Service"], "negative": ["Pricing"], "neutral": ["Issues"]}},
        {"Date": "2024-05-29", "Categories": {"positive": ["Service"], "negative": ["Product"], "neutral": ["Website"]}}
    ],
    "email": [
        {"Date": "2024-05-28", "Categories": {"positive": ["Product"], "negative": ["Service"], "neutral": ["Pricing"]}},
        {"Date": "2024-05-29", "Categories": {"positive": ["Issues"], "negative": ["Website"], "neutral": ["Product"]}}
    ],
    "social": [
        {"Date": "2024-05-28", "Categories": {"positive": ["Website"], "negative": ["Issues"], "neutral": ["Service"]}},
        {"Date": "2024-05-29", "Categories": {"positive": ["Pricing"], "negative": ["Product"], "neutral": ["Service"]}}
    ]
}

selected_date_range = ["2024-05-28", "2024-05-29"]
specific_date = None

datasets = bar_chart_extract(['email', 'social'], cache_data, selected_date_range, specific_date)
print(json.dumps(datasets, indent=2))
