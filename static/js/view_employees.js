$(document).ready(function() {
    $('#example').DataTable( {
        "processing": true,
        "serverSide": true,
        "lengthMenu": [200, 300, 400, 500],
        "pageLength": 200,
        "ajax": "/get_employee_data/"
    } );
} );
