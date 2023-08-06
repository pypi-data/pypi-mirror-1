jq(document).ready(function(){
    var base_url = jq("#volunteer_url")[0].value;
    
    function volunteer(ele){
      jq.ajax({
      url: base_url + "/volunteerday_ajax",
      data: {
        method: 'volunteer',
        id: ele.attr('id')
      },
      complete: function(res, status){
        var values = eval(res.responseText)[0];
        var ele = jq("#" + values.ele_id);
        ele.html("remove");
        ele.removeClass("volunteer");
        ele.addClass("remove_volunteer");
        ele.parent().find('dt').html(values.user_id);
      }
    });
    }
    
    function remove_volunteer(ele){
      jq.ajax({
      url: base_url + "/volunteerday_ajax",
      data: {
        method: 'remove_volunteer',
        id: ele.attr('id')
      },
      complete: function(res, status){
        var values = eval(res.responseText)[0];
        var ele = jq("#" + values.ele_id);
        ele.html("Volunteer for this time");
        ele.removeClass("remove_volunteer");
        ele.addClass("volunteer");
        ele.parent().find('dt').html("");
      }
    });
    }
    
    jq('.volunteer-slot').click(function(){
      if(jq(this).hasClass('volunteer')){
        volunteer(jq(this));
      }else{
        remove_volunteer(jq(this));
      }
    });
});