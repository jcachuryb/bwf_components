/* eslint-disable no-alert */
import '@popperjs/core/dist/umd/popper.min.js';
import '../scss/app.scss';
import 'jquery-ui/dist/jquery-ui.js';
import 'jquery-toast-plugin/dist/jquery.toast.min.js';
import 'jquery-mask-plugin/dist/jquery.mask.js';
/* Your JS Code goes here */
import './form-builder.js';

/* Demo JS */
import './demo.js';

const storedForm = window.localStorage.getItem('storedForm');

$('#app').formBuilder({
  formData: storedForm ? JSON.parse(storedForm) : [],
  API_KEY: 'AXAKSDHASKJDHAKSJHDLAKSHDASDFHASDHFJKL',
  initialValue: {
    emailField: 'robe@extremoduro.com',
    people: [
      {
        selectBoxes: ['john.doe@test.com'],
        checkboxControl: true,
      },
    ],
    datePicker: [new Date('2024-10-30T16:00:00.000Z'), new Date('2024-10-21T16:00:00.000Z')],
    table: [
      {
        textField1: 'sadf',
        inputNumber: 123,
        selectBoxes1: ['john.doe@test.com', 'jane.doe@test.com'],
        datePicker1: new Date('2024-11-11T16:00:00.000Z'),
      },
    ],
  },
});
$('#app').formBuilder('render');

// $('#app').formBuilder('render', {
//   formData: storedForm ? JSON.parse(storedForm) : [],
//   //   onSubmit
//   submitData: {
//     url: 'http://127.0.0.1:3000/form-submission',
//     method: 'POST',
//     headers: {
//       'X-Api-Key': '12345',
//     },
//     data: {},
//   },
// });
