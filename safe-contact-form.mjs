import {contactText as t, localizeContactForm} from './contact-i18n.mjs?v=20261103-audit';
import {CONTACT_METHODS, contactPermissions, prepareContactData, contactEmailBody, missingContactDestination} from './contact-preferences.mjs?v=20261102-contact';
import {submitContact} from './contact-submission.mjs?v=20261103-response-wait';

const form = document.getElementById('contact-form');
const status = document.getElementById('form-status');
if (form && status) {
  form.noValidate = true;
  let sending = false;
  const submit = form.querySelector('[type="submit"]');
  const method = document.getElementById('contact-method');
  const voicemail = document.getElementById('voicemail-permission');
  const time = document.getElementById('contact-time');
  const timeDetails = document.getElementById('contact-time-details');
  const email = document.getElementById('email');
  const phone = document.getElementById('phone');
  const summary = document.getElementById('contact-preferences-summary');
  const fallback = document.getElementById('email-fallback');
  const controls = [...form.querySelectorAll('input:not([type="hidden"]),select,textarea')];
  const message = (text, type) => { status.textContent = text; status.className = 'form-status ' + type; };
  const clearError = field => {
    field.classList.remove('invalid');
    field.removeAttribute('aria-invalid');
    field.removeAttribute('aria-errormessage');
  };
  const updateFallback = () => {
    const data = prepareContactData(new FormData(form));
    fallback.href = 'mailto:info@lumirize.co?subject=' + encodeURIComponent(data.get('_subject')) + '&body=' + encodeURIComponent(contactEmailBody(data));
  };
  const syncPreferences = () => {
    localizeContactForm();
    const allowed = contactPermissions(method.value);
    const canReply = allowed.email || allowed.phone;
    email.disabled = !allowed.email;
    email.required = method.value === CONTACT_METHODS.email;
    phone.disabled = !allowed.phone;
    phone.required = method.value === CONTACT_METHODS.phone;
    voicemail.disabled = !allowed.phone;
    if (!allowed.phone) voicemail.value = '留守電を残さない';
    time.disabled = !canReply;
    timeDetails.disabled = !canReply;
    timeDetails.required = canReply && time.value === '下の補足欄で指定';
    document.getElementById('email-requirement').textContent = email.required ? t('required', '必須 / Required') : allowed.email ? t('either', 'どちらか一方は必須 / At least one contact') : t('notNeeded', '入力不要 / Not needed');
    document.getElementById('phone-requirement').textContent = phone.required ? t('required', '必須 / Required') : allowed.phone ? t('either', 'どちらか一方は必須 / At least one contact') : t('notNeeded', '入力不要 / Not needed');
    document.getElementById('contact-time-requirement').textContent = timeDetails.required ? t('required', '必須 / Required') : t('optional', '任意 / Optional');
    controls.filter(field => field.disabled || !field.required).forEach(clearError);
    if (!method.value) {
      summary.textContent = t('choose', '希望する連絡方法を選んでください。「返信不要」も選べます。');
    } else if (!canReply) {
      summary.textContent = t('noReply', '返信不要として受け付けます。メールアドレス・電話番号の入力は不要です。必要なときに、改めてご連絡ください。');
    } else {
      summary.textContent = [method.selectedOptions[0].textContent, allowed.phone ? voicemail.selectedOptions[0].textContent : '', time.selectedOptions[0].textContent].filter(Boolean).join(' / ');
    }
    updateFallback();
  };
  controls.forEach(field => {
    field.addEventListener('input', () => { clearError(field); updateFallback(); });
    field.addEventListener('change', () => clearError(field));
  });
  form.addEventListener('change', syncPreferences);
  syncPreferences();
  submit.disabled = false;
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (sending) return;
    syncPreferences();
    let firstInvalid;
    controls.filter(field => !field.disabled && field.name !== '_honey').forEach(field => {
      clearError(field);
      const valid = field.checkValidity() && (!field.required || field.type === 'checkbox' || field.value.trim().length > 0);
      if (!valid) {
        field.classList.add('invalid');
        field.setAttribute('aria-invalid', 'true');
        field.setAttribute('aria-errormessage', status.id);
        firstInvalid ||= field;
      }
    });
    if (missingContactDestination(method.value, email.value, phone.value)) {
      const field = method.value === CONTACT_METHODS.phone ? phone : email;
      field.classList.add('invalid');
      field.setAttribute('aria-invalid', 'true');
      field.setAttribute('aria-errormessage', status.id);
      firstInvalid ||= field;
    }
    if (firstInvalid) {
      message(t('error', '連絡方法、必要な連絡先、必須項目、個人情報の取り扱いへの同意をご確認ください。 Please check your contact preferences and required fields.'), 'error');
      firstInvalid.focus({preventScroll: true});
      firstInvalid.scrollIntoView({block:'center', behavior:'auto'});
      return;
    }
    sending = true;
    submit.disabled = true;
    form.setAttribute('aria-busy', 'true');
    message(t('pending', '送信結果を確認しています。確認に最大1分ほどかかる場合があります。同じ内容を重ねて送らず、このままお待ちください。 Sending… Confirmation can take up to a minute. Please wait without sending again.'), 'pending');
    status.dataset.submissionState = 'pending';
    delete status.dataset.submissionReason;
    const data = prepareContactData(new FormData(form));
    const noReply = method.value === CONTACT_METHODS.none;
    try {
      const result = await submitContact(form.dataset.ajaxAction, data);
      status.dataset.submissionState = result.confirmed ? 'accepted' : 'unconfirmed';
      status.dataset.submissionReason = result.reason;
      if (!result.confirmed) {
        message(t('warning', '送信結果を確認できませんでした。受付先に届いている場合があります。重複を避けるため、同じ内容をすぐに再送せず、安全に利用できる連絡方法で受付状況をご確認ください。入力内容は残っています。 Delivery could not be confirmed. It may have arrived; avoid duplicate submissions. Your input is retained.'), 'warning');
        return;
      }
      message(noReply
        ? t('successNone', '返信不要のご希望とともに送信しました。必要なときに、改めてご連絡ください。 Submitted with your no-reply preference.')
        : t('success', '連絡方法・留守電・時間のご希望とともに送信しました。ご希望を確認したうえで、受付時間内に対応します。 Submitted with your contact preferences.'), 'success');
      const chosenLanguage = document.getElementById('language').value;
      form.reset();
      document.getElementById('language').value = chosenLanguage;
      syncPreferences();
    } finally {
      sending = false;
      submit.disabled = false;
      form.removeAttribute('aria-busy');
    }
  });
}
