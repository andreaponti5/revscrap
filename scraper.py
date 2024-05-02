import csv
import sys
from datetime import datetime
from io import StringIO
from typing import Tuple

import numpy as np
from app_store_scraper import AppStore
from google_play_scraper import Sort, reviews, reviews_all


def get_app_id_name_from_appstore_url(
        url: str
) -> Tuple[str, str]:
    """
    Extract the app id and name from an App Store url.

    :param url: the App Store url (e.g., https://apps.apple.com/it/app/enel-x-way/id1377291789)
    :return: the app id and the app name.
    """
    return url.split("/")[-1].replace("id", ""), url.split("/")[-2]


def get_app_id_from_playstore_url(
        url: str
) -> str:
    """
    Extract the app id from a Play Store url.

    :param url: the Play Store url (e.g.,
        https://play.google.com/store/apps/details?id=com.enel.mobile.recharge2&hl=it&gl=US)
    :return: the app id.
    """
    return url.split("/")[-1].split("?")[-1].split("&")[0].replace("id=", "")


def retrieve_appstore_reviews(
        app_name: str,
        app_id: str,
        country: str = "it",
        how_many: int = sys.maxsize,
) -> list[dict]:
    """
    Retrieve a list of reviews for a given app from the App Store.

    :param app_name: the name of the app. You can find it in the App Store url.
        E.g., given the url https://apps.apple.com/it/app/enel-x-way/id1377291789, the app name would be "enel-x-way"
    :param app_id: the id of the app. You can find it in the App Store url.
        E.g., given the url https://apps.apple.com/it/app/enel-x-way/id1377291789, the app id would be "1377291789"
    :param country: the considered country to retrieve the reviews.
    :param how_many: the number of reviews to retrieve. By default, all the reviews will be returned.
    :return: a list of dictionaries containing reviews.
        Each review has the following parameter:
            - 'date': datetime of the review.
            - 'developerResponse': dictionary containing the id, body and date of the response.
            - 'review': the text of the review.
            - 'rating': the number of stars of the review (1-5).
            - 'isEdited': boolean indicating whether the review has been modified or not.
            - 'title': the title of the review.
            - 'userName': the user that created the review.
    """
    app_store = AppStore(country=country, app_name=app_name, app_id=app_id)
    app_store.review(how_many=how_many)
    return app_store.reviews[:how_many]


def retrieve_playstore_reviews(
        app_id: str,
        lang: str = 'it',
        country: str = "it",
        how_many: int = 100000,
) -> list[dict]:
    """
    Retrieve a list of reviews for a given app from the Google Play Store.

    :param app_id: the id of the app. You can find it in the Play Store url.
        E.g., given the url https://play.google.com/store/apps/details?id=com.enel.mobile.recharge2&hl=it&gl=US,
        the app id would be "com.enel.mobile.recharge2"
    :param lang: the considered language to retrieve the reviews.
    :param country: the considered country to retrieve the reviews.
    :param how_many: the number of reviews to retrieve. If None, all the reviews will be returned.
    :return: a list of dictionaries containing reviews.
        Each review has the following parameter:
            - 'reviewId': the id of the review.
            - 'userName': the user that created the review.
            - 'userImage': the image url of the user.
            - 'content': the text of the review.
            - 'score': the number of stars of the review (1-5).
            - 'thumbsUpCount': the number of thumbs up.
            - 'reviewCreatedVersion': the version of the app considered in the review.
            - 'at': datetime of the review.
            - 'replyContent': the response to the review.
            - 'repliedAt': datetime of the response.
            - 'appVersion': the current version of the app.
    """
    # Retrieve max 200 reviews per request to avoid problems.
    # 200 is the maximum number of reviews displayed in a page
    result, continuation_token = [], None
    while len(result) < how_many:
        new_result, continuation_token = reviews(
            app_id=app_id,
            continuation_token=continuation_token,
            lang=lang,
            country=country,
            sort=Sort.NEWEST,
            filter_score_with=None,
            count=150
        )
        if not new_result:
            break
        result.extend(new_result)
    return result


def formate_appstore_reviews(
        revs: list[dict]
) -> np.array:
    """
    Format the reviews obtained calling `retrieve_appstore_reviews` in a pandas dataframe.

    :param revs: a list of dictionaries containing reviews from the App Store.
        Each review has the following parameter:
            - 'date': datetime of the review.
            - 'developerResponse': dictionary containing the id, body and date of the response.
            - 'review': the text of the review.
            - 'rating': the number of stars of the review (1-5).
            - 'isEdited': boolean indicating whether the review has been modified or not.
            - 'title': the title of the review.
            - 'userName': the user that created the review.
    :return: A dataframe containing the reviews with the following columns: "datetime", "username",
        "review", "rating", "reply", "reply_datetime", "thumbsup".
    """
    revs_cols = ["date", "userName", "review", "rating", "replyContent", "repliedAt"]
    dataset_cols = ["Datetime", "Username", "Review", "Rating", "Reply", "Reply Datetime"]
    # Preprocess results
    for rev in revs:
        # Concat title and review
        rev["review"] = rev["title"] + rev["review"]
        # Add response info
        if "developerResponse" in rev:
            rev["replyContent"] = rev["developerResponse"]["body"]
            rev["repliedAt"] = datetime.strptime(rev["developerResponse"]["modified"], "%Y-%m-%dT%H:%M:%SZ")
        else:
            rev["replyContent"], rev["repliedAt"] = "", ""
    return _format_generic(revs, dataset_cols, revs_cols)


def format_playstore_reviews(
        revs: list[dict]
) -> np.array:
    """
    Format the reviews obtained calling `retrieve_playstore_reviews` in a pandas dataframe.

    :param revs: a list of dictionaries containing reviews from the Play Store.
        Each review has the following parameter:
            - 'reviewId': the id of the review.
            - 'userName': the user that created the review.
            - 'userImage': the image url of the user.
            - 'content': the text of the review.
            - 'score': the number of stars of the review (1-5).
            - 'thumbsUpCount': the number of thumbs up.
            - 'reviewCreatedVersion': the version of the app considered in the review.
            - 'at': datetime of the review.
            - 'replyContent': the response to the review.
            - 'repliedAt': datetime of the response.
            - 'appVersion': the current version of the app.
    :return: A dataframe containing the reviews with the following columns: "datetime", "username",
        "review", "rating", "reply", "reply_datetime", "thumbsup".
    """
    revs_cols = ["at", "userName", "content", "score", "replyContent", "repliedAt", "thumbsUpCount"]
    dataset_cols = ["Datetime", "Username", "Review", "Rating", "Reply", "Reply Datetime", "Thumbs Up"]
    return _format_generic(revs, dataset_cols, revs_cols)


def numpy_to_str(
        dataset: np.array
) -> str:
    text_stream = StringIO()
    # Use the csv.writer to handle the CSV writing with proper quoting and escaping
    csv_writer = csv.writer(text_stream, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for row in dataset:
        csv_writer.writerow(row)
    result_string = text_stream.getvalue()
    text_stream.close()
    return result_string


def _format_generic(revs, dataset_cols, revs_cols):
    dataset = {key: [] for key in dataset_cols}
    for rev in revs:
        for rev_key, dataset_key in zip(revs_cols, dataset_cols):
            # Remove all new line in string attributes to avoid problem when importing the csv in Excel
            dataset[dataset_key].append(rev[rev_key].replace("\n", "") if isinstance(rev[rev_key], str)
                                        else rev[rev_key])
    # Datetime to string
    dataset["Datetime"] = ["" if value is None or isinstance(value, str) else value.strftime("%d/%m/%Y")
                           for value in dataset["Datetime"]]
    dataset["Reply Datetime"] = ["" if value is None or isinstance(value, str) else value.strftime("%d/%m/%Y")
                                 for value in dataset["Reply Datetime"]]
    return np.concatenate([np.array([list(dataset.keys())]), np.array(list(dataset.values())).T])
