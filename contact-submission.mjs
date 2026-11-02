// An acknowledgement failure does not prove that the recipient did not receive mail.
// Return only a fixed diagnostic code; never retain or log the submitted content.
export async function submitContact(endpoint, data, {
  fetchImpl = fetch,
  timeoutMs = 20000
} = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  let phase = 'request';
  try {
    const response = await fetchImpl(endpoint, {
      method: 'POST', headers: {Accept: 'application/json'}, body: data,
      signal: controller.signal
    });
    if (!response.ok) return {confirmed: false, reason: 'http-response'};
    phase = 'response';
    const result = await response.json();
    if (result?.success === true || result?.success === 'true') {
      return {confirmed: true, reason: 'accepted'};
    }
    return {confirmed: false, reason: 'not-confirmed'};
  } catch {
    return {
      confirmed: false,
      reason: controller.signal.aborted ? 'timeout'
        : phase === 'response' ? 'unreadable-response' : 'network'
    };
  } finally {
    clearTimeout(timeout);
  }
}
