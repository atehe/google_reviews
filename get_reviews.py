import requests, json

NUM_PAGES = 3



def get_reviews(url):
    url_split = url.split("!2m2!1i")
    review_data= []
    for i in range(NUM_PAGES):

        page_url = f'{url_split[0]}{"!2m2!1i"}{i}{url_split[-1]}'
        response = requests.get(page_url)
        
        # cleaning up and making response parseable
        response_text =response.text[5:]
        response_text = json.loads(response_text) 

        reviews = response_text[2] 

        page_review_dict = {'url': page_url, 'reviews': []}
        for review in reviews:
            page_review_dict['reviews'].append(review)
        
        review_data.append(page_review_dict)
    
    return review_data



print(get_reviews('https://www.google.com/maps/preview/review/listentitiesreviews?authuser=0&hl=en&gl=uk&pb=!1m2!1y5221390517247707075!2y12871855046015027610!2m2!1i0!2i10!3e1!4m5!3b1!4b1!5b1!6b1!7b1!5m2!1s49XaYs_ND9SBhbIP7Ky4gAo!7e81'))

        

    


