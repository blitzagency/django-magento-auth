var $ = django.jQuery;
$(function(){
    var $chosen = $('.chosen');
    $chosen.closest('.grp-row').css({overflow:'visible'});

    $(".chosen").ajaxChosen({
            dataType: 'json',
            type: 'GET',
        },{
        processItems: function(data){
            // var option = '<option value="hi">hi</option>';
            // $chosen.append(option);
            // $chosen.trigger("chosen:updated");
            var output = [];
            for(var i =0; i < data.length; i ++){
                var obj = {};
                var item = data[i];
                obj.id = item.product_id;
                obj.text = item.name;
                output.push(obj);
            }
            return output;
        },
        generateUrl: function(q){
            return '/madjango/?search='+q;
        },
        loadingImg: '/static/img/loading.gif'
    });

});
