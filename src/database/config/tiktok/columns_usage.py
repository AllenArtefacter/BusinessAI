campaign_columns_usage = {  # Relation to video/account/stream?
    "campaign_cnt_views": "ok",
    "campaign_cnt_engagement": "ok",
    "campaign_cnt_reaches": "ok",
    "campaign_cnt_likes": "ok",
    "campaign_cnt_comments": "ok",
    "campaign_cnt_shares": "ok",
    "campaign_cnt_clicks": "ok",
    "campaign_ads_spend": "ok",
    "campaign_cnt_conversions": "ok",
    "campaign_cnt_orders": "ok",
    "campaign_gmv": "ok",
    "campaign_cnt_impression": "ok",
    "campaign_id": "ok",
    "campaign_name": "mask_any",
    "account_name": "mask_company",
    "dt": "ok",
}

# What is the relation with creator?
# only account is maybelline_indonesia. is account both high level creator manager + posting videos?
# is just high level manager? then why is there account_cnt_profile_visited?

account_columns_usage = {
    "account_name": "mask_company",
    "account_id": "ok",
    "account_avatar_image": "drop",
    "account_region": "ok",
    "account_cnt_posted_video": "ok",
    "account_cnt_livestream": "ok",
    "account_gmv": "ok",
    "account_cnt_follower": "ok",
    "account_cnt_profile_visited": "ok",
    "account_ads_spend": "ok",
    "account_return_value": "ok",
    "account_cnt_ads_click": "ok",
    "account_cnt_video_views": "ok",
    "account_cnt_sales_orders": "ok",
    "dt": "ok",
}

video_columns_usage = {
    "video_id": "ok",
    "dt": "ok",
    "video_cnt_engagement": "ok",
    "video_duration_ms": "ok",
    "video_cnt_views": "ok",
    "video_cnt_likes": "ok",
    "video_cnt_comments": "ok",
    "video_cnt_shares": "ok",
    "video_cnt_orders": "ok",
    "video_gmv": "ok",
    "video_cnt_unit_sales": "ok",
    "video_cnt_buyers": "ok",
    "video_refund": "ok",
    "video_gpv": "ok",
    "publish_time": "ok",
    "title": "mask_any",
    "creator": "mask_name",  # creator_id? like livestream
    "hashtag": "mask_any_words",
    "img": "drop",
    "url": "drop",
    "video_music": "drop",
    "video_cnt_new_followers": "ok",
    "is_brand": "ok",
}

live_columns_usage = {  # link to product/campaign?
    "live_cnt_duration_secs": "ok",
    "live_cnt_views": "ok",
    "live_cnt_likes": "ok",
    "live_cnt_comments": "ok",
    "live_cnt_shares": "ok",
    "live_cnt_peak_views": "ok",
    "live_cnt_engagement": "ok",
    "live_cnt_view_duration": "ok",
    "live_gmv": "ok",
    "live_cnt_orders_paid": "ok",
    "live_cnt_unit_sales": "ok",
    "live_cnt_orders_created": "ok",
    "live_cnt_viewers": "ok",
    "live_cnt_buyers": "ok",
    "is_brand": "ok",
    "dt": "ok",
    "creator": "mask_name",
    "creator_id": "ok",
    "end_time": "ok",
    "nickname": "mask_name",
    "start_time": "ok",
}

product_columns_usage = {
    "product_name": "mask_any_words",
    "product_info": "mask_any",
    "price": "ok",
    "product_sales": "ok",
    "product_cnt_buyers": "ok",
    "product_cnt_orders": "ok",
    "product_cnt_clicks": "ok",
    "product_revenue": "ok",
    "account_name": "mask_company",
    "product_source": "ok",  # id to video? id to livestream?
    "dt": "ok",
}

if __name__ == "__main__":
    from columns_meaning import (
        account_columns,
        campaign_columns,
        live_columns,
        product_columns,
        video_columns,
    )

    # Check columns are the same
    assert set(video_columns) == set(video_columns_usage)
    assert set(live_columns) == set(live_columns_usage)
    assert set(product_columns) == set(product_columns_usage)
    assert set(account_columns) == set(account_columns_usage)
    assert set(campaign_columns) == set(campaign_columns_usage)
