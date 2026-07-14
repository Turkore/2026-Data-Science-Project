This is a project for a Data Science course in the 2026-1 semester.

Does Kindness Sell? Impact of Linguistic Signals on Dangun Purchase Conversions
This project investigates whether a seller's polite tone (friendliness) or category-specific information has a greater impact on purchase conversion rates (wishlist and chat rates) in the C2C secondhand market (Dangun).

Used Tech
Language and Libraries: Python, Playwright, Beautifulsoup, Pandas, Statsmodels
Methodology: Multiple Linear Regression(OLS) with HC3 Robust Standard Errors

My Role in the project: Data Preprocessing and Crawling
1. Dynamic Web Crawling
  1. Designed a dynamic web scraoer using Playwright to handle asynchronous XHR/Fetch requests and scroll interactions on Dangun.
  2. Implemented random sampling across 350 regions(average) to eliminate spatial bias.
  3. Collected a total of 4,400+ listings across 6 distinct categories(Airpods 4, Medicube, Nintendo, Ikea Trolley, Stokke Baby Chair, Constantin Bicycle)

2. Data Cleansing and Flitering
  1. Outlier Removal: Filtered out bait listings with unrealistic prices.
  2. Noise Reduction: Automatically excluded non-selling posts(e.g., "looking to buy" or accessory-only listings) using text-matching rules.

3. Feature Engineering(Regex)
   1. Parsed raw, unstructured string stsatistics into numerical indicatiors(Whishlists,Chart,Views etc.) using regular expressions(re.sub) to construct the target conversion metrics:
   2. Wishlist Conversion Rate = Wishlists/Views
   3. Chart Conversion Rate = Charts/Views

4. Key findings and Conclusion:
   1. Politeness vs. Information: "Polite" linguistic features (emojis, honorific endings, friendliness markers) did not increase purchase conversions.
   2. Category Keywords Matter: Including key domain-specific words (such as item specs and conditions) significantly boosted wishlist conversion rates by 8% to 16% in the Beauty, AirPods, and Nintendo Switch categories.
   3. Conclusion: Secondhand buyers are not driven by a seller’s emotional warmth, but by practical, high-density item information.
      
