/* eslint-disable prefer-spread */

import LayoutController from './layout';

import { FORM_CONTROLS } from '../controls/toolbox';
import ViewerLayoutController from './viewer-layout';

/* eslint-disable no-plusplus */
class FormBuilder {
  constructor(element, settings, $) {

    console.log('FormBuilder initialized', {
      element,
      settings,
    });
    var _ = this;

    _.defaults = {
      name: 'DBCA-FORMBUILDER',
      theme: 'default',
      formControls: FORM_CONTROLS,
    };

    _.initials = {
      present: true,
      formData: settings.formData || [],
    };
    $.extend(_, _.initials);

    _.$builder = $(element);

    _.body = [];

    _.$controlFactory = undefined;
    _.options = $.extend({}, _.defaults, settings);
    _.API_KEY = _.options.API_KEY || '';
    _.initialValue = _.options.initialValue || {};
    _.onSubmit = _.options.onSubmit || undefined;

    _.layout = new LayoutController(this, FORM_CONTROLS);

    _.originalSettings = _.options;
  }

  build() {
    const _ = this;
    _.layout.renderFormBuilder();
    _.$builder.find('#btn-load-form').trigger('click');
  }

  render(options={}) {
    this.viewer = new ViewerLayoutController(this);
    const formData = options.formData || this.initials.formData || [];
    const submitData = options.submitData || {};
    const onSubmit = options.onSubmit || undefined;
    this.viewer.renderForm(formData, { initialValue: this.initialValue });

    const form = this.viewer.form;
    form.on('submit', { viewer: this.viewer, fb: this }, (e) => {
      const { viewer, fb } = e.data;
      const formData = viewer.getFormData();

      console.log({ formData: formData });
      if (fb.onSubmit) {
        fb.onSubmit(formData);
      } else if (submitData) {
        const { url, method, data: inputData, headers } = submitData;
        /* fetch(url, {
          method: method ?? 'POST',
          headers: {
            // 'Content-Type': 'application/json',
            ...headers,
          },
          body: formData,
        }); */
        console.log({
          method: method ?? 'POST',
          url,
          data: { ...inputData, ...formData },
          headers,
        });
      }
    });
  }

  onSubmit() {}

  getJSON() {
    return this.layout.buildArea.toJSON();
  }

  widget() {
    return this;
  }
}

jQuery.fn.formBuilder = function (...args) {
  const _ = this;
  const opt = args[0];
  const moreArgs = Array.prototype.slice.call(args, 1);
  const l = _.length;
  let i;
  let ret;

  for (i = 0; i < l; i++) {
    if (typeof opt === 'object' || typeof opt === 'undefined') {
      _[i].formb = new FormBuilder(_[i], opt, jQuery);
    } else {
      ret = _[i].formb[opt].apply(_[i].formb, moreArgs, jQuery);
    }
    if (typeof ret !== 'undefined') return ret;
  }
  return _;
};
