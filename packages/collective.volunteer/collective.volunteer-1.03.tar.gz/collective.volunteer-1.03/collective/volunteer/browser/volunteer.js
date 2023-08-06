jq(document).ready(function(){
    var base_url = jq("#volunteer_url")[0].value;
    
    function volunteer(ele){
    
        jQuery.post(
            base_url + "/volunteer",
            {id: ele.attr('id')},
            function(res, status){
                  var values = eval(res)[0];
                  var ele = jq("#" + values.ele_id);
                  ele.html("remove me!");
                  ele.removeClass("volunteer");
                  ele.addClass("removeVolunteer");
                  jq("#timeUser-" + values.index).html(values.user_id);
              }
        );
    }
    
    function remove_volunteer(ele){
        jQuery.post(
            base_url + "/remove_volunteer",
            {id: ele.attr('id')},
            function(res, status){
                var values = eval(res)[0];
                var ele = jq("#" + values.ele_id);
                ele.html("Volunteer for this time");
                ele.removeClass("removeVolunteer");
                ele.addClass("volunteer");
                jq("#timeUser-" + values.index).html("");
              }
        );
    }
    
    jq('.volunteer-slot').click(function(){
        if(jq(this).hasClass('volunteer')){
            volunteer(jq(this));
        }else{
            remove_volunteer(jq(this));
        }
    });
});