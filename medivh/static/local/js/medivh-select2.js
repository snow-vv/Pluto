var select2_remote_options = {
    minimumInputLength: 0,
    ajax: {
        url: $(this).attr("data-ajax--url"),
        dataType: "json",
        data: function (params) {
            return {
                q: params.term,
                page: params.page
            };
        },
        processResults: function (data, params) {
            var num = data.num;
            params.page = params.page || 1;
            var more = data.results.length == num;
            //var more = (data.page * num) < data.total_count;
            data.pagination = {more: more};
            return data;
        },
        cache: true
    },
}
var select2_remote_multiple_options = {
    multiple: true,
    closeOnSelect: false,
};
$.extend(true, select2_remote_multiple_options, select2_remote_options);

function select2_init() {
    $(".select2-remote").select2(select2_remote_options);
    $(".select2-remote-multiple").select2(select2_remote_multiple_options);
}


function gm_select2() {
    var url = $(this).attr("data-ajax--url");
    var init_value = $(this).attr("init-value");
    var cur = $(this);
    if (init_value && url) {
        $.ajax({
            type: "get",
            url: url,
            data: {'initial': init_value},
            async: false,
            success: function (data) {
                for (i in data['results']) {
                    var val = data['results'][i]['id'];
                    var text = data['results'][i]['text'];
                    cur.append("<option value='" + val + "' selected='selected'>" + text + "</option>");
                }
            }
        });
    }
}


function gm_select2_init() {
    $(".select2-remote").each(gm_select2);
    $(".select2-remote").select2(select2_remote_options);
    $(".select2-remote-multiple").each(gm_select2);
    $(".select2-remote-multiple").select2(select2_remote_multiple_options);
}

function select2_disable() {
    $(".select2-remote").prop("disabled", true);
    $(".select2-remote-multiple").prop("disabled", true);
}