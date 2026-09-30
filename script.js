(() => {
  'use strict';
  const faqItems = [...document.querySelectorAll('.faq-item')];
  faqItems.forEach((item, index) => {
    const button = item.querySelector('.faq-question');
    const answer = item.querySelector('.faq-answer');
    if (!button || !answer) return;
    button.type = 'button';
    button.id = `faq-question-${index + 1}`;
    answer.id = `faq-answer-${index + 1}`;
    button.setAttribute('aria-controls', answer.id);
    button.setAttribute('aria-expanded', 'false');
    answer.setAttribute('aria-labelledby', button.id);
    answer.hidden = true;
    button.addEventListener('click', () => {
      const open = button.getAttribute('aria-expanded') !== 'true';
      item.classList.toggle('active', open);
      button.setAttribute('aria-expanded', String(open));
      answer.hidden = !open;
    });
  });

  const form = document.getElementById('contact-form');
  const status = document.getElementById('form-status');
  const fallback = document.getElementById('email-fallback');
  if (!form || !status) return;
  // Native validation remains available when JavaScript is unavailable.
  form.noValidate = true;
  let sending = false;
  const required = [...form.querySelectorAll('[required]')];
  const submit = form.querySelector('[type="submit"]');
  const message = (text, type) => {
    status.textContent = text;
    status.className = 'form-status ' + type;
  };
  const clearError = field => {
    field.classList.remove('invalid');
    field.removeAttribute('aria-invalid');
    field.removeAttribute('aria-errormessage');
  };
  required.forEach(field => {
    field.addEventListener('input', () => clearError(field));
    field.addEventListener('change', () => clearError(field));
  });
  const safeOptions = document.getElementById('safe-contact');
  const safeMethod = document.getElementById('safe-contact-method');
  const voicemail = document.getElementById('safe-voicemail');
  const syncSafeContact = () => {
    if (!safeMethod || !voicemail) return;
    const noPhone = safeMethod.value === '電話不可・メールで連絡';
    // Keep the control enabled so FormData preserves the instruction.
    const allowVoicemail = [...voicemail.options].find(option => option.value === '残してよい');
    if (allowVoicemail) allowVoicemail.disabled = noPhone;
    if (noPhone) voicemail.value = '残さない';
  };
  safeMethod?.addEventListener('change', syncSafeContact);
  form.addEventListener('reset', () => setTimeout(syncSafeContact, 0));
  const openSafeOptions = () => {
    if (safeOptions && location.hash === '#safe-contact') safeOptions.open = true;
  };
  window.addEventListener('hashchange', openSafeOptions);
  openSafeOptions();
  syncSafeContact();
  const updateFallback = () => {
    const data = new FormData(form);
    const value = key => String(data.get(key) || '').trim();
    const subject = '【株式会社ルミライズ】' + (value('topic') || 'お問い合わせ');
    const body = ['お名前：' + value('name'), 'メール：' + value('email'), '電話：' + value('phone'), '相談種別：' + value('topic'), '希望言語：' + value('language'), '安全な連絡方法：' + value('安全な連絡方法'), '留守番電話：' + value('留守番電話'), '連絡可能な時間帯・注意点：' + value('連絡可能な時間帯・注意点'), '', value('message')].join('\n');
    if (fallback) fallback.href = 'mailto:info@lumirize.co?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
  };
  form.addEventListener('input', updateFallback);
  form.addEventListener('change', updateFallback);
  updateFallback();
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (sending) return;
    let firstInvalid;
    required.forEach(field => {
      clearError(field);
      const valid = field.type === 'checkbox' ? field.checked : field.value.trim().length > 0 && field.checkValidity();
      if (!valid) {
        field.classList.add('invalid');
        field.setAttribute('aria-invalid', 'true');
        field.setAttribute('aria-errormessage', status.id);
        firstInvalid ||= field;
      }
    });
    if (firstInvalid) {
      message('未入力の必須項目、メールアドレスの形式、個人情報の取り扱いへの同意をご確認ください。 Please check the required fields, email address and privacy consent.', 'error');
      firstInvalid.focus({preventScroll: true});
      firstInvalid.scrollIntoView({block: "center", behavior: "auto"});
      return;
    }
    sending = true;
    submit.disabled = true;
    form.setAttribute('aria-busy', 'true');
    message('送信中です。しばらくお待ちください。 Sending…', 'pending');
    updateFallback();
    const data = new FormData(form);
    data.set('_subject', '【株式会社ルミライズ】' + data.get('topic'));
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 20000);
    try {
      const response = await fetch(form.dataset.ajaxAction, {method: 'POST', headers: {Accept: 'application/json'}, body: data, signal: controller.signal});
      const result = await response.json();
      if (!response.ok || !(result.success === true || result.success === 'true')) throw new Error('Submission not confirmed');
      message('送信を受け付けました。 Your message has been submitted. 受付時間内に順次ご返信します。時間外のご相談は次の営業日以降に確認します。内容や混雑状況によりお時間をいただく場合があります。 We reply during reception hours; messages received outside these hours are reviewed from the next business day. Response times vary.返信が届かない場合は、迷惑メールフォルダをご確認のうえ、お電話ください。', 'success');
      form.reset();
      updateFallback();
    } catch {
      message('送信の完了を確認できませんでした。入力内容は残っています。 Submission could not be confirmed. Please email or call us. 下の「メールアプリから相談する」またはお電話をご利用ください。', 'error');
    } finally {
      clearTimeout(timeout);
      sending = false;
      submit.disabled = false;
      form.removeAttribute('aria-busy');
    }
  });
})();
