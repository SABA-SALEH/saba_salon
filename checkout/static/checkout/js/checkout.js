// JavaScript to synchronize the save_info checkbox value
const saveInfoCheckbox = document.querySelector('#id-save-info');
const saveInfoInput = document.querySelector('#id_save_info');

if (saveInfoCheckbox && saveInfoInput) {
    saveInfoCheckbox.addEventListener('change', function () {
        saveInfoInput.value = this.checked ? 'true' : 'false';
    });
}
