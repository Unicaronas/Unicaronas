var element = document.getElementById('cropper');
var cropper = new Croppie(element, croppieOptions);
var cropperCreatedEvent = new Event('cropper-created');

function readFile(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            if (e.target.result) {
                cropper.bind({
                    url: e.target.result
                });
                document.dispatchEvent(cropperCreatedEvent);
            }
        }
        reader.readAsDataURL(input.files[0]);
    }
}

var photoInput = document.getElementById('id_' + croppieFieldName + '_0');
photoInput.addEventListener('change', function() {
    $(element).show();
    $('#pre_cropper').hide();
    readFile(this);
});

element.addEventListener('update', function(cr) {
    var data = cropper.get();
    var baseSelector = 'id_' + croppieFieldName + '_';
    var pointInput = null;
    for (var i = 1; i <= 4; i++) {
        pointInput = document.getElementById(baseSelector + i)
        pointInput.value = data.points[i-1];
    }
});

if (croppieUrl) {
    $('#pre_cropper').show();
    $(element).hide();
} else {
    $(element).hide();
    cropper.bind({
        url: croppieUrl
    });
}
