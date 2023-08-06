var $j = jQuery.noConflict();

function wholeDayHandler(e) {
    if (e.target.checked) 
        $j('.vs-calendarwidget-time').hide();
    else 
        $j('.vs-calendarwidget-time').show();
}

function useEndDateHandler(e) {
    if (e.target.checked) 
        $j('#archetypes-fieldname-endDate').show();
    else 
        $j('#archetypes-fieldname-endDate').hide();
}


$j(document).ready(function() {
    $j('#wholeDay').bind('change', wholeDayHandler);
    $j('#useEndDate').bind('change', useEndDateHandler);

    if (! $j('#useEndDate').attr('checked')) {
        $j('#archetypes-fieldname-endDate').hide();
    }

 $j.datepicker.setDefaults($j.datepicker.regional['de']);

    $j('.calendarInput').datepicker({dateFormat : 'dd.mm.yy',
                                     numberOfMonths : 1,
                                     showButtonPanel : true,
                                     });
})
