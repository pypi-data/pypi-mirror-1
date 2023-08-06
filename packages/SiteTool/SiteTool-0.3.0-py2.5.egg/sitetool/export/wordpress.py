import MySQLdb
import os.path
import logging

from sitetool.exception import TemplateError
from sitetool.convert.blog import build_rst_post

log = logging.getLogger(__name__)

def dict_fetchall(cursor):
    rows = cursor.fetchall()
    res = []
    for row in rows:
        dictionary = {}
        for i in range(len(row)):
            val = row[i]
            if isinstance(val, str):
                val = val.decode('utf-8')
            dictionary[cursor.description[i][0]] = val
        res.append(dictionary)
    return res

def get_posts(state):
    cursor = state['remote_conn'].cursor()
    sql = """
        SELECT
            ID              AS id,
            post_content    AS source, 
            post_title      AS title, 
            post_title      AS name, 
            post_name       AS path, 
            post_date       AS posted, 
            post_status     AS status, 
            -- comment_status, 
            -- post_password, 
            post_modified   AS updated
            -- comment_count, 
        FROM wp_posts
        WHERE post_type='post' and post_status != 'draft'
        ORDER BY COALESCE(post_date, post_modified)
    """
    #sql += ' LIMIT 50'
    cursor.execute(sql)
    rows = dict_fetchall(cursor)
    cursor.close()
    return rows

def get_tags(state):
    cursor = state['remote_conn'].cursor()
    sql = """
        SELECT
            cat_ID         AS id,
            cat_name       AS name,
            category_nicename AS path
        FROM wp_categories
    """
    cursor.execute(sql)
    rows = dict_fetchall(cursor)
    cursor.close()
    return rows

def get_comments_for_post(state, post_id):
    cursor = state['remote_conn'].cursor()
    sql = """
        SELECT
            comment_author       AS author,
            comment_author_email AS email,
            comment_author_url   AS url,
            comment_author_IP    AS ip,
            comment_date         AS created,
            -- comment_date_gmt    ,
            comment_content      AS content
            -- comment_karma       ,
            -- comment_approved    ,
            -- comment_agent       ,
            -- comment_type        ,
            -- comment_parent      ,
            -- user_id             
        FROM wp_comments
        WHERE comment_post_ID=%s and comment_approved!='spam'
        ORDER BY comment_date
    """
    #sql += ' LIMIT 50'
    cursor.execute(sql, post_id)
    rows = dict_fetchall(cursor)
    cursor.close()
    return rows

def get_tags_for_post(state, post_id):
    cursor = state['remote_conn'].cursor()
    sql = """
        SELECT
            post_id, 
            category_id       AS id, 
            cat_name          AS name, 
            category_nicename AS path
        FROM wp_post2cat
        LEFT JOIN wp_categories ON wp_post2cat.category_id = wp_categories.cat_ID
        WHERE post_id=%s
    """
    cursor.execute(sql, post_id)
    rows = dict_fetchall(cursor)
    cursor.close()
    return rows

def export(connect):
    state = dict()
    log.debug('Connecting to database...')
    try:
        remote_conn = MySQLdb.connect(**connect)
    except MySQLdb.OperationalError, e:
        raise TemplateError(str(e))
    log.info('Fetching tags and posts...')
    state = {'remote_conn':remote_conn}
    
    tags = get_tags(state)
    for tag in tags:
        log.debug("Tag: %s"%(tag['name'],))

    posts = []
    for row in get_posts(state):
        if not row:
            raise Exception(row)
        post = row.copy()
        if not post['path']:
            raise Exception('Post %r has no path'%row)
        post['source'] = post['source'].lstrip('.. -*- mode: rst -*-').strip()
        if not post['posted']:
            post['posted'] = post['updated']
        log.debug("Post: %s" % post['title'])
        post['tags'] = get_tags_for_post(state, post['id'])
        for tag in post['tags']:
            log.debug("Post tag: %s" % tag['path'])
        post['comments'] = get_comments_for_post(state, post['id'])
        for comment in post['comments']:
            log.debug("Comment: %s" % comment['created'])
        posts.append(post)
    remote_conn.close()
    log.info("Success. Returning data.")
    return posts, tags

def save_posts(site_root, dest, posts):
    if not os.path.exists(os.path.join(site_root, 'Templates')):
        raise TemplateError(
            "Path %r does not appear to be a vaild site root, it has no "
            "'Templates' directory"%site_root
        )
    if not dest.startswith(site_root):
        raise TemplateError(
            "Directory %r is not under site root %r"%(dest, site_root)
        )
    if not os.path.exists(dest):
        os.mkdir(dest)
    dirs = []
    for post in posts:
        year = str(post['posted'].year)
        if not year in dirs:
            if not os.path.exists(os.path.join(dest, year)):
                os.mkdir(os.path.join(dest, year))
            dirs.append(year)
        rst = build_rst_post(post)
        log.debug(
            "Processing %r",
            os.path.join(dest, year, post['path']+'.rst')
        )
        try:
            data = rst.encode('utf-8')
        except UnicodeDecodeError, e:
            log.warning('Could not convert %s.rst: %s', post['path'], e)
            data = rst
        fp = open(os.path.join(dest, year, post['path']+'.rst'), 'w')
        fp.write(data)
        fp.close()
    print 
    print "Now download the images and update the site."
    print "See the documentation for details."


