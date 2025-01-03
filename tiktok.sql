# Can you tell me how does Indonesia MNY perform on TikTok
select *
from (select account_name,
             account_id,
             account_avatar_image,
             account_region,
             sum(ifnull(account_cnt_posted_video, 0))    as account_cnt_posted_video,
             sum(ifnull(account_cnt_livestream, 0))      as account_cnt_livestream,
             sum(ifnull(account_gmv, 0))                 as account_gmv,
             sum(ifnull(account_cnt_follower, 0))        as account_cnt_follower,
             sum(ifnull(account_cnt_profile_visited, 0)) as account_cnt_profile_visited,
             sum(ifnull(account_ads_spend, 0))           as account_ads_spend,
             sum(ifnull(account_return_value, 0))        as account_return_value,
             sum(ifnull(account_cnt_ads_click, 0))       as account_cnt_ads_click,
             sum(ifnull(account_cnt_video_views, 0))     as account_cnt_video_views,
             sum(ifnull(account_cnt_sales_orders, 0))    as account_cnt_sales_orders
      from 'tiktoknav_poc.dws_account_daily'
      where dt <= 20230331
      group by account_name,
               account_id,
               account_avatar_image,
               account_region) t1
         left join
     (select username,
             total_likes,
             total_shares,
             total_comments,
             engagement_rate
      from 'tiktoknav_poc.ods_exolyt_accounts_account_full'
      where dt = '2023-03-31') t2
     on
         t1.account_name = t2.username;


# Show me the sources of GMV contribution on TikTok
with gmv_sum_video as
    (select account_name,
            sum(ifnull(product_revenue, 0)) as gmv
     from 'tiktoknav_poc.dws_product_daily'
     where dt = 20230301
       and product_source = 'video'
     group by account_name)
   , gmv_sum_livestream as
    (select account_name,
            sum(ifnull(product_revenue, 0)) as gmv
     from 'tiktoknav_poc.dws_product_daily'
     where dt = 20230301
       and product_source = 'livestream'
     group by account_name)
select product_name,
       product_revenue / t2.gmv as gmv_contribution,
       product_source
from 'tiktoknav_poc.dws_product_daily' t1
         left join
     gmv_sum_video t2
     on t1.account_name = t2.account_name
where t1.product_source = 'video'
  and t1.dt = 20230301
union all
select product_name,
       product_revenue / t2.gmv as gmv_contribution,
       product_source,
from 'tiktoknav_poc.dws_product_daily' t1
         left join
     gmv_sum_livestream t2
     on t1.account_name = t2.account_name
where t1.product_source = 'livestream'
  and t1.dt = 20230301;


# Show the  most liked hashtags for Indonesia Maybelline
with top_hashtag_MNY as (SELECT dt,
                                split(hashtag, '|') as r
                         FROM 'itg-tiktoknav-gbl-ww-dv.tiktoknav_poc.dws_video_daily'
                         order by hashtag desc)
select r, count(r)
from top_hashtag_MNY,
     unnest(r) r
where dt = 20230330
group by r
order by count(r) desc
limit 10
;

# Show the Top 10 selling products in the MNY livestreaming yesterday
select product_name,
       product_cnt_orders
from 'itg-tiktoknav-gbl-ww-dv.tiktoknav_poc.dws_product_daily'
where dt = 20230331
  and account_name = 'maybelline_indonesia'
  and product_source = 'livestream'
order by product_cnt_orders desc
limit 10;

# Show me the performance of Indonesia MNY TikTok videos for last 7 days. And in a line chart?
select *
from 'itg-tiktoknav-gbl-ww-dv.tiktoknav_poc.dws_video_daily'
where parse_date('%Y%m%d', cast(dt AS String)) >=
      date_sub(parse_date('%Y%m%d', cast(20230331 AS String)), interval 6 day)
  and creator = 'maybelline_indonesia'
order by video_id,
         dt desc;


# What’s the Indonesia MNY video traffice distribution is like, maybe with a pie chart?

