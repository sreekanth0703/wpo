$(document).ready(function() {

  $("#employee-upload").submit(function( event ) {
    event.preventDefault();
    formData = new FormData()
    files = $("#employee-upload").find('[name="files"]')[0].files;
    $.each(files, function(i, file) {
        formData.append('files-' + i, file);
    });

    $.ajax({url: '/employee_upload/',
            data: formData,
            method: 'POST',
            processData : false,
            contentType : false,
            'success': function(response) {
              $.notify(response);
              if(response == 'Success') {
                $("#employee-upload").trigger('reset');
              }
            }});
    event.preventDefault();
  });


})
