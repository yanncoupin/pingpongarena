$(document).ready(function(){
    $('input[name="team_a"]').click(function(event){
        me = event.target
        if ($('input:checked[name="team_a"]').length == 3 || $(me.nextSibling).hasClass("disabled"))
        {
            event.preventDefault();
            return;
        }
        alter_ego_label = $('input[name="team_b"][value="'+me.value+'"] + label');
        alter_ego = $('input[name="team_b"][value="'+me.value+'"]');
        if (me.checked)
        {
            alter_ego_label.addClass('disabled');
        }
        else
        {
            alter_ego_label.removeClass('disabled');
        }
    });
    $('input[name="team_a"] + label').click(function(event){event.target.previousSibling.click();event.preventDefault()});
    $('input[name="team_b"]').click(function(event){
        me = event.target
        if ($('input:checked[name="team_b"]').length == 3 || $(me.nextSibling).hasClass("disabled"))
        {
            event.preventDefault();
            return;
        }
        alter_ego_label = $('input[name="team_a"][value="'+me.value+'"] + label');
        alter_ego = $('input[name="team_a"][value="'+me.value+'"]');
        if (me.checked)
        {
            alter_ego_label.addClass('disabled');
        }
        else
        {
            alter_ego_label.removeClass('disabled');
        }
    });
    $('input[name="team_b"] + label').click(function(event){event.target.previousSibling.click();event.preventDefault()});
    $('input[name="base"] + label').click(function(event){event.target.previousSibling.click();event.preventDefault()});
    $('form').submit(function(){
        a = $('input:checked[name="team_a"]').length;
        b = $('input:checked[name="team_b"]').length;
        base = parseInt($('input:checked[name="base"]')[0].value);
        score_a = parseInt($('input[name="score_a"]')[0].value);
        if (isNaN(score_a)) {score_a = 0;}
        score_b = parseInt($('input[name="score_b"]')[0].value);
        if (isNaN(score_b)) {score_b = 0;}

        if (a != 1 && a != 2 || b != 1 && b != 2 || a != b)
        {
            $("#warnings").text("Simple ou double uniquement !").show().fadeOut(3000);
            return false;
        }
        if (score_a <= base && score_b <= base && score_a != base && score_b != base)
        {
            $("#warnings").text("Score sans gagnant !").show().fadeOut(3000);
            return false;
        }
        if (score_a <= base && score_b <= base && abs(score_a - score_b)  == 1)
        {
            $("#warnings").text("Score invalide !").show().fadeOut(3000);
            return false;
        }
        if ((score_a > base || score_b > base) && (score_a - score_b) != -2 && (score_a - score_b) != 2 )
        {
            $("#warnings").text("Score invalide !").show().fadeOut(3000);
            return false;
        }
    });
});
