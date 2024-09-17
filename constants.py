import urllib.parse

keyword = "Python Backend Developer"
main_url = f"https://www.linkedin.com/jobs/search?keywords={urllib.parse.quote(keyword)}&location=Morocco&geoId=102787409&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0"
anchors_xpath = "//a[contains(@href, '/jobs/view')]"
modal_dismiss_xpath = "//button[contains(@data-tracking-control-name, 'public_jobs_contextual-sign-in-modal_modal_dismiss')]"
title_xpath = "//h2[contains(@class, 'top-card-layout__title')]"
job_title_xpath = "//h1[contains(@class, 'top-card-layout__title')]"


job_description_xpath = "//div[contains(@class, 'description__text')]"
job_company_name_xpath = "//a[contains(@class, 'topcard__org-name-link topcard__flavor--black-link')]"
job_location_xpath = "//span[contains(@class, 'topcard__flavor topcard__flavor--bullet')]"
job_age_xpath = "//span[contains(@class, 'posted-time-ago__text topcard__flavor--metadata')]"




card_port_xpath = "//a[contains(@class, 'base-card__full-link')]"

scrapping_source = 'LinkedIn'


url_index_spliter = '&refId'