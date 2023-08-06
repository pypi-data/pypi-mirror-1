function googleapps_menu(link_id, menu_id) {
	if (jq(link_id).length > 0) {
                jq(link_id).click(function() {
                        jq(menu_id).toggle();
                        return false;
                        });

                var contentMenu = jq(menu_id);
                var position = jq(link_id).position();

                contentMenu.hide();
                contentMenu.css({ top: position.top-contentMenu.outerHeight(), left: (position.left+jq(link_id).outerWidth())-contentMenu.outerWidth() });
        }
}

jq(document).ready(function() {
	googleapps_menu('#gd-new-content-link', '#gd-new-content-menu');
        googleapps_menu('#gm-new-mail-link', '#gm-new-mail-menu');
	googleapps_menu('#gc-add-event-link', '#gc-add-event-menu');
});
