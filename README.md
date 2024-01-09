# Reviews Scraper for Play Store and App Store
A simple Python Dash web app to scrape reviews for the Google Play Store and the Apple App Store.

The app is deployed on vercel at the following link: [Revscrap](https://revscrap.vercel.app/).

## Revscraper
The web app consists in just a search bar, in which to insert the url of the app you want to download reviews.  
The url has to be a valid Google Play Store or Apple App Store link.

![image](https://github.com/andreaponti5/revscrap/assets/59694427/6649da51-5b1c-4e4e-bd6d-4b712a19fffe)

The output is a CSV file with the following columns:
- `Datetime`: date of the review (_%d/%m%Y_).
- `Username`: user that wrote the review.
- `Review`: text of the review (both title and content).
- `Rating`: number of stars assigned to the review (1-5).
- `Reply`: text of the reply to the review.
- `Reply Datetime`: date of the reply (_%d/%m%Y_).
- `Thumbs Up`: number of thumbs up (only for Google Play Store).

## Requirements
Vercel currently supports only `Python 3.9`.

The library used are:
- `dash`: as the main framework.
- `numpy`: to manage the csv dataset. Numpy has been used instead of Pandas to keep the serverless function lightweight.
- `google-play-scraper`: to scrape data from the Google Play Store.
- `app-store-scraper`: to scrape data from the Apple App Store.
