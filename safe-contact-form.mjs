import {CONTACT_METHODS, contactPermissions, prepareContactData, contactEmailBody} from './contact-preferences.mjs?v=20261001-safe-contact';

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
    const allowed = contactPermissions(method.value);
    const canReply = allowed.email || allowed.phone;
    email.disabled = !allowed.email;
    email.required = allowed.email;
    phone.disabled = !allowed.phone;
    phone.required = allowed.phone;
    voicemail.disabled = !allowed.phone;
    if (!allowed.phone) voicemail.value = '留守電を残さない';
    time.disabled = !canReply;
    timeDetails.disabled = !canReply;
    timeDetails.required = canReply && time.value === '下の補足欄で指定';
    document.getElementById('email-requirement').textContent = allowed.email ? '必須 / Required' : '入力不要 / Not needed';
    document.getElementById('phone-requirement').textContent = allowed.phone ? '必須 / Required' : '入力不要 / Not needed';
    document.getElementById('contact-time-requirement').textContent = timeDetails.required ? '必須 / Required' : '任意 / Optional';
    controls.filter(field => field.disabled || !field.required).forEach(clearError);
    if (!method.value) {
      summary.textContent = '希望する連絡方法を選んでください。「返信不要」も選べます。';
    } else if (!canReply) {
      summary.textContent = '返信不要として受け付けます。メールアドレス・電話番号の入力は不要です。必要なときに、改めてご連絡ください。';
    } else {
      summary.textContent = method.value + '。' + (allowed.phone ? voicemail.value + '。' : '電話・留守電は希望しない旨を伝えます。') + '連絡時間：' + time.value + '。';
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
    if (firstInvalid) {
      message('連絡方法、必要な連絡先、必須項目、個人情報の取り扱いへの同意をご確認ください。 Please check your contact preferences and required fields.', 'error');
      firstInvalid.focus({preventScroll: true});
      firstInvalid.scrollIntoView({block:'center', behavior:'auto'});
      return;
    }
    sending = true;
    submit.disabled = true;
    form.setAttribute('aria-busy', 'true');
    message('送信中です。 Sending…', 'pending');
    const data = prepareContactData(new FormData(form));
    const noReply = method.value === CONTACT_METHODS.none;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 20000);
    try {
      const response = await fetch(form.dataset.ajaxAction, {method:'POST', headers:{Accept:'application/json'}, body:data, signal:controller.signal});
      const result = await response.json();
      if (!response.ok || !(result.success === true || result.success === 'true')) throw new Error('Submission not confirmed');
      message(noReply
        ? '返信不要のご希望とともに送信しました。必要なときに、改めてご連絡ください。 Submitted with your no-reply preference.'
        : '連絡方法・留守電・時間のご希望とともに送信しました。ご希望を確認したうえで、受付時間内に対応します。 Submitted with your contact preferences.', 'success');
      form.reset();
      syncPreferences();
    } catch {
      message('送信の完了を確認できませんでした。入力内容は残っています。下の「メールアプリから相談する」もご利用いただけます。 Submission could not be confirmed; your input is retained.', 'error');
    } finally {
      clearTimeout(timeout);
      sending = false;
      submit.disabled = false;
      form.removeAttribute('aria-busy');
    }
  });
}
