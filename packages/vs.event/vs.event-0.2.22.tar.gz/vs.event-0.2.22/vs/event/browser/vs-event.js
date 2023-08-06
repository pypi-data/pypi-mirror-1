var $j = jQuery.noConflict();

function wholeDayHandler(e) {
    if (e.target.checked) 
        $j('.vs-calendarwidget-time').fadeOut();
    else 
        $j('.vs-calendarwidget-time').fadeIn();
}

function useEndDateHandler(e) {
    if (e.target.checked) 
        $j('#archetypes-fieldname-endDate').fadeIn();
    else 
        $j('#archetypes-fieldname-endDate').fadeOut();
}

$j(document).ready(function() {
    $j('#wholeDay').bind('change', wholeDayHandler);
    $j('#useEndDate').bind('change', useEndDateHandler);

    if (! $j('#useEndDate').attr('checked')) {
        $j('#archetypes-fieldname-endDate').fadeOut();
    }

    // PLONE_LANGUAGE will be defined in vs_calendarwidget.pt
    try {
        language = PLONE_LANGUAGE;
    } catch(e) {language ='en';};
    
    if (language == 'de') {
        jQuery(function($){
                
                $.datepicker.regional['de'] = {clearText: 'l&ouml;schen', clearStatus: 'aktuelles Datum l&ouml;schen',
                        closeText: 'schlie&szlig;en', closeStatus: 'ohne &Auml;nderungen schlie&szlig;en',
                        prevText: '< zur&uuml;ck', prevStatus: 'letzten Monat zeigen',
                        nextText: 'Vor >', nextStatus: 'n&auml;chsten Monat zeigen',
                        currentText: 'heute', currentStatus: '',
                        monthNames: ['Januar','Februar','M&auml;rz','April','Mai','Juni',
                        'Juli','August','September','Oktober','November','Dezember'],
                        monthNamesShort: ['Jan','Feb','M&auml;r','Apr','Mai','Jun',
                        'Jul','Aug','Sep','Okt','Nov','Dez'],
                        monthStatus: 'anderen Monat anzeigen', yearStatus: 'anderes Jahr anzeigen',
                        weekHeader: 'Wo', weekStatus: 'Woche des Monats',
                        dayNames: ['Sonntag','Montag','Dienstag','Mittwoch','Donnerstag','Freitag','Samstag'],
                        dayNamesShort: ['So','Mo','Di','Mi','Do','Fr','Sa'],
                        dayNamesMin: ['So','Mo','Di','Mi','Do','Fr','Sa'],
                        dayStatus: 'Setze DD als ersten Wochentag', dateStatus: 'W&auml;hle D, M d',
                        dateFormat: 'dd.mm.yy', firstDay: 1, 
                        initStatus: 'W&auml;hle ein Datum', isRTL: false};
                $.datepicker.setDefaults($.datepicker.regional['de']);
        });
    }

    var jquery_date_format = 'yy-mm-dd';
    var python_date_format = '%Y-%m-%d';

    try {
        jquery_date_format = JQUERY_DATE_FORMAT;
        python_date_format = PYTHON_DATE_FORMAT;
                
    } catch(e) {}

    $j('.calendarInput').datepicker({dateFormat : jquery_date_format,
                                     numberOfMonths : 1,
                                     showButtonPanel : true,
                                     });

    $j('.calendarInput').each(function(f) {
            this.readonly = '1';
    });

    $j('.calendarInputDateFormat').each(function(f) {
            this.value = python_date_format;
    });

})
