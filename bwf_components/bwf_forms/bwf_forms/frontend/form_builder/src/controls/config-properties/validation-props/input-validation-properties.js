import { CONTROL_VALIDATION_PROPS_TYPES } from '../../utils/control-props-types';
import { INPUT_TYPES } from '../../utils/input-types';
import { BaseValidationProps } from '../data-props/base-validation-props';

export class InputFieldValidationProps extends BaseValidationProps {
  constructor(type = INPUT_TYPES.TEXT, props) {
    super(getProps(type));
    this.fillInProps(props);
    if (
      [
        INPUT_TYPES.RADIO,
        INPUT_TYPES.CHECK_BOX,
        INPUT_TYPES.SELECT,
        INPUT_TYPES.DATE,
        INPUT_TYPES.SELECT_BOXES,
        INPUT_TYPES.FILE_UPLOAD,
      ].includes(type)
    ) {
      if (this.props.hasOwnProperty(CONTROL_VALIDATION_PROPS_TYPES.VALIDATE_ON)) {
        this.modifyPropValue(CONTROL_VALIDATION_PROPS_TYPES.VALIDATE_ON, 'change');
      }
    }
  }

  _onDataPropsChange(e) {
    const { context: _this, prop } = e.data;
    const value = e.target
      ? e.target.type === INPUT_TYPES.CHECK_BOX
        ? e.target.checked
        : e.target.type === 'number'
        ? Number.parseInt(e.target.value) || 0
        : e.target.value
      : e.value;

    _this.modifyPropValue(prop.name, value);
    _this.editor._renderPreviewControl();
  }

  render() {
    return super.render();
  }
}

function getProps(type) {
  switch (type) {
    case INPUT_TYPES.NUMBER:
      return numberProps;
    case INPUT_TYPES.RADIO:
      return radioProps;
    case INPUT_TYPES.CHECK_BOX:
      return checkboxProps;
    case INPUT_TYPES.SELECT:
      return selectProps;
    case INPUT_TYPES.DATE:
      return dateProps;
    case INPUT_TYPES.PASSWORD:
      return passwordProps;
    case INPUT_TYPES.EMAIL:
      return emailProps;
    case INPUT_TYPES.SELECT_BOXES:
      return selectBoxes;
    case INPUT_TYPES.FILE_UPLOAD:
      return FileUploadProps;
    default:
      return textProps;
  }
}

const textProps = [
  CONTROL_VALIDATION_PROPS_TYPES.VALIDATE_ON,
  CONTROL_VALIDATION_PROPS_TYPES.REQUIRED,
  // CONTROL_VALIDATION_PROPS_TYPES.VALIDATE_HIDDEN,
  CONTROL_VALIDATION_PROPS_TYPES.MIN_LENGTH,
  CONTROL_VALIDATION_PROPS_TYPES.MAX_LENGTH,
  CONTROL_VALIDATION_PROPS_TYPES.MIN_WORD_LENGTH,
  CONTROL_VALIDATION_PROPS_TYPES.MAX_WORD_LENGTH,
  CONTROL_VALIDATION_PROPS_TYPES.REGEX,
  CONTROL_VALIDATION_PROPS_TYPES.ERROR_MESSAGE,
];

const numberProps = [
  CONTROL_VALIDATION_PROPS_TYPES.VALIDATE_ON,
  CONTROL_VALIDATION_PROPS_TYPES.REQUIRED,
  CONTROL_VALIDATION_PROPS_TYPES.UNIQUE,
  CONTROL_VALIDATION_PROPS_TYPES.VALIDATE_HIDDEN,
  CONTROL_VALIDATION_PROPS_TYPES.MIN_VALUE,

  CONTROL_VALIDATION_PROPS_TYPES.MAX_VALUE,
  CONTROL_VALIDATION_PROPS_TYPES.ERROR_MESSAGE,
];

const dateProps = [
  CONTROL_VALIDATION_PROPS_TYPES.VALIDATE_ON,
  CONTROL_VALIDATION_PROPS_TYPES.REQUIRED,
  CONTROL_VALIDATION_PROPS_TYPES.UNIQUE,
  CONTROL_VALIDATION_PROPS_TYPES.VALIDATE_HIDDEN,
  CONTROL_VALIDATION_PROPS_TYPES.MIN_DATE,
  CONTROL_VALIDATION_PROPS_TYPES.MAX_DATE,
  CONTROL_VALIDATION_PROPS_TYPES.ERROR_MESSAGE,
];
const selectProps = [
  CONTROL_VALIDATION_PROPS_TYPES.VALIDATE_ON,
  CONTROL_VALIDATION_PROPS_TYPES.REQUIRED,
  CONTROL_VALIDATION_PROPS_TYPES.UNIQUE,

  CONTROL_VALIDATION_PROPS_TYPES.ERROR_MESSAGE,
];

const radioProps = [CONTROL_VALIDATION_PROPS_TYPES.REQUIRED, CONTROL_VALIDATION_PROPS_TYPES.ERROR_MESSAGE];
const checkboxProps = [CONTROL_VALIDATION_PROPS_TYPES.REQUIRED, CONTROL_VALIDATION_PROPS_TYPES.ERROR_MESSAGE];

const passwordProps = [
  CONTROL_VALIDATION_PROPS_TYPES.VALIDATE_ON,
  CONTROL_VALIDATION_PROPS_TYPES.REQUIRED,
  CONTROL_VALIDATION_PROPS_TYPES.MIN_LENGTH,
  CONTROL_VALIDATION_PROPS_TYPES.MAX_LENGTH,
  CONTROL_VALIDATION_PROPS_TYPES.REGEX,
  CONTROL_VALIDATION_PROPS_TYPES.ERROR_MESSAGE,
];
const emailProps = [
  CONTROL_VALIDATION_PROPS_TYPES.VALIDATE_ON,
  CONTROL_VALIDATION_PROPS_TYPES.REQUIRED,
  CONTROL_VALIDATION_PROPS_TYPES.MIN_LENGTH,
  CONTROL_VALIDATION_PROPS_TYPES.MAX_LENGTH,
  CONTROL_VALIDATION_PROPS_TYPES.REGEX,
  CONTROL_VALIDATION_PROPS_TYPES.ERROR_MESSAGE,
];

const selectBoxes = [
  CONTROL_VALIDATION_PROPS_TYPES.VALIDATE_ON,
  CONTROL_VALIDATION_PROPS_TYPES.REQUIRED,
  CONTROL_VALIDATION_PROPS_TYPES.MIN_CHECKED,
  CONTROL_VALIDATION_PROPS_TYPES.MAX_CHECKED,
  CONTROL_VALIDATION_PROPS_TYPES.MIN_CHECKED_ERROR_MESSAGE,
  CONTROL_VALIDATION_PROPS_TYPES.MAX_CHECKED_ERROR_MESSAGE,
];

const FileUploadProps = [CONTROL_VALIDATION_PROPS_TYPES.REQUIRED, CONTROL_VALIDATION_PROPS_TYPES.ERROR_MESSAGE];
