export const CONTACT_METHODS = Object.freeze({
  email: 'メールのみ（電話不可）',
  phone: '電話のみ（メール返信不可）',
  both: 'メール・電話どちらも可',
  none: '返信不要（こちらから連絡します）'
});

export function contactPermissions(method) {
  return {
    email: method === CONTACT_METHODS.email || method === CONTACT_METHODS.both,
    phone: method === CONTACT_METHODS.phone || method === CONTACT_METHODS.both
  };
}

export function prepareContactData(input) {
  const data = new FormData();
  input.forEach((value, name) => data.append(name, value));
  const method = String(data.get('連絡方法') || '');
  const allowed = contactPermissions(method);
  if (!allowed.email) { data.delete('email'); data.delete('_replyto'); }
  if (!allowed.phone) data.delete('phone');
  data.delete('_autoresponse');
  data.set('電話連絡', allowed.phone ? '可' : '不可');
  data.set('メール返信', allowed.email ? '可' : '不可');
  data.set('留守電', allowed.phone
    ? (data.get('留守電') === '留守電を残してよい' ? '留守電を残してよい' : '留守電を残さない')
    : '電話・留守電ともに不可');
  if (!allowed.email && !allowed.phone) {
    data.set('連絡可能な時間', method === CONTACT_METHODS.none ? '返信不要' : '連絡方法未選択');
    data.delete('連絡時間の補足');
  } else if (!data.get('連絡可能な時間')) {
    data.set('連絡可能な時間', '指定なし（受付時間内）');
  }
  const subjectMethod = Object.values(CONTACT_METHODS).includes(method) ? method : '連絡方法未選択';
  data.set('_subject', '【ルミライズ／' + subjectMethod + '】' + (data.get('topic') || 'お問い合わせ'));
  return data;
}

export function contactEmailBody(data) {
  const value = key => String(data.get(key) || '').trim();
  return [
    '【連絡希望：返信前にご確認ください】',
    '連絡方法：' + (value('連絡方法') || '未選択（電話・留守電は不可）'),
    '電話連絡：' + value('電話連絡'),
    'メール返信：' + value('メール返信'),
    '留守電：' + value('留守電'),
    '連絡可能な時間：' + value('連絡可能な時間'),
    '連絡時間の補足：' + value('連絡時間の補足'),
    '', 'お名前：' + value('name'),
    ...(value('email') ? ['メール：' + value('email')] : []),
    ...(value('phone') ? ['電話番号：' + value('phone')] : []),
    '相談種別：' + value('topic'), '希望言語：' + value('language'),
    '', value('message')
  ].join('\n');
}
