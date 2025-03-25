// ================= WOOCOMERCE =======================
function allow_yoast_meta_rest_update() {
    register_meta('post', '_yoast_wpseo_metadesc', array(
        'type'         => 'string',
        'description'  => 'Yoast SEO Meta Description',
        'single'       => true,
        'show_in_rest' => true,
    ));
    register_meta('post', '_yoast_wpseo_title', array(
        'type'         => 'string',
        'description'  => 'Yoast SEO Title',
        'single'       => true,
        'show_in_rest' => true,
    ));
}
add_action('init', 'allow_yoast_meta_rest_update');