$(document).ready( function () {
    $('#table_id').DataTable({
        language: {
            'zeroRecords': '<a href="/newpaciente' + '">Agregar nuevo paciente</a>',
            "search": "Buscar:",
        }
    });
} );