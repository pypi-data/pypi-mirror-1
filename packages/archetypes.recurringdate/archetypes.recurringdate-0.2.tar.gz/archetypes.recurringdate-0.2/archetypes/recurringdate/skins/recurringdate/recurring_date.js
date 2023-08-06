jq(function() {
    function formatDuration(value) {
      value /= 1000;
      var seconds = Math.floor(value % 60);
      value /= 60;
      var minutes = Math.abs(Math.floor(value % 60));
      var hours = Math.floor(value / 60);
      return hours + ':' + (minutes < 10 ? '0' : '') + minutes;
    }

    function timeComponents(value) {
      var hour = value.getHours();
      var minute = value.getMinutes();
      var ampm = "AM";
      if (hour > 11) ampm = "PM";
      if (hour > 12) hour = hour - 12;
      if (hour < 10) hour = "0" + hour;
      if (minute < 10) minute = "0" + minute;
      return new Array(hour, minute, ampm);
    }

    // Functions to keep date/time synchronized
    function updateEventStartTime() {
      var tc = timeComponents(jq.timePicker("#recurrence_time_start").getTime());
      jq("#edit_form_startDate_0_hour option[value='"+tc[0]+"']").attr('selected', 'selected');
      jq("#edit_form_startDate_0_minute option[value='"+tc[1]+"']").attr('selected', 'selected');
      jq("#edit_form_startDate_0_ampm option[value='"+tc[2]+"']").attr('selected', 'selected');
    }
    function updateEventEndTime() {
      var tc = timeComponents(jq.timePicker("#recurrence_time_end").getTime());
      jq("#edit_form_endDate_1_hour option[value='"+tc[0]+"']").attr('selected', 'selected');
      jq("#edit_form_endDate_1_minute option[value='"+tc[1]+"']").attr('selected', 'selected');
      jq("#edit_form_endDate_1_ampm option[value='"+tc[2]+"']").attr('selected', 'selected');
    }
    function updateEventStartEndTime() {
      var dc = jq("#recurrence_range_start").val().split("/");
      jq("#edit_form_startDate_0_year option[value='"+dc[0]+"']").attr('selected', 'selected');
      jq("#edit_form_startDate_0_month option[value='"+dc[1]+"']").attr('selected', 'selected');
      jq("#edit_form_startDate_0_day option[value='"+dc[2]+"']").attr('selected', 'selected');
      jq("#edit_form_endDate_1_year option[value='"+dc[0]+"']").attr('selected', 'selected');
      jq("#edit_form_endDate_1_month option[value='"+dc[1]+"']").attr('selected', 'selected');
      jq("#edit_form_endDate_1_day option[value='"+dc[2]+"']").attr('selected', 'selected');
    }
    function updateRecurrenceStartEndTime() {
      var start = plone.jscalendar._fields("#edit_form_startDate_0");
      var end = plone.jscalendar._fields("#edit_form_endDate_1");
      jq("#recurrence_time_start").val(start.hour.val()+":"+start.minute.val()+" "+start.ampm.val());
      jq("#recurrence_time_end").val(end.hour.val()+":"+end.minute.val()+" "+end.ampm.val());
      jq("#recurrence_time_end").change();
    }
    function updateRecurrenceStartDate() {
      var start = plone.jscalendar._fields("#edit_form_startDate_0");
      jq("#recurrence_range_start").val(start.year.val()+"/"+start.month.val()+"/"+start.day.val());
    }
    function updateRecurrenceEndDate() {
      var end = plone.jscalendar._fields("#edit_form_endDate_1");
      jq("#recurrence_range_end").val(end.year.val()+"/"+end.month.val()+"/"+end.day.val());
    }

    // Automatic parser for date formats
    jq("#recurrence_range_start").change(function() {
        var value = Date.parse(jq(this).val());
        if(value) jq(this).val(value.toString('yyyy/MM/dd'));
        updateEventStartEndTime();
    });
    jq("#recurrence_range_end").change(function() {
        var value = Date.parse(jq(this).val());
        if(value) jq(this).val(value.toString('yyyy/MM/dd'));
    });

    // Enable the timepicker
    jq("#recurrence_time_start, #recurrence_time_end").timePicker();

    // Enable the datepicker
    jq("#recurrence_range_start").DatePicker({
        format:'Y/m/d',
        starts: 0,
        date: jq(this).val(),
        onBeforeShow: function(){
            var value = Date.parse(jq(this).val());
            if(value) jq(this).DatePickerSetDate(value, true);
        },
        onChange: function(formated, dates){
            jq("#recurrence_range_start").val(formated);
            jq("#recurrence_range_start").DatePickerHide();
            updateEventStartEndTime();
        }
    });
    jq("#recurrence_range_end").DatePicker({
        format:'Y/m/d',
        starts: 0,
        date: jq(this).val(),
        onBeforeShow: function(){
            var value = Date.parse(jq(this).val());
            if(value) jq(this).DatePickerSetDate(value, true);
        },
        onChange: function(formated, dates){
            jq("#recurrence_range_end").val(formated);
            jq("#recurrence_range_end").DatePickerHide();
        }
    });

    // Update time end and duration after change time start
    var oldTime = jq.timePicker("#recurrence_time_start").getTime();
    jq("#recurrence_time_start").change(function() {
      var time = jq.timePicker("#recurrence_time_start").getTime();
      updateEventStartTime();
      if (jq("#recurrence_time_end").val()) {
        // Calculate duration.
        var duration = (jq.timePicker("#recurrence_time_end").getTime() - oldTime);

        // Calculate and update the time in the second input.
        jq.timePicker("#recurrence_time_end").setTime(new Date(new Date(time.getTime() + duration)));
        updateEventEndTime();

        // Update the duration input
        var duration = jq.timePicker("#recurrence_time_end").getTime() - jq.timePicker("#recurrence_time_start").getTime();
        jq("#recurrence_duration").val(formatDuration(duration));
      }
      oldTime = time;
    });

    // Update duration after change time end
    jq("#recurrence_time_end").change(function() {
      if (jq("#recurrence_time_start").val()) {
        var duration = jq.timePicker("#recurrence_time_end").getTime() - jq.timePicker("#recurrence_time_start").getTime();
        jq("#recurrence_duration").val(formatDuration(duration));
        updateEventEndTime();
      }
    });

    // Update time end after change duration
    jq("#recurrence_duration").change(function() {
      if (jq("#recurrence_time_start").val()) {
        var time = jq.timePicker("#recurrence_time_start").getTime();
        var parsed = jq("#recurrence_duration").val().split(':');
        var duration = parsed[0] * 60 * 60 * 1000 + parsed[1] * 60 * 1000;
        jq.timePicker("#recurrence_time_end").setTime(new Date(new Date(time.getTime() + duration)));
        updateEventEndTime();
      }
    });

    // Update the date recurrence field when change the event date start fields
    jq("#edit_form_startDate_0_year, #edit_form_startDate_0_month, #edit_form_startDate_0_day").change(function() {
      updateRecurrenceStartDate();
    });

    // Update the start time recurrence field when change the event time start fields
    jq("#edit_form_startDate_0_hour, #edit_form_startDate_0_minute, #edit_form_startDate_0_ampm").change(function() {
      updateRecurrenceStartEndTime();
    });

    // Update the end time recurrence field when change the event time end fields
    jq("#edit_form_endDate_1_hour, #edit_form_endDate_1_minute, #edit_form_endDate_1_ampm").change(function() {
      updateRecurrenceStartEndTime();
    });

    // Toggle the recurrence box and copy event start/end date/time to the recurrence fields
    jq("#recurrence_enabled").click(function() {
      if(jq(this).attr("checked")) {
        updateRecurrenceStartEndTime();
        updateRecurrenceStartDate();
        updateRecurrenceEndDate();
        jq(".recurrence_box").show();
      } else {
        jq(".recurrence_box").hide();
      }
    });

    // Show/hide the related boxes when the frequency change
    jq(".frequency_options input.frequency_daily").click(function() {
      if(jq(this).attr("checked")) {
        jq(this).parents(".field").find(".daily_box").show();
        jq(this).parents(".field").find(".weekly_box").hide();
        jq(this).parents(".field").find(".monthly_box").hide();
        jq(this).parents(".field").find(".yearly_box").hide();
      }
    });
    jq(".frequency_options input.frequency_weekly").click(function() {
      if(jq(this).attr("checked")) {
        jq(this).parents(".field").find(".daily_box").hide();
        jq(this).parents(".field").find(".weekly_box").show();
        jq(this).parents(".field").find(".monthly_box").hide();
        jq(this).parents(".field").find(".yearly_box").hide();
      }
    });
    jq(".frequency_options input.frequency_monthly").click(function() {
      if(jq(this).attr("checked")) {
        jq(this).parents(".field").find(".daily_box").hide();
        jq(this).parents(".field").find(".weekly_box").hide();
        jq(this).parents(".field").find(".monthly_box").show();
        jq(this).parents(".field").find(".yearly_box").hide();
      }
    });
    jq(".frequency_options input.frequency_yearly").click(function() {
      if(jq(this).attr("checked")) {
        jq(this).parents(".field").find(".daily_box").hide();
        jq(this).parents(".field").find(".weekly_box").hide();
        jq(this).parents(".field").find(".monthly_box").hide();
        jq(this).parents(".field").find(".yearly_box").show();
      }
    });

    // Display the boxes if enabled
    jq("#recurrence_enabled:checked").parent().find(".recurrence_box").show();
    jq(".frequency_options input.frequency_daily:checked").parents(".field").find(".daily_box").show();
    jq(".frequency_options input.frequency_weekly:checked").parents(".field").find(".weekly_box").show();
    jq(".frequency_options input.frequency_monthly:checked").parents(".field").find(".monthly_box").show();
    jq(".frequency_options input.frequency_yearly:checked").parents(".field").find(".yearly_box").show();

});
