$('#submit_button').click(function () {
    var name = $('#username').val();
    var age = $('#age').val();
    var passwd = $('#passwd').val();
    var job = $('#Job').val();
    var role_name = $('#user_role').val();

    var type = 'POST';
    var url = '/user/add/';
    var data = {name: name, age: age, passwd: passwd, job: job, role_name: role_name};

    $.ajax({
        type: type,
        url: url,
        data: data,
        dataType: 'json',
        success: function (data) {
            if(data['is_ok']){
                alert('添加成功！');
                window.location.href = '/user/list';
            } else {
                // 此处的 error 是后端返回值的 key
                alert(data['error']);
                window.location.href = '/user/add';
            }
        }
    })
});