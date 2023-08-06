function DPA(s1, s2){
    var m = new Array();
    var i, j;
    for(i=0; i < s1.length + 1; i++) m[i] = new Array(); // i.e. 2-D array

    m[0][0] = 0; // boundary conditions

    for(j=1; j <= s2.length; j++)
        m[0][j] = m[0][j-1]-0 + 1; // boundary conditions

    for(i=1; i <= s1.length; i++)                            // outer loop
    {
        m[i][0] = m[i-1][0]-0 + 1; // boundary conditions

        for(j=1; j <= s2.length; j++)                         // inner loop
        {
            var diag = m[i-1][j-1];
            if( s1.charAt(i-1) != s2.charAt(j-1) ) diag++;

            m[i][j] = Math.min( diag,               // match or change
            Math.min( m[i-1][j]-0 + 1,    // deletion
            m[i][j-1]-0 + 1 ) ) // insertion
        }//for j
    }//for i
   return m[s1.length][s2.length];
}

EMAIL_LIST = ['163.com','126.com', '139.com', '188.com', '2008.china.com', '2008.sina.com', '21cn.com', '263.net', 'china.com', 'chinaren.com', 'citiz.net', 'eyou.com', 'foxmail.com', 'gmail.com', 'hongkong.com', 'hotmail.com', 'live.cn', 'live.com', 'mail.china.com', 'msn.com', 'my3ia.sina.com', 'qq.com', 'sina.cn', 'sina.com', 'sina.com.cn', 'sogou.com', 'sohu.com', 'tom.com', 'vip.163.com', 'vip.qq.com', 'vip.sina.com', 'vip.sohu.com', 'vip.tom.com', 'yahoo.cn', 'yahoo.com', 'yahoo.com.cn', 'yahoo.com.hk', 'yahoo.com.tw', 'yeah.net'];
function email_like(s){
    var v = s.split('@'), domain = v[1]||"", dis = domain.length , e_domain;
    for (k=0; k < EMAIL_LIST.length; k++){
        var e = EMAIL_LIST[k],d = DPA(domain, e);
        if (d < dis){
            dis = d;
            e_domain = e;
        }
    }
    if(dis && dis < 4){
        return e_domain;
    }
};

function fixemail_set(){
    var e=$("#email"),v=e.val(),fixemail=$("#fixemail"),c=email_like(v);
    if(c)e.val(v.split('@')[0]+"@"+c);
    fixemail.fadeOut();
}
function fixemail_hide(t){
    $(t.parentNode).fadeOut()
    $("#name").focus()
}

function check_email(tip){
	var fixemail=$("#err_email"),self=$("#email");
    var v=$.trim(self.val());
    self.val(v);
    if(tip){ 
        var com = email_like(v),name =v.split('@')[0];
        if(com){
            fixemail.html('<b class="fixmail_name" style="font-weight:normal;color:#666"></b><b class="fixmail_domain"></b>　<a onclick="fixemail_set();fixemail_hide(this)" href="javascript:void(0)">是</a> <b style="font-weight:normal;color:#666">/</b> <a onclick="fixemail_hide(this)" href="javascript:void(0)">否</a>')
            fixemail.find('.fixmail_name').text('你是否要输入 '+name+'@')
            fixemail.find('.fixmail_domain').text(com)
            fixemail.fadeIn().find('a:first').focus()
            return
        }    
    }
    if(!/^[_\.0-9a-zA-Z+-]+@([0-9a-zA-Z]+[0-9a-zA-Z-]*\.)+[a-zA-Z]{2,4}$/.exec(v)){
        fixemail.text("请输入正确的Email地址").fadeIn()
        return 
    }
    return 1; 
}
function check_name(){
    var err=$("#err_name"),self=$("#name"),val=self.val().length,tip;
    if(val){
        if(val>16)tip="名号不要超过8个汉字或16个英文字符";
    }
    else{tip="请输入名号"}
    if(tip){
        err.text(tip).fadeIn()
    }else return 1;
    
}
function check_password(){
    var err=$("#err_password"),self=$("#password"),val=self.val().length,tip;
    if(val){
        if(val<6)tip="密码不得少于6个字符";
        if(val>60)tip="密码不得多于60个字符";
    }
    else{tip="请输入密码"}
    if(tip){
        err.text(tip).fadeIn()
    }else return 1;
    
}
function submit_form(){
    var result=1;
    result &= check_password();
    result &= check_name();
    result &= check_email();
    if(result){
        return true;
    }
    return false;
}
$(function(){
    $("#email").blur(check_email).change(function(){$("#err_email").hide()})
    $("#name").blur(check_name).change(function(){$("#err_name").hide()})
    $("#password").blur(check_password).change(function(){$("#err_password").hide()})
    $(".Pform input:first").focus()
})

