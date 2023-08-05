/**
 * ViewTopic
 * ---------
 *
 * @copyright 2006 by Armin Ronacher.
 * @license GNU GPL, see LICENSE for more details.
 */

/**
 * automatically jumps to the active post if the active post
 * isn't the root_post_id.
 *
 * @param format        a string which represents the format of a
 *                      post id with '%d' as placeholder for the
 *                      real post it. eg: 'p%d'.
 * @param root_post_id  the id of the first post on the page.
                        eg: 42
 */
function jumpToActivePost(format, root_post_id) {
    var href = document.location.href + '';
    var post_id = parseInt(href.match(/\/post\/(\d+)/)[1]);
    if (post_id != root_post_id) {
        document.location.href = '#' + (format.replace(/\%d/, post_id));
    }
}
