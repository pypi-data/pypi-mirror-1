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


    // DatePicker stuff

    var UIDateFormat = 'yy/mm/dd';
    var BackendDateFormat = '%Y/%m/%d';
    // PLONE_LANGUAGE will be defined in vs_calendarwidget.pt
    try {
        language = PLONE_LANGUAGE;
    } catch(e) {language ='en';};
    
    if (language == 'de') {
        jQuery(function($){
                UIDateFormat = 'dd.mm.yy';
                BackendDateFormat = '%d.%m.%Y';
                
                $.datepicker.regional['de'] = {clearText: 'löschen', clearStatus: 'aktuelles Datum löschen',
                        closeText: 'schließen', closeStatus: 'ohne Änderungen schließen',
                        prevText: '&#x3c;zurück', prevStatus: 'letzten Monat zeigen',
                        nextText: 'Vor&#x3e;', nextStatus: 'nächsten Monat zeigen',
                        currentText: 'heute', currentStatus: '',
                        monthNames: ['Januar','Februar','M&auml;rz','April','Mai','Juni',
                        'Juli','August','September','Oktober','November','Dezember'],
                        monthNamesShort: ['Jan','Feb','Mär','Apr','Mai','Jun',
                        'Jul','Aug','Sep','Okt','Nov','Dez'],
                        monthStatus: 'anderen Monat anzeigen', yearStatus: 'anderes Jahr anzeigen',
                        weekHeader: 'Wo', weekStatus: 'Woche des Monats',
                        dayNames: ['Sonntag','Montag','Dienstag','Mittwoch','Donnerstag','Freitag','Samstag'],
                        dayNamesShort: ['So','Mo','Di','Mi','Do','Fr','Sa'],
                        dayNamesMin: ['So','Mo','Di','Mi','Do','Fr','Sa'],
                        dayStatus: 'Setze DD als ersten Wochentag', dateStatus: 'Wähle D, M d',
                        dateFormat: 'dd.mm.yy', firstDay: 1, 
                        initStatus: 'Wähle ein Datum', isRTL: false};
                $.datepicker.setDefaults($.datepicker.regional['de']);
        });
    }

    $j('.calendarInput').datepicker({dateFormat : UIDateFormat,
                                     numberOfMonths : 1,
                                     showButtonPanel : true,
                                     });

    $j('.calendarInputDateFormat').each(function(f) {
            this.value = BackendDateFormat;
    });

})
