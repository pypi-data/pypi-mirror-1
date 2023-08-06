/* styleselect.js */


connect(window, 'onload', function () {
        if ($('styleselect')) {
                connect('styleselect_st', 'onchange', styleselect_submit);
                addElementClass('styleselect_submit_container', 'invisible');
        }
    }
);

function styleselect_submit() {
    $('styleselect').submit();
}
