def zip_paginate(p):
    items = p.items
    total = p.total
    page = p.page
    per_page = p.per_page
    return page, per_page, total, items
