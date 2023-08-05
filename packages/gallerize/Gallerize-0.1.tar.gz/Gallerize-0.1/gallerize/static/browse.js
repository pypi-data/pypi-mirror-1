// Fade in all thumbnails, one by one.
function show_item() {
    $(this).next('li').show('fast', show_item);
}
$(function() {
    $('ol.thumbnails li').hide().eq(0).show('fast', show_item);
});

// Fade in a big image.
$(function() {
    $('img').hide().show('slow');
});
