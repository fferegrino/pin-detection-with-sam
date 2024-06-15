$(function() {
    $("#pinsImage").mapster({
        enableAutoResizeSupport: true,
        autoResize: true,
        fillColor: '000000',
        isSelectable: false,
        stroke: true,
        strokeColor: '00FF00',
        strokeWidth: 3,
        mapKey: 'data-key',
        fillOpacity: 0.5,
        onClick: function(data) {
            const clonedImage = document.getElementById(`cutout-${data.key}`).cloneNode(true);
            clonedImage.id = `cutout-${data.key}-cloned`;
            clonedImage.style.zIndex = 1000;

            const modal = document.getElementById('modal');
            modal.innerHTML = '';
            modal.appendChild(clonedImage);
            $(modal).modal();
        },
        // showToolTip: true,
        // toolTip: function(data) {
        //     // use the data attribute name as the default tooltip for all areas
        //     // returning a string (plain text) value
        //     // return $(data.target).data('name');
        //     return $(data.target).data('name')
        // },
    }).mapster('set', true, 'all');
});