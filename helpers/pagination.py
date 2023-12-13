import math
from flask import request
from helpers.contants import ITEMS_PER_PAGE

def get_pagination_data(item_count_in_db):
    count = 0
    idx = 0

    if item_count_in_db:
        count = int(item_count_in_db)

    if "idx" in request.args:
        idx = int(request.args["idx"])

    page_count = math.ceil(count / ITEMS_PER_PAGE)
    last_idx = max(0, page_count - 1)
    count_on_next_idx = min(ITEMS_PER_PAGE, count - (idx + 1) * ITEMS_PER_PAGE)
    page_numbers = range(1, page_count + 1)

    return idx, last_idx, count, count_on_next_idx, page_numbers
